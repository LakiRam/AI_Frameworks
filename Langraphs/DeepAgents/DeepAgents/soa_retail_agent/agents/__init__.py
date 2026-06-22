"""Specialist agents for SOA Retail.

Each agent is a small `create_react_agent` instance bound to the tools it needs.
They share the same `RetailState` and append a structured `AgentFinding`
when invoked by the supervisor.
"""
from .forecast_agent import forecast_node
from .inventory_agent import inventory_node
from .pricing_agent import pricing_node
from .promotion_agent import promotion_node
from .customer_insight_agent import customer_insight_node
from .supply_chain_agent import supply_chain_node
from .anomaly_agent import anomaly_node

AGENT_NODES = {
    "forecast_agent": forecast_node,
    "inventory_agent": inventory_node,
    "pricing_agent": pricing_node,
    "promotion_agent": promotion_node,
    "customer_insight_agent": customer_insight_node,
    "supply_chain_agent": supply_chain_node,
    "anomaly_agent": anomaly_node,
}

__all__ = ["AGENT_NODES"]
