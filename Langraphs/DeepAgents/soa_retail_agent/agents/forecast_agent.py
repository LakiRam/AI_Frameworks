"""Forecast agent — predicts near-term demand using sales + weather signals."""
from ._base import make_agent_node
from ..tools.sales_db import recent_sales, forecast_baseline
from ..tools.weather import get_weather_forecast

SYSTEM_PROMPT = """You are the DEMAND FORECAST agent for a retail chain.
Given a store and SKU (or a city), you must:
  1. Pull the last 7 days of sales for the relevant SKU(s).
  2. Check weather forecast for the city (it may amplify demand for cold drinks, ice cream, etc.).
  3. Produce a short-term demand forecast and flag whether demand is normal, elevated, or critical.

If the request does NOT yet specify a concrete SKU (or city for weather),
DO NOT ask the user — instead, respond with exactly:
  "NO_SKU_PROVIDED: forecast requires a specific SKU; suggest routing to
   inventory_agent first to identify candidate SKUs."

Otherwise, be terse and end with a one-sentence summary of the forecast and risk level."""

forecast_node = make_agent_node(
    agent_name="forecast_agent",
    system_prompt=SYSTEM_PROMPT,
    tools=[recent_sales, forecast_baseline, get_weather_forecast],
    risk_default="LOW",
)
