"""SOA Retail — LangGraph supervisor orchestrator.

Flow:
    START -> supervisor -> (one of 7 specialists) -> supervisor -> ...
            -> approval (HITL, if any finding is high-risk) -> finalizer -> END

Exports:
    `graph`        : compiled StateGraph (used by `langgraph dev` via langgraph.json)
    `build_graph()`: factory to build a graph with a chosen checkpointer.
"""
from __future__ import annotations

import json
import re
from typing import Literal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from .state import RetailState
from .llm import get_llm
from .agents import AGENT_NODES
from .config import APPROVAL_REQUIRED


WORKERS = list(AGENT_NODES.keys())  # 7 specialist names


SUPERVISOR_PROMPT = f"""You are the SOA Retail SUPERVISOR.
You coordinate a team of specialist agents:
{json.dumps(WORKERS, indent=2)}

Your job: read the user's operational request + the findings so far, then pick
the ONE specialist whose tools are best suited for the NEXT step. Reply FINISH
when the request has been adequately answered.

ROUTING GUIDE (pick by INTENT, not by a fixed order):
  - "forecast demand", "will we run out", "spike from weather/event"
        -> forecast_agent       (needs an explicit SKU or city)
  - "stock levels", "overstock", "slow-moving SKUs", "what's not selling"
        -> inventory_agent      (good first step when SKUs are unspecified)
  - "price change", "competitor pricing", "margin"
        -> pricing_agent
  - "promotion", "discount", "loyalty offer", "campaign"
        -> promotion_agent      (usually AFTER inventory + customer_insight)
  - "loyalty customers", "customer segment", "audience"
        -> customer_insight_agent
  - "delivery", "shipment", "supplier", "logistics", "ETA"
        -> supply_chain_agent
  - "fraud", "unusual transactions", "anomaly", "suspicious"
        -> anomaly_agent

EXAMPLES:
  Request: "Design a weekend promotion for slow-moving SKUs at S002.
            Target: loyalty customers."
  Best chain: inventory_agent -> customer_insight_agent -> promotion_agent -> FINISH

  Request: "Will store S001 run out of SKU123 this weekend?"
  Best chain: forecast_agent -> inventory_agent -> FINISH

Rules:
  - Do NOT call the same agent twice unless its first run was blocked by
    missing data that a later finding now supplies.
  - Do NOT route to forecast_agent unless you know (or a prior finding gives)
    a concrete store + SKU (or city).
  - When findings already answer the request, return FINISH.

Respond with ONLY a compact JSON object:
  {{"next": "<agent_name_or_FINISH>", "reason": "<one short sentence>"}}

Available values for "next": {WORKERS + ["FINISH"]}
"""


def _extract_json(text: str) -> dict:
    """Best-effort JSON extraction from an LLM response."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return {"next": "FINISH", "reason": "no json"}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"next": "FINISH", "reason": "bad json"}


def _user_request_text(state: RetailState) -> str:
    """Resolve the user's original request text.

    Studio's chat UI delivers input as `messages=[HumanMessage(...)]` rather
    than `{"request": "..."}`. Messages may arrive as either LangChain
    `HumanMessage` objects (type == "human") OR raw dicts
    ({"role": "user", "content": "..."}) depending on whether the
    `add_messages` reducer has run yet, so we handle both shapes.
    """
    req = (state.get("request") or "").strip()
    if req:
        return req

    def _is_human(m) -> bool:
        # LangChain message object
        if getattr(m, "type", None) == "human":
            return True
        # Raw dict (Studio JSON input or REST API)
        if isinstance(m, dict):
            if m.get("type") == "human":
                return True
            if m.get("role") in ("user", "human"):
                return True
        return False

    def _content_of(m) -> str:
        c = m.get("content") if isinstance(m, dict) else getattr(m, "content", "")
        if isinstance(c, str):
            return c
        # Some clients wrap content as a list of parts: [{"type":"text","text":"..."}]
        if isinstance(c, list):
            parts = []
            for p in c:
                if isinstance(p, dict) and "text" in p:
                    parts.append(p["text"])
                elif isinstance(p, str):
                    parts.append(p)
            return "\n".join(parts)
        return str(c) if c else ""

    for m in state.get("messages", []) or []:
        if _is_human(m):
            text = _content_of(m).strip()
            if text:
                return text
    return ""


def supervisor_node(state: RetailState) -> dict:
    """LLM-based router. Picks the next worker or FINISH."""
    findings_brief = "\n".join(
        f"- [{f.get('agent')}] risk={f.get('risk')} :: {_summary_text(f)[:200]}"
        for f in state.get("findings", [])
    )
    history_brief = findings_brief or "(no findings yet)"

    request_text = _user_request_text(state)

    # --- DIAGNOSTIC (remove once routing is stable) ---
    msgs = state.get("messages", []) or []
    print(
        f"[supervisor] request_text={request_text!r} "
        f"| state.request={state.get('request')!r} "
        f"| #messages={len(msgs)} "
        f"| first_msg_type={type(msgs[0]).__name__ if msgs else None} "
        f"| first_msg_role={(msgs[0].get('role') if isinstance(msgs[0], dict) else getattr(msgs[0], 'type', None)) if msgs else None}",
        flush=True,
    )
    # --------------------------------------------------

    user = (
        f"User request:\n{request_text}\n\n"
        f"Context: {state.get('context', {})}\n\n"
        f"Findings so far:\n{history_brief}\n\n"
        "Which agent should act next? Reply with JSON only."
    )
    resp = get_llm().invoke([
        SystemMessage(content=SUPERVISOR_PROMPT),
        HumanMessage(content=user),
    ])
    decision = _extract_json(resp.content if hasattr(resp, "content") else str(resp))
    nxt = decision.get("next", "FINISH")
    if nxt not in WORKERS + ["FINISH"]:
        nxt = "FINISH"

    return {
        "next": nxt,
        # Persist the resolved request so downstream specialists don't have to
        # re-derive it from `messages` themselves.
        "request": request_text,
        "messages": [AIMessage(content=f"[supervisor] -> {nxt} ({decision.get('reason','')})",
                               name="supervisor")],
    }


def approval_node(state: RetailState) -> dict:
    """Human-in-the-loop gate.

    By default we *mark* approval as required when any finding has
    `requires_approval=True`. The actual pause/resume is handled by
    `interrupt_before=["approval"]` when the graph is compiled with a
    checkpointer (e.g. via `langgraph dev` or our FastAPI runner).
    """
    needs = any(f.get("requires_approval") for f in state.get("findings", []))
    if not APPROVAL_REQUIRED:
        needs = False
    return {
        "approval_required": needs,
        # If APPROVAL_REQUIRED is off, auto-approve so finalizer runs straight away
        "approved": None if needs else True,
    }


def _summary_text(f: dict) -> str:
    """Coerce a finding's `summary` to a plain string (some providers return lists)."""
    s = f.get("summary", "")
    if isinstance(s, str):
        return s.strip()
    if isinstance(s, list):
        parts: list[str] = []
        for p in s:
            if isinstance(p, str):
                parts.append(p)
            elif isinstance(p, dict) and isinstance(p.get("text"), str):
                parts.append(p["text"])
        return "\n".join(parts).strip()
    return str(s).strip()


