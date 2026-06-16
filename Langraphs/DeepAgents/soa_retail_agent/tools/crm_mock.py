"""CRM / Loyalty mock — segmentation + outbound promotion delivery."""
from __future__ import annotations

import uuid
from datetime import datetime
import pandas as pd
from langchain_core.tools import tool

from ..config import DATA_DIR

_PROMO_LOG: list[dict] = []


@tool
def customer_segments(city: str | None = None, min_loyalty_tier: str = "Silver") -> dict:
    """Return loyalty members in a city above a minimum tier.

    Tiers (ranked): Bronze < Silver < Gold < Platinum
    """
    rank = {"Bronze": 1, "Silver": 2, "Gold": 3, "Platinum": 4}
    threshold = rank.get(min_loyalty_tier, 2)
    df = pd.read_csv(DATA_DIR / "customers.csv")
    if city:
        df = df[df["city"].str.lower() == city.lower()]
    df = df[df["loyalty_tier"].map(rank).fillna(0) >= threshold]
    return {
        "city": city,
        "min_loyalty_tier": min_loyalty_tier,
        "count": len(df),
        "members": df.to_dict(orient="records"),
    }


@tool
def send_promotion(
    campaign_name: str, audience_city: str, audience_min_tier: str,
    offer: str, channel: str = "Email"
) -> dict:
    """Send a personalized promotional campaign to a loyalty segment."""
    audience = customer_segments.invoke({
        "city": audience_city, "min_loyalty_tier": audience_min_tier,
    })
    record = {
        "campaign_id": f"CMP-{uuid.uuid4().hex[:8].upper()}",
        "campaign_name": campaign_name,
        "channel": channel,
        "audience_city": audience_city,
        "audience_size": audience["count"],
        "offer": offer,
        "dispatched_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "status": "DISPATCHED",
    }
    _PROMO_LOG.append(record)
    return record
