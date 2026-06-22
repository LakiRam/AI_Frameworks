"""Shared helpers for building specialist agent nodes.

Each specialist is a small ReAct agent (LLM + tools). We wrap it in a node
function that:
  1. Invokes the ReAct agent with the running message history + context.
  2. Extracts the final assistant message.
  3. Appends a structured `AgentFinding` to the shared state.
"""
from __future__ import annotations

from typing import Callable

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

from ..llm import get_llm
from ..state import RetailState, AgentFinding


def _coerce_content_to_text(content) -> str:
    """Normalize LangChain message content to a plain string.

    Some providers return `AIMessage.content` as a list of content blocks
    (e.g. ``[{"type": "text", "text": "..."}]``) instead of a string.
    Downstream code (`.strip()`, slicing for previews) expects a string.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for p in content:
            if isinstance(p, str):
                parts.append(p)
            elif isinstance(p, dict):
                # Common shapes: {"type": "text", "text": "..."} or {"text": "..."}
                if isinstance(p.get("text"), str):
                    parts.append(p["text"])
                elif isinstance(p.get("content"), str):
                    parts.append(p["content"])
        return "\n".join(parts)
    return "" if content is None else str(content)


def make_agent_node(
    agent_name: str,
    system_prompt: str,
    tools: list,
    risk_default: str = "LOW",
    requires_approval: bool = False,
) -> Callable[[RetailState], dict]:
    """Build a node function for a specialist agent."""

    react_agent = create_react_agent(
        model=get_llm(),
        tools=tools,
        prompt=system_prompt,
    )

    def node(state: RetailState) -> dict:
        request = (state.get("request") or "").strip()
        if not request:
            # Fallback: take the first HumanMessage (Studio chat puts input
            # into `messages` rather than `request`).
            for m in state.get("messages", []) or []:
                if getattr(m, "type", None) == "human":
                    c = getattr(m, "content", "")
                    if isinstance(c, str) and c.strip():
                        request = c.strip()
                        break
        context = state.get("context", {})
        prior = "\n".join(
            f"- [{f.get('agent')}] {f.get('summary','')}" for f in state.get("findings", [])
        )
        user_block = (
            f"Operational request:\n{request}\n\n"
            f"Context: {context}\n\n"
            f"Findings from earlier agents:\n{prior or '(none)'}"
        )

        result = react_agent.invoke({"messages": [HumanMessage(content=user_block)]})
        final_msg = result["messages"][-1]
        raw_content = final_msg.content if isinstance(final_msg, AIMessage) else str(final_msg)
        summary = _coerce_content_to_text(raw_content)

        # Collect tool call actions executed by the ReAct loop
        actions: list[dict] = []
        for m in result["messages"]:
            if hasattr(m, "tool_calls") and m.tool_calls:
                for tc in m.tool_calls:
                    actions.append({"tool": tc.get("name"), "args": tc.get("args", {})})

        finding: AgentFinding = {
            "agent": agent_name,
            "summary": summary,
            "actions": actions,
            "risk": risk_default,
            "requires_approval": requires_approval,
        }
        return {
            "messages": [AIMessage(content=f"[{agent_name}] {summary}", name=agent_name)],
            "findings": [finding],
        }

    node.__name__ = f"{agent_name}_node"
    return node
