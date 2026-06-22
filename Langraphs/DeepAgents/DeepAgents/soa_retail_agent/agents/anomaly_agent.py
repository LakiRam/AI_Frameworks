"""Anomaly & Shrinkage agent — scans POS for fraud / shrinkage events."""
from ._base import make_agent_node
from ..tools.anomaly_mock import scan_pos_anomalies

SYSTEM_PROMPT = """You are the ANOMALY & SHRINKAGE agent.
For each store in scope, scan recent POS activity for fraud or shrinkage.
Report:
  - Number of anomalies and their risk scores.
  - The single most urgent event, if any.
Recommend whether Loss Prevention should be paged."""

anomaly_node = make_agent_node(
    agent_name="anomaly_agent",
    system_prompt=SYSTEM_PROMPT,
    tools=[scan_pos_anomalies],
    risk_default="MEDIUM",
)
