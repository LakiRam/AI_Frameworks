"""Smoke test that the LangGraph builds and exposes the right symbol.

This does NOT invoke any LLM (would require Ollama). It only verifies the
compiled graph object is importable and well-formed.
"""
from __future__ import annotations

from soa_retail_agent.graph import graph, build_graph
from soa_retail_agent.agents import AGENT_NODES


def test_graph_symbol_exists():
    assert graph is not None
    # CompiledGraph has invoke / stream / get_graph
    assert hasattr(graph, "invoke")
    assert hasattr(graph, "stream")


def test_all_specialists_registered():
    expected = {
        "forecast_agent", "inventory_agent", "pricing_agent",
        "promotion_agent", "customer_insight_agent",
        "supply_chain_agent", "anomaly_agent",
    }
    assert expected == set(AGENT_NODES.keys())


def test_build_graph_with_memory_checkpointer():
    from langgraph.checkpoint.memory import MemorySaver
    g = build_graph(checkpointer=MemorySaver(), interrupt_for_approval=False)
    nodes = g.get_graph().nodes
    assert "supervisor" in nodes
    assert "finalizer" in nodes
    assert "approval" in nodes
