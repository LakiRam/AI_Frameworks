"""Inventory / WMS read + replenishment helpers."""
from __future__ import annotations

import pandas as pd
from langchain_core.tools import tool

from ..config import DATA_DIR


def _load_inventory() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "inventory.csv")


@tool
def get_inventory(store_id: str, sku: str | None = None) -> dict:
    """Read current on-hand inventory for a store (optionally filtered to one SKU)."""
    df = _load_inventory()
    df = df[df["store_id"] == store_id]
    if sku:
        df = df[df["sku"] == sku]
    if df.empty:
        return {"store_id": store_id, "rows": [], "note": "no inventory record"}
    return {
        "store_id": store_id,
        "rows": df.to_dict(orient="records"),
    }


@tool
def suggest_reorder(
    store_id: str, sku: str, forecast_units_per_day: float, cover_days: int = 14
) -> dict:
    """Compute a recommended reorder quantity for a SKU.

    Formula:  qty = (forecast_per_day * cover_days) + safety_stock - on_hand

    Args:
        store_id: store identifier
        sku: SKU identifier
        forecast_units_per_day: from forecast_baseline()
        cover_days: target days of cover after delivery
    """
    df = _load_inventory()
    row = df[(df["store_id"] == store_id) & (df["sku"] == sku)]
    if row.empty:
        return {"error": "no inventory record", "store_id": store_id, "sku": sku}

    r = row.iloc[0]
    target = forecast_units_per_day * cover_days + r["safety_stock"]
    reorder_qty = max(0, int(round(target - r["on_hand"])))
    return {
        "store_id": store_id,
        "sku": sku,
        "on_hand": int(r["on_hand"]),
        "safety_stock": int(r["safety_stock"]),
        "lead_time_days": int(r["lead_time_days"]),
        "supplier_id": r["supplier_id"],
        "recommended_reorder_qty": reorder_qty,
        "stockout_risk": "HIGH" if r["on_hand"] < r["reorder_point"] else "LOW",
    }
