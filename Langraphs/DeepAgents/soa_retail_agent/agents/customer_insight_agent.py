"""Customer Insight agent — surfaces segment-level analytics."""
from ._base import make_agent_node
from ..tools.crm_mock import customer_segments

SYSTEM_PROMPT = """You are the CUSTOMER INSIGHT agent.
Provide a short analytical view of the loyalty base relevant to the request:
  - Size of audience by city / tier.
  - Notable churn risk or LTV concentration.
Do not dispatch any campaigns; that is the Promotion agent's job."""

customer_insight_node = make_agent_node(
    agent_name="customer_insight_agent",
    system_prompt=SYSTEM_PROMPT,
    tools=[customer_segments],
    risk_default="LOW",
)
