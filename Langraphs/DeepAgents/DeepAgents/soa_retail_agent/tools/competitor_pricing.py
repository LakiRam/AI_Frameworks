"""Competitor pricing intelligence (mock scraper)."""
from __future__ import annotations

import pandas as pd
from langchain_core.tools import tool

from ..config import DATA_DIR


@tool
def get_competitor_prices(sku: str, store_id: str | None = None) -> dict:
    """Look up the most recent competitor prices for a SKU (optionally store-local)."""
    df = pd.read_csv(DATA_DIR / "competitor_prices.csv")
    df = df[df["sku_match"] == sku]
    if store_id:
        df = df[df["store_id"] == store_id]
    if df.empty:
        return {"sku": sku, "store_id": store_id, "rows": [], "note": "no observations"}
    return {
        "sku": sku,
        "store_id": store_id,
        "min_price": float(df["price"].min()),
        "avg_price": round(float(df["price"].mean()), 2),
        "rows": df.to_dict(orient="records"),
    }