def finalizer_node(state: RetailState) -> dict:
    """Build the consolidated executive plan from all agent findings."""
    bullets = []
    for f in state.get("findings", []):
        bullets.append(
            f"- **{f.get('agent')}** (risk={f.get('risk')}): {_summary_text(f)}"
        )
    plan = (
        f"# SOA Retail — Action Plan\n\n"
        f"**Request:** {state.get('request','')}\n\n"
        f"**Approved:** {state.get('approved')}\n\n"
        f"## Findings\n" + ("\n".join(bullets) if bullets else "(no findings)")
    )
    return {
        "plan": plan,
        "messages": [AIMessage(content=plan, name="finalizer")],
    }


def _route_from_supervisor(state: RetailState) -> str:
    nxt = state.get("next", "FINISH")
    return "approval" if nxt == "FINISH" else nxt


def _route_from_approval(state: RetailState) -> Literal["finalizer", "__end__"]:
    # If approval is required and not yet granted, end so the runner can pause/resume.
    if state.get("approval_required") and state.get("approved") is None:
        return "finalizer"  # finalizer will still produce a plan marked "pending approval"
    return "finalizer"


def build_graph(checkpointer=None, interrupt_for_approval: bool = True):
    """Construct the StateGraph.

    Args:
        checkpointer: optional checkpointer (MemorySaver / SqliteSaver). When
            running under `langgraph dev`, the platform supplies one for us.
        interrupt_for_approval: when True and `APPROVAL_REQUIRED`, the graph
            pauses *before* the approval node so a human can intervene.
    """
    g = StateGraph(RetailState)
    g.add_node("supervisor", supervisor_node)
    for name, node in AGENT_NODES.items():
        g.add_node(name, node)
    g.add_node("approval", approval_node)
    g.add_node("finalizer", finalizer_node)

    g.add_edge(START, "supervisor")
    g.add_conditional_edges(
        "supervisor",
        _route_from_supervisor,
        {**{w: w for w in WORKERS}, "approval": "approval"},
    )
    for w in WORKERS:
        g.add_edge(w, "supervisor")

    g.add_conditional_edges(
        "approval", _route_from_approval, {"finalizer": "finalizer"}
    )
    g.add_edge("finalizer", END)

    compile_kwargs: dict = {}
    if checkpointer is not None:
        compile_kwargs["checkpointer"] = checkpointer
    if interrupt_for_approval and APPROVAL_REQUIRED:
        compile_kwargs["interrupt_before"] = ["approval"]

    return g.compile(**compile_kwargs)


# --- Module-level compiled graph (referenced by langgraph.json) -------------
# LangGraph Platform / `langgraph dev` injects its own checkpointer when it
# loads this symbol, so we compile without one here.
graph = build_graph(checkpointer=None, interrupt_for_approval=False)


__all__ = ["graph", "build_graph"]
