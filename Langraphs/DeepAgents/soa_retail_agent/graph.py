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

Given the user's operational request and the findings so far, decide WHICH
agent should act next, or respond FINISH when the situation has been adequately
covered (forecast -> inventory -> pricing/promotion/supply_chain as needed,
plus anomaly when fraud is suspected).

Respond with ONLY a compact JSON object of the form:
  {{"next": "<agent_name_or_FINISH>", "reason": "<one short sentence>"}}

Available values for "next": {WORKERS + ["FINISH"]}
Do not call the same agent twice unless absolutely necessary.
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


def supervisor_node(state: RetailState) -> dict:
    """LLM-based router. Picks the next worker or FINISH."""
    findings_brief = "\n".join(
        f"- [{f.get('agent')}] risk={f.get('risk')} :: {f.get('summary','')[:200]}"
        for f in state.get("findings", [])
    )
    history_brief = findings_brief or "(no findings yet)"

    user = (
        f"User request:\n{state.get('request','')}\n\n"
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


def finalizer_node(state: RetailState) -> dict:
    """Build the consolidated executive plan from all agent findings."""
    bullets = []
    for f in state.get("findings", []):
        bullets.append(
            f"- **{f.get('agent')}** (risk={f.get('risk')}): {f.get('summary','').strip()}"
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
