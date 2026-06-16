"""Shared graph state used by every node in the SOA Retail multi-agent workflow."""
from __future__ import annotations

from typing import Annotated, Literal, TypedDict
from operator import add

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


# Names of available specialist agents (used by the supervisor)
AgentName = Literal[
    "forecast_agent",
    "inventory_agent",
    "pricing_agent",
    "promotion_agent",
    "customer_insight_agent",
    "supply_chain_agent",
    "anomaly_agent",
    "FINISH",
]


class AgentFinding(TypedDict, total=False):
    """A structured finding emitted by a specialist agent."""
    agent: str
    summary: str
    actions: list[dict]      # proposed or executed tool calls
    risk: str                # LOW | MEDIUM | HIGH
    requires_approval: bool


class RetailState(TypedDict, total=False):
    """Shared mutable state passed between all nodes in the graph."""

    # Free-form user request
    request: str
    # Optional structured context, e.g. {"store_id": "S001", "city": "Mumbai"}
    context: dict

    # Conversation transcript across agents (LangChain messages)
    messages: Annotated[list[AnyMessage], add_messages]

    # Per-agent structured findings (appended by reducer)
    findings: Annotated[list[AgentFinding], add]

    # Supervisor's chosen next worker (or "FINISH")
    next: AgentName

    # Final consolidated plan from the supervisor
    plan: str

    # HITL approval status
    approval_required: bool
    approved: bool | None
