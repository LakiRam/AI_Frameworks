"""ERP / Purchase Order mock — represents SAP/Oracle PO creation."""
from __future__ import annotations

import uuid
from datetime import datetime
from langchain_core.tools import tool

# In-memory PO store (would be a real ERP in production)
_PO_LOG: list[dict] = []


@tool
def create_purchase_order(
    store_id: str, sku: str, quantity: int, supplier_id: str, unit_cost: float
) -> dict:
    """Create a purchase order in the ERP. Returns a PO number and total cost."""
    po_number = f"PO-{uuid.uuid4().hex[:8].upper()}"
    total = round(quantity * unit_cost, 2)
    record = {
        "po_number": po_number,
        "store_id": store_id,
        "sku": sku,
        "quantity": quantity,
        "supplier_id": supplier_id,
        "unit_cost": unit_cost,
        "total_value": total,
        "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "status": "SUBMITTED",
    }
    _PO_LOG.append(record)
    return record


def get_po_log() -> list[dict]:
    """Helper for tests / UI to inspect the in-memory PO log."""
    return list(_PO_LOG)
