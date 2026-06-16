"""Sales history + simple baseline forecast (mock data warehouse)."""
from __future__ import annotations

from typing import Optional
import pandas as pd
from langchain_core.tools import tool

from ..config import DATA_DIR


def _load_sales() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "sales.csv", parse_dates=["date"])
    return df


@tool
def recent_sales(store_id: str, sku: str, days: int = 7) -> dict:
    """Return the most recent N days of sales for a store/SKU.

    Args:
        store_id: e.g. "S001"
        sku: e.g. "SKU001"
        days: how many days to look back (default 7)
    """
    df = _load_sales()
    mask = (df["store_id"] == store_id) & (df["sku"] == sku)
    df = df.loc[mask].sort_values("date").tail(days)
    if df.empty:
        return {"store_id": store_id, "sku": sku, "rows": [], "note": "no sales data"}
    return {
        "store_id": store_id,
        "sku": sku,
        "rows": [
            {"date": d.strftime("%Y-%m-%d"), "units": int(u), "revenue": float(r)}
            for d, u, r in zip(df["date"], df["units_sold"], df["revenue"])
        ],
        "avg_daily_units": float(df["units_sold"].mean()),
        "trend_pct": float(
            (df["units_sold"].iloc[-1] - df["units_sold"].iloc[0])
            / max(df["units_sold"].iloc[0], 1)
            * 100
        ),
    }


@tool
def forecast_baseline(
    store_id: str, sku: str, horizon_days: int = 7, demand_multiplier: float = 1.0
) -> dict:
    """Produce a naive baseline demand forecast.

    Uses last-7-day moving average × optional demand multiplier
    (e.g. 2.4 for a heatwave spike).

    Args:
        store_id: store identifier
        sku: SKU identifier
        horizon_days: number of forward days to forecast
        demand_multiplier: external demand shock factor (1.0 = normal)
    """
    history = recent_sales.invoke({"store_id": store_id, "sku": sku, "days": 7})
    if not history.get("rows"):
        return {"error": "no history", "store_id": store_id, "sku": sku}

    baseline_per_day = history["avg_daily_units"] * demand_multiplier
    return {
        "store_id": store_id,
        "sku": sku,
        "horizon_days": horizon_days,
        "demand_multiplier": demand_multiplier,
        "forecast_units_per_day": round(baseline_per_day, 1),
        "forecast_total_units": int(round(baseline_per_day * horizon_days)),
    }
