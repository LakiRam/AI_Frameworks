"""POS / Pricing engine mock — represents in-store price master updates."""
from __future__ import annotations

from datetime import datetime
import pandas as pd
from langchain_core.tools import tool

from ..config import DATA_DIR

# Track price overrides in memory
_PRICE_OVERRIDES: dict[tuple[str, str], dict] = {}


@tool
def get_current_price(store_id: str, sku: str) -> dict:
    """Return the active selling price for a store/SKU.

    Considers any price override pushed earlier in this session.
    """
    key = (store_id, sku)
    if key in _PRICE_OVERRIDES:
        return {"store_id": store_id, "sku": sku, **_PRICE_OVERRIDES[key]}

    products = pd.read_csv(DATA_DIR / "products.csv")
    row = products[products["sku"] == sku]
    if row.empty:
        return {"error": "unknown sku", "sku": sku}
    return {
        "store_id": store_id,
        "sku": sku,
        "price": float(row.iloc[0]["base_price"]),
        "source": "base_price",
    }


@tool
def update_price(
    store_id: str, sku: str, new_price: float, valid_days: int = 7, reason: str = ""
) -> dict:
    """Push a new selling price to the POS / pricing engine.

    Returns the confirmation record.
    """
    record = {
        "price": new_price,
        "valid_days": valid_days,
        "reason": reason,
        "effective_from": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "source": "override",
    }
    _PRICE_OVERRIDES[(store_id, sku)] = record
    return {"store_id": store_id, "sku": sku, "status": "APPLIED", **record}
