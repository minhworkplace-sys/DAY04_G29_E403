from __future__ import annotations

from typing import Any

import requests

from tools._shared import TIMEOUT, err


def get_weather(city: str = "", units: str = "metric") -> dict[str, Any]:
    """Lấy thời tiết hiện tại cho một thành phố qua wttr.in (miễn phí, không cần API key)."""
    try:
        if not city:
            return err("weather", ValueError("'city' is required"))

        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": "research-agent/1.0"})
        response.raise_for_status()
        data = response.json()

        current = data.get("current_condition", [{}])[0]
        temp_c = current.get("temp_C", "N/A")
        feels_like = current.get("FeelsLikeC", "N/A")
        desc = current.get("weatherDesc", [{}])[0].get("value", "N/A")
        humidity = current.get("humidity", "N/A")
        wind = current.get("windspeedKmph", "N/A")

        # 3-day forecast
        forecast = []
        for day in data.get("weather", [])[:3]:
            forecast.append({
                "date": day.get("date", ""),
                "max_temp_c": day.get("maxtempC", ""),
                "min_temp_c": day.get("mintempC", ""),
                "description": day.get("hourly", [{}])[4].get("weatherDesc", [{}])[0].get("value", ""),
            })

        result: dict[str, Any] = {
            "tool": "weather",
            "city": city,
            "units": units,
            "current": {
                "temp_c": temp_c,
                "feels_like_c": feels_like,
                "description": desc,
                "humidity_pct": humidity,
                "wind_kmph": wind,
            },
            "forecast": forecast,
        }

        if units == "imperial":
            result["current"]["temp_f"] = str(round(int(temp_c) * 9 / 5 + 32)) if temp_c != "N/A" else "N/A"

        return result

    except Exception as exc:
        return err("weather", exc)
