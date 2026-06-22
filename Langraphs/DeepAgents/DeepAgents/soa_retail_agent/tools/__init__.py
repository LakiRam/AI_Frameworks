"""Mock tools that simulate retail systems (POS, ERP, WMS, CRM, etc.).

In production, replace these with real adapters (SAP REST, Salesforce CDP, etc.).
All tools are decorated with `@tool` so any agent can bind them to an LLM.
"""
from __future__ import annotations

from .sales_db import recent_sales, forecast_baseline
from .weather import get_weather_forecast
from .inventory_db import get_inventory, suggest_reorder
from .competitor_pricing import get_competitor_prices
from .erp_mock import create_purchase_order
from .pos_mock import update_price, get_current_price
from .crm_mock import send_promotion, customer_segments
from .logistics_mock import check_shipment_status, expedite_shipment
from .anomaly_mock import scan_pos_anomalies

ALL_TOOLS = [
    recent_sales,
    forecast_baseline,
    get_weather_forecast,
    get_inventory,
    suggest_reorder,
    get_competitor_prices,
    create_purchase_order,
    update_price,
    get_current_price,
    send_promotion,
    customer_segments,
    check_shipment_status,
    expedite_shipment,
    scan_pos_anomalies,
]

__all__ = ["ALL_TOOLS"]
