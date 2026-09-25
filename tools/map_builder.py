import folium

WAYPOINTS = {
    "everest": [
        {"name": "Lukla Airport", "coords": [27.6881, 86.7314], "elev": "2,840m", "desc": "Flight gateway to Khumbu"},
        {"name": "Monjo Checkpoint", "coords": [27.7700, 86.7200], "elev": "2,840m", "desc": "Sagarmatha NP entry & permit gate"},
        {"name": "Namche Bazaar", "coords": [27.8069, 86.7140], "elev": "3,440m", "desc": "Sherpa capital & acclimatization hub"},
        {"name": "Everest View Hotel", "coords": [27.8220, 86.7200], "elev": "3,880m", "desc": "Acclimatization panoramic viewpoint"},
        {"name": "Tengboche Monastery", "coords": [27.8358, 86.7645], "elev": "3,860m", "desc": "Historic spiritual monastery"}
    ],
    "annapurna": [
        {"name": "Nayapul", "coords": [28.2980, 83.7620], "elev": "1,070m", "desc": "Trek starting point"},
        {"name": "Ghorepani", "coords": [28.4010, 83.7020], "elev": "2,860m", "desc": "Gateway to Poon Hill sunrise"},
        {"name": "Tadapani", "coords": [28.3960, 83.7630], "elev": "2,630m", "desc": "Forest settlement"},
        {"name": "Chhomrong", "coords": [28.4190, 83.8200], "elev": "2,170m", "desc": "Gateway to ABC valley"},
        {"name": "Annapurna Base Camp", "coords": [28.5300, 83.8780], "elev": "4,130m", "desc": "Sanctuary destination"}
    ],
    "langtang": [
        {"name": "Syabrubesi", "coords": [28.1580, 85.3400], "elev": "1,503m", "desc": "Langtang trailhead roadhead"},
        {"name": "Lama Hotel", "coords": [28.1880, 85.4200], "elev": "2,480m", "desc": "Riverside lodge stop"},
        {"name": "Langtang Village", "coords": [28.2160, 85.5000], "elev": "3,430m", "desc": "Rebuilt Himalayan valley village"},
        {"name": "Kyanjin Gompa", "coords": [28.2120, 85.5683], "elev": "3,870m", "desc": "Monastery & peak base"}
    ],
    "manaslu": [
        {"name": "Soti Khola", "coords": [28.2250, 84.9750], "elev": "700m", "desc": "Manaslu circuit start"},
        {"name": "Jagat", "coords": [28.3670, 84.9000], "elev": "1,410m", "desc": "RAP police checkpoint"},
        {"name": "Samagaon", "coords": [28.5900, 84.6300], "elev": "3,530m", "desc": "Acclimatization base"},
        {"name": "Larkya La Pass", "coords": [28.6470, 84.5020], "elev": "5,106m", "desc": "High altitude glaciated pass"}
    ]
}

def render_trail_map(region_key: str):
    """Generates an interactive Folium trail map with plotted markers and trail line."""
    key = region_key.lower().strip()
    points = WAYPOINTS.get(key, WAYPOINTS["annapurna"])

    center_lat = points[len(points) // 2]["coords"][0]
    center_lon = points[len(points) // 2]["coords"][1]

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=11,
        tiles="OpenStreetMap"
    )

    trail_coords = []
    for pt in points:
        trail_coords.append(pt["coords"])
        popup_html = f"<b>{pt['name']}</b><br>Altitude: {pt['elev']}<br><i>{pt['desc']}</i>"
        folium.Marker(
            location=pt["coords"],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{pt['name']} ({pt['elev']})",
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(m)

    folium.PolyLine(
        locations=trail_coords,
        color="#0066cc",
        weight=4,
        opacity=0.8,
        dash_array="6"
    ).add_to(m)

    return m