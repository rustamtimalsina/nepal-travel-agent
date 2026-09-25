def get_nepal_trek_permit(region: str) -> dict:
    """Fetches official government permits, fees in NPR, and entry regulations for trekking regions in Nepal."""
    permits = {
        "annapurna": {
            "region": "Annapurna Region (ABC / Circuit / Poon Hill)",
            "permits": ["ACAP (Annapurna Conservation Area Permit)", "TIMS Card"],
            "total_fee_npr": 5000,
            "checkpoints": ["Birethanti", "Besishahar", "Dharapani"],
            "notes": "A certified guide is required as per Nepal Tourism Board regulations."
        },
        "everest": {
            "region": "Khumbu / Everest Region",
            "permits": ["Sagarmatha National Park Entry Permit", "Khumbu Pasang Lhamu Rural Municipality Fee"],
            "total_fee_npr": 5000,
            "checkpoints": ["Lukla", "Monjo"],
            "notes": "TIMS card is no longer accepted in Khumbu; local municipality fee replaced it."
        },
        "langtang": {
            "region": "Langtang Valley & Gosainkunda",
            "permits": ["Langtang National Park Entry Permit", "TIMS Card"],
            "total_fee_npr": 4000,
            "checkpoints": ["Dhunche", "Syabrubesi"],
            "notes": "Carry cash in NPR for teahouses; no reliable ATMs exist beyond Syabrubesi."
        },
        "manaslu": {
            "region": "Manaslu Circuit (Restricted Area)",
            "permits": ["Manaslu Restricted Area Permit (RAP)", "MCAP", "ACAP"],
            "total_fee_npr": 14000,
            "checkpoints": ["Jagat", "Samagaon", "Dharapani"],
            "notes": "Minimum group of 2 trekkers with a licensed government guide is mandatory."
        }
    }

    key = region.lower().strip()
    for name in permits:
        if name in key:
            return permits[name]

    return {
        "error": f"Region '{region}' not recognized. Supported: Annapurna, Everest, Langtang, Manaslu."
    }