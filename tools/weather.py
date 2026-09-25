import json
import urllib.request


def get_himalayan_weather(location_name: str) -> dict:
    """Fetches real-time weather, temperature in Celsius, wind speeds, and precipitation for Himalayan key locations.

    Supported locations: Lukla, Namche, Tengboche, Pokhara, Annapurna Base Camp, Kyanjin Gompa, Manaslu.
    """
    coordinates = {
        "lukla": {"lat": 27.6881, "lon": 86.7314, "elev_m": 2840},
        "namche": {"lat": 27.8069, "lon": 86.7140, "elev_m": 3440},
        "namche bazaar": {"lat": 27.8069, "lon": 86.7140, "elev_m": 3440},
        "tengboche": {"lat": 27.8358, "lon": 86.7645, "elev_m": 3860},
        "annapurna base camp": {"lat": 28.5300, "lon": 83.8780, "elev_m": 4130},
        "pokhara": {"lat": 28.2096, "lon": 83.9856, "elev_m": 820},
        "kyanjin gompa": {"lat": 28.2120, "lon": 85.5683, "elev_m": 3870},
        "langtang": {"lat": 28.2120, "lon": 85.5683, "elev_m": 3870},
        "manaslu": {"lat": 28.5500, "lon": 84.6333, "elev_m": 3500},
    }

    key = location_name.lower().strip()
    match = None
    for name, coords in coordinates.items():
        if name in key or key in name:
            match = (name, coords)
            break

    if not match:
        return {
            "error": f"Coordinates not indexed for '{location_name}'. Defaulting to general regional safety advisory."
        }

    resolved_name, coords = match

    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={coords['lat']}&longitude={coords['lon']}&"
        f"current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,wind_speed_10m"
    )

    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "NepalTravelAgent/1.0"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            current = data.get("current", {})
            return {
                "location": resolved_name.title(),
                "elevation_m": coords["elev_m"],
                "temperature_c": current.get("temperature_2m"),
                "feels_like_c": current.get("apparent_temperature"),
                "humidity_percent": current.get("relative_humidity_2m"),
                "wind_speed_kmh": current.get("wind_speed_10m"),
                "precipitation_mm": current.get("precipitation"),
                "source": "Open-Meteo Real-Time Meteorological API",
            }
    except Exception as err:
        return {"error": f"Failed to contact meteorological station: {str(err)}"}