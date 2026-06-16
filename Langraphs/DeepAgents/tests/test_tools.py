"""Unit tests for the mock tool layer.

These do NOT require Ollama running — they just exercise the deterministic
mocks against the bundled CSV fixtures.
"""
from __future__ import annotations

import pytest

from soa_retail_agent.tools import ALL_TOOLS
from soa_retail_agent.tools.sales_db import recent_sales, forecast_baseline
from soa_retail_agent.tools.weather import get_weather_forecast
from soa_retail_agent.tools.inventory_db import get_inventory, suggest_reorder
from soa_retail_agent.tools.competitor_pricing import get_competitor_prices
from soa_retail_agent.tools.erp_mock import create_purchase_order
from soa_retail_agent.tools.pos_mock import get_current_price, update_price
from soa_retail_agent.tools.crm_mock import customer_segments, send_promotion
from soa_retail_agent.tools.logistics_mock import (
    check_shipment_status, expedite_shipment,
)
from soa_retail_agent.tools.anomaly_mock import scan_pos_anomalies


def test_all_tools_aggregated():
    names = {t.name for t in ALL_TOOLS}
    expected = {
        "recent_sales", "forecast_baseline", "get_weather_forecast",
        "get_inventory", "suggest_reorder", "get_competitor_prices",
        "create_purchase_order", "update_price", "get_current_price",
        "send_promotion", "customer_segments",
        "check_shipment_status", "expedite_shipment", "scan_pos_anomalies",
    }
    assert expected.issubset(names), f"missing: {expected - names}"


def test_recent_sales_returns_rows():
    out = recent_sales.invoke({"store_id": "S001", "sku": "SKU001", "days": 7})
    assert "rows" in out and len(out["rows"]) >= 1
    assert "avg_daily_units" in out


def test_forecast_baseline_uses_multiplier():
    base = forecast_baseline.invoke(
        {"store_id": "S001", "sku": "SKU001", "horizon_days": 7, "demand_multiplier": 1.0}
    )
    spike = forecast_baseline.invoke(
        {"store_id": "S001", "sku": "SKU001", "horizon_days": 7, "demand_multiplier": 2.0}
    )
    assert spike["forecast_units_per_day"] >= base["forecast_units_per_day"]


def test_weather_mumbai_heatwave():
    out = get_weather_forecast.invoke({"city": "Mumbai", "days_ahead": 3})
    assert out["anomaly"] is True


def test_inventory_lookup():
    out = get_inventory.invoke({"store_id": "S001"})
    assert "rows" in out and len(out["rows"]) >= 1


def test_suggest_reorder_flags_risk():
    out = suggest_reorder.invoke(
        {"store_id": "S001", "sku": "SKU001",
         "forecast_units_per_day": 999, "cover_days": 14}
    )
    assert out["stockout_risk"] in {"HIGH", "LOW"}
    assert out["recommended_reorder_qty"] >= 0


def test_competitor_prices():
    out = get_competitor_prices.invoke({"sku": "SKU001"})
    assert "rows" in out


def test_erp_create_purchase_order():
    out = create_purchase_order.invoke(
        {"store_id": "S001", "sku": "SKU001", "quantity": 50,
         "supplier_id": "SUP001", "unit_cost": 20.0}
    )
    assert out["status"] == "SUBMITTED"
    assert out["po_number"].startswith("PO-")


def test_pos_price_override_roundtrip():
    p1 = get_current_price.invoke({"store_id": "S001", "sku": "SKU001"})
    assert "price" in p1
    update_price.invoke(
        {"store_id": "S001", "sku": "SKU001",
         "new_price": 99.0, "valid_days": 3, "reason": "test"}
    )
    p2 = get_current_price.invoke({"store_id": "S001", "sku": "SKU001"})
    assert p2["price"] == 99.0


def test_crm_segments_and_promo():
    seg = customer_segments.invoke({"city": "Mumbai", "min_loyalty_tier": "Silver"})
    assert "count" in seg
    promo = send_promotion.invoke({
        "campaign_name": "Heatwave Cooler", "audience_city": "Mumbai",
        "audience_min_tier": "Silver", "offer": "15% off",
    })
    assert promo["status"] == "DISPATCHED"


def test_logistics_status_and_expedite():
    status = check_shipment_status.invoke({"po_number": "PO-TEST123"})
    assert "status" in status
    exp = expedite_shipment.invoke({"po_number": "PO-TEST123", "reason": "stockout risk"})
    assert exp["status"] == "EXPEDITED"


def test_anomaly_scan_shape():
    out = scan_pos_anomalies.invoke({"store_id": "S001", "lookback_hours": 24})
    assert "events" in out and "anomalies_found" in out
