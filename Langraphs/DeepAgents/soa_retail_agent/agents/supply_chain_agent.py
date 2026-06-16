"""Supply Chain agent — creates POs and manages logistics escalations."""
from ._base import make_agent_node
from ..tools.erp_mock import create_purchase_order
from ..tools.logistics_mock import check_shipment_status, expedite_shipment

SYSTEM_PROMPT = """You are the SUPPLY CHAIN agent.
You receive a reorder plan from the Inventory agent. Your job:
  1. Create purchase orders via the ERP for each line item.
  2. Check status of existing shipments mentioned in the request.
  3. If a HIGH urgency reorder has a long lead time, expedite via 3PL.
Return a concise list of POs created and any expedite actions taken."""

supply_chain_node = make_agent_node(
    agent_name="supply_chain_agent",
    system_prompt=SYSTEM_PROMPT,
    tools=[create_purchase_order, check_shipment_status, expedite_shipment],
    risk_default="HIGH",
    requires_approval=True,
)
