"""Mock weather forecast — in production wire to OpenWeather or AccuWeather API."""
from __future__ import annotations

from langchain_core.tools import tool

# Hard-coded mock signals so the demo is deterministic
_MOCK_WEATHER = {
    "Mumbai": {"condition": "Heatwave", "max_temp_c": 41, "anomaly": True},
    "Bangalore": {"condition": "Heatwave", "max_temp_c": 39, "anomaly": True},
    "Delhi": {"condition": "Clear", "max_temp_c": 36, "anomaly": False},
    "Hyderabad": {"condition": "Heatwave", "max_temp_c": 42, "anomaly": True},
    "Chennai": {"condition": "Humid", "max_temp_c": 35, "anomaly": False},
    "Kolkata": {"condition": "Rain", "max_temp_c": 31, "anomaly": False},
    "Noida": {"condition": "Clear", "max_temp_c": 37, "anomaly": False},
}


@tool
def get_weather_forecast(city: str, days_ahead: int = 3) -> dict:
    """Get the weather forecast for a city.

    Returns the dominant condition, expected max temperature (C),
    and an `anomaly` flag (True for heatwaves, storms, etc.).
    """
    city_norm = city.strip().title()
    info = _MOCK_WEATHER.get(city_norm, {
        "condition": "Normal", "max_temp_c": 30, "anomaly": False
    })
    return {"city": city_norm, "days_ahead": days_ahead, **info}
