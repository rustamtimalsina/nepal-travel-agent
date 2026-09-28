def calculate_teahouse_budget(region: str, trek_days: int, trekking_style: str = "Standard", hire_guide: bool = False, hire_porter: bool = False) -> dict:
    """
    Calculates estimated daily and total budget for Himalayan teahouse trekking,including teahouse expenses, certified guide wages, and porter fees.
    Covers rooms, meals (Dal Bhat power), hot gas/solar showers, battery charging, and cash reserve buffers.
    
   Args:
        region: Trekking region ('Everest', 'Annapurna', 'Langtang', 'Manaslu')
        trek_days: Total duration of the trek in days
        trekking_style: 'Budget', 'Standard', or 'Comfort'
        hire_guide: Whether a certified trekking guide is hired (~$30/day)
        hire_porter: Whether a porter is hired (~$22/day for max 18-20 kg)
    """
   # Current exchange rate baseline
    usd_to_npr = 145.0
    # Region elevation factor (Khumbu / Manaslu logistics carry higher supply costs)
    region_multipliers = {
        "everest": 1.25,
        "manaslu": 1.20,
        "annapurna": 1.0,
        "langtang": 0.95
    }
    
    reg_key = region.lower().strip()
    multiplier = region_multipliers.get(reg_key, 1.0)

    # Base daily rates in NPR (excluding permits)
    tiers = {
        "budget": {
            "room_npr": 500,
            "meals_npr": 2800,       # 3 meals (Dal Bhat, porridge, tea)
            "hot_shower_npr": 0,      # Wet wipes / skip paid geysers
            "device_charging_npr": 200,
            "drinking_water_npr": 100 # Purification tablets (Aquatabs)
        },
        "standard": {
            "room_npr": 800,
            "meals_npr": 3500,       # 3 hot meals + snacks + bakery
            "hot_shower_npr": 400,    # Gas/solar shower every 2-3 days
            "device_charging_npr": 350,
            "drinking_water_npr": 300 # Occasional boiled water + tablets
        },
        "comfort": {
            "room_npr": 1500,        # Attached bathroom where available
            "meals_npr": 4500,       # A-la-carte dishes, desserts, hot lemon ginger
            "hot_shower_npr": 600,
            "device_charging_npr": 500,
            "drinking_water_npr": 500
        }
    }

    style_key = trekking_style.lower().strip()
    tier = tiers.get(style_key, tiers["standard"])
    personal_daily_npr = round(sum(tier.values()) * multiplier)
# Support Staff Standard Daily Rates (Wages + Meals/Accommodation + Insurance)
    guide_daily_usd = 30.0 if hire_guide else 0.0
    porter_daily_usd = 22.0 if hire_porter else 0.0

    guide_daily_npr = round(guide_daily_usd * usd_to_npr)
    porter_daily_npr = round(porter_daily_usd * usd_to_npr)

    total_daily_npr = personal_daily_npr + guide_daily_npr + porter_daily_npr
    total_daily_usd = round(total_daily_npr / usd_to_npr, 2)

    total_npr = total_daily_npr * trek_days
    total_usd = round(total_npr / usd_to_npr, 2)
    
    # 20% cash emergency buffer recommendation (no ATMs above Namche/Manang)
    emergency_buffer_npr = round(total_npr * 0.20)
    emergency_buffer_usd = round(emergency_buffer_npr / usd_to_npr, 2)

    return {
        "region": region.title(),
        "trek_days": trek_days,
        "trekking_style": trekking_style.title(),
        "personal_daily_npr": personal_daily_npr,
        "guide_daily_usd": guide_daily_usd,
        "porter_daily_usd": porter_daily_usd,
        "total_daily_npr": total_daily_npr,
        "total_daily_usd": total_daily_usd,
        "total_estimated_npr": total_npr,
        "total_estimated_usd": total_usd,
        "recommended_cash_buffer_npr": emergency_buffer_npr,
        "recommended_cash_buffer_usd": emergency_buffer_usd,
        "currency_exchange_rate": f"1 USD = {usd_to_npr} NPR",
        "staff_details": {
            "guide_hired": hire_guide,
            "porter_hired": hire_porter,
            "porter_weight_limit": "Max 18-20 kg luggage carry limit" if hire_porter else "N/A"
        },
        "golden_rule": "Always carry full cash in NPR from Kathmandu/Pokhara. ATMs in the mountains are unreliable or nonexistent."
    }