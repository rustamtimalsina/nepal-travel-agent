def check_altitude_safety(start_altitude_m: int, end_altitude_m: int) -> dict:
    """Validates daily elevation gain against Himalayan Acute Mountain Sickness (AMS) safety rules."""
    gain = end_altitude_m - start_altitude_m

    # Medical rule: Above 3,000m, sleeping elevation should not increase by more than 500m per day
    if end_altitude_m > 3000 and gain > 500:
        return {
            "safe": False,
            "elevation_gain_m": gain,
            "status": "DANGER: High AMS Risk",
            "advisory": f"A daily gain of {gain}m exceeds the safe 500m limit above 3,000m. An acclimatization day or lower camp is mandatory."
        }

    return {
        "safe": True,
        "elevation_gain_m": gain,
        "status": "SAFE: Normal Ascent Rate",
        "advisory": "Elevation gain is within safe physiological limits. Stay hydrated (3-4 liters/day)."
    }