def generate_packing_checklist(max_elevation_m: int, duration_days: int, current_temp_c: float = 5.0) -> dict:
    """Generates an essential Nepal trekking packing checklist based on elevation, duration, and ambient temperature.
    
    Args:
        max_elevation_m: Peak altitude reached on the route in meters.
        duration_days: Total length of the trek.
        current_temp_c: Current weather temperature in Celsius from meteorological telemetry.
    """
    is_sub_zero = current_temp_c <= 0 or max_elevation_m >= 3500
    high_altitude = max_elevation_m >= 4000

    checklist = {
        "Base Clothing & Layering": [
            f"{min(duration_days, 4)}x Moisture-wicking synthetic/merino base layers (Avoid cotton)",
            "1x Mid-layer fleece jacket or lightweight grid fleece",
            f"1x Down jacket ({'Rated -15°C to -20°C high-loft' if is_sub_zero else 'Rated 0°C to -5°C lightweight'})",
            "1x Windproof & waterproof outer shell jacket (Gore-Tex or equivalent)",
            "2x Quick-dry trekking pants + 1x thermal leggings for night/cold passes"
        ],
        "Footwear & Trail Hardware": [
            "1x Sturdy high-ankle waterproof trekking boots (broken-in)",
            f"{min(duration_days, 5)}x Merino wool trekking socks + 2x thin liner socks",
            "1x Microspikes / crampons" if high_altitude or is_sub_zero else "1x Lightweight trail microspikes (precautionary)",
            "1x Pair of adjustable trekking poles (reduces knee impact by 25%)",
            "1x Camp shoes / lightweight sandals for teahouse dining halls"
        ],
        "Health, Altitude & Hydration": [
            "Acetazolamide (Diamox 125mg/250mg) - consult physician for AMS prevention",
            "Water purification tablets (Aquatabs / Micropur) or UV SteriPEN (never drink raw tap/river water)",
            "Electrolyte rehydration salts (ORS sachets)",
            "Broad-spectrum SPF 50+ Sunscreen and UV-rated Lip Balm (UV radiation increases 10-12% every 1,000m)",
            "Personal blister kit (Compeed patches, zinc oxide tape, antiseptic wipes)"
        ],
        "Electronics & Alpine Essentials": [
            f"1x High-capacity power bank ({'20,000 mAh' if duration_days > 5 else '10,000 mAh'}) - cold temperatures drain batteries rapidly",
            "1x LED Headlamp (with spare rechargeable batteries) for pre-dawn viewpoint pushes",
            "1x Heavy-duty sleeping bag liner (silk or fleece) to boost teahouse blanket warmth",
            "1x Category 3 or 4 UV-blocking Glacier sunglasses (essential to prevent snow blindness)",
            "Dry bags or waterproof pack liner for your 40L-50L rucksack"
        ]
    }

    return checklist