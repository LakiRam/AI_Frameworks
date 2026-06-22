"""Inventory & Replenishment agent — sizes reorders against forecast + cover days."""
from ._base import make_agent_node
from ..tools.inventory_db import get_inventory, suggest_reorder

SYSTEM_PROMPT = """You are the INVENTORY & REPLENISHMENT agent.
You receive forecasts from the demand agent. For each store/SKU:
  1. Check current on-hand and reorder point.
  2. Compute a reorder quantity for the target cover period.
  3. Flag any HIGH stockout risk SKUs.
Return a short, actionable reorder plan (store, SKU, qty, urgency)."""

inventory_node = make_agent_node(
    agent_name="inventory_agent",
    system_prompt=SYSTEM_PROMPT,
    tools=[get_inventory, suggest_reorder],
    risk_default="MEDIUM",
)
