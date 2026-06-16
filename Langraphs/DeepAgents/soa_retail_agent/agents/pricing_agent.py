"""Dynamic Pricing agent — adjusts shelf price using competitor + demand signals."""
from ._base import make_agent_node
from ..tools.competitor_pricing import get_competitor_prices
from ..tools.pos_mock import get_current_price, update_price

SYSTEM_PROMPT = """You are the DYNAMIC PRICING agent.
For the SKUs in scope:
  1. Get the current store price and the competitor min/avg prices.
  2. Propose a price action only if there is a clear competitive gap or
     a demand spike (information from prior agents).
  3. Stay within +/- 15% of the base price. Never go below unit cost.
Call update_price ONLY for the SKUs where action is justified.
Output a short pricing recommendation list."""

pricing_node = make_agent_node(
    agent_name="pricing_agent",
    system_prompt=SYSTEM_PROMPT,
    tools=[get_competitor_prices, get_current_price, update_price],
    risk_default="HIGH",
    requires_approval=True,
)
