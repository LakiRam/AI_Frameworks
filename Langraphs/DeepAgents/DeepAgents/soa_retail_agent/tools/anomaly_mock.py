"""Anomaly / shrinkage detection mock — scans POS transaction patterns."""
from __future__ import annotations

import random
from langchain_core.tools import tool


@tool
def scan_pos_anomalies(store_id: str, lookback_hours: int = 24) -> dict:
    """Scan POS transactions for fraud / shrinkage anomalies.

    Returns a list of suspicious events with a risk score (0-1).
    """
    # Deterministic-ish mock so demo behaves consistently
    random.seed(hash(store_id) % 9999)
    n = random.randint(0, 3)
    events = []
    sample_types = [
        ("Excessive void transactions on register R-04", 0.78),
        ("Refund without receipt > 3 in 4h", 0.65),
        ("High-shrinkage SKU scanned but undercounted", 0.83),
        ("Self-checkout skip-scan pattern detected", 0.71),
    ]
    for i in range(n):
        et, rs = random.choice(sample_types)
        events.append({
            "event_id": f"ANM-{store_id}-{i+1:03d}",
            "type": et,
            "risk_score": rs,
            "recommended_action": "Notify Loss Prevention",
        })
    return {
        "store_id": store_id,
        "lookback_hours": lookback_hours,
        "anomalies_found": len(events),
        "events": events,
    }
