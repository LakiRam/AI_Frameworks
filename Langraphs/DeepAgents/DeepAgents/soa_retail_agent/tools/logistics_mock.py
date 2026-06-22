"""Logistics / TMS mock — shipment tracking + expedite calls to 3PL."""
from __future__ import annotations

import random
import uuid
from langchain_core.tools import tool

_SHIPMENTS: dict[str, dict] = {}


@tool
def check_shipment_status(po_number: str) -> dict:
    """Get the current logistics status for a PO."""
    if po_number not in _SHIPMENTS:
        # Simulate a status based on PO number
        statuses = ["IN_TRANSIT", "AT_HUB", "OUT_FOR_DELIVERY", "DELAYED"]
        _SHIPMENTS[po_number] = {
            "po_number": po_number,
            "carrier": random.choice(["Delhivery", "BlueDart", "Ecom Express"]),
            "status": random.choice(statuses),
            "eta_days": random.randint(1, 6),
        }
    return _SHIPMENTS[po_number]


@tool
def expedite_shipment(po_number: str, reason: str) -> dict:
    """Request the 3PL carrier to expedite a shipment.

    Returns an updated ETA (typically 40-60% faster).
    """
    current = check_shipment_status.invoke({"po_number": po_number})
    new_eta = max(1, int(current["eta_days"] * 0.5))
    _SHIPMENTS[po_number].update({
        "status": "EXPEDITED",
        "eta_days": new_eta,
        "expedite_reason": reason,
        "expedite_ticket": f"EXP-{uuid.uuid4().hex[:6].upper()}",
    })
    return _SHIPMENTS[po_number]
