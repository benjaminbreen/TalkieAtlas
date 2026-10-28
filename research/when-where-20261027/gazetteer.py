"""Hand-built gazetteer for the When-and-where page.

Coordinates are approximate (city centre or region centroid, about 0.1 degree), entered by hand,
not from a geocoding service. Levels: city places plot as dots; region places plot as rings;
country and wider places are counted but not plotted, since a dot would claim precision the
reply does not give. Ambiguous names resolve to the reading the replies support
(Stratford is Stratford-upon-Avon; Washington alone is the city).
"""

GAZ = {
    # London and Britain: cities and towns
    "London": (51.507, -0.128, "city"), "Westminster": (51.499, -0.135, "city"),
    "Edinburgh": (55.953, -3.189, "city"), "Glasgow": (55.864, -4.252, "city"),
    "Liverpool": (53.408, -2.991, "city"), "Manchester": (53.480, -2.243, "city"),
    "Birmingham": (52.486, -1.890, "city"), "Bristol": (51.454, -2.588, "city"), "Clifton": (51.465, -2.620, "city"),
    "Newcastle upon Tyne": (54.978, -1.618, "city"), "Newcastle": (54.978, -1.618, "city"),
    "Oxford": (51.752, -1.258, "city"), "Cambridge": (52.205, 0.122, "city"), "Exeter": (50.718, -3.534, "city"),
    "Chester": (53.193, -2.893, "city"), "Dorchester": (50.716, -2.437, "city"), "Malmesbury": (51.584, -2.098, "city"),
    "Gainsborough": (53.399, -0.774, "city"), "Chipping Norton": (51.942, -1.546, "city"), "Milverton": (51.026, -3.256, "city"),
    "Stratford": (52.192, -1.708, "city"), "Stratford-upon-Avon": (52.192, -1.708, "city"), "Coventry": (52.407, -1.512, "city"),
    "Holton": (53.85, -2.55, "city"), "Hawick": (55.422, -2.787, "city"), "Heriot": (55.756, -2.958, "city"),
    "Gairloch": (57.728, -5.697, "city"), "Dublin": (53.350, -6.260, "city"), "Belfast": (54.597, -5.930, "city"),
    "Aberdeen": (57.149, -2.094, "city"), "Dundee": (56.462, -2.971, "city"), "Leeds": (53.800, -1.549, "city"),
    "Sheffield": (53.381, -1.470, "city"), "Bath": (51.381, -2.359, "city"), "York": (53.960, -1.087, "city"),
    "Norwich": (52.630, 1.297, "city"), "Plymouth": (50.376, -4.143, "city"), "Portsmouth": (50.820, -1.088, "city"),
    "Brighton": (50.823, -0.138, "city"), "Canterbury": (51.280, 1.080, "city"), "Dover": (51.128, 1.313, "city"),
    "Nottingham": (52.954, -1.158, "city"), "Leicester": (52.637, -1.140, "city"), "Hull": (53.744, -0.333, "city"),
    "Cardiff": (51.482, -3.179, "city"), "Perth": (56.396, -3.437, "city"), "Inverness": (57.478, -4.224, "city"),
    # Britain: regions
    "Scotland": (56.8, -4.2, "region"), "Wales": (52.3, -3.7, "region"), "England": (52.6, -1.5, "country"),
    "Ireland": (53.2, -8.0, "country"), "Northern Ireland": (54.6, -6.7, "region"),
    "Yorkshire": (53.95, -1.3, "region"), "West Riding": (53.75, -1.6, "region"), "Lancashire": (53.8, -2.6, "region"),
    "Cornwall": (50.4, -4.9, "region"), "Devonshire": (50.7, -3.8, "region"), "Devon": (50.7, -3.8, "region"),
    "Dorset": (50.75, -2.35, "region"), "Somerset": (51.1, -3.0, "region"), "Wiltshire": (51.3, -1.9, "region"),
    "Essex": (51.8, 0.6, "region"), "Suffolk": (52.2, 1.0, "region"), "Berkshire": (51.45, -1.2, "region"),
    "Hertfordshire": (51.8, -0.2, "region"), "Oxfordshire": (51.8, -1.3, "region"), "Lincolnshire": (53.1, -0.2, "region"),
    "Kent": (51.2, 0.7, "region"), "Surrey": (51.25, -0.4, "region"), "Sussex": (50.95, -0.3, "region"),
    "Norfolk": (52.65, 1.0, "region"), "Middlesex": (51.55, -0.35, "region"), "Midlothian": (55.83, -3.1, "region"),
    "Inverness-shire": (57.3, -4.9, "region"), "Scottish Highlands": (57.4, -4.8, "region"), "Highlands": (57.4, -4.8, "region"),
    "North of England": (54.6, -2.0, "region"), "County Galway": (53.3, -8.9, "region"), "Galway": (53.27, -9.05, "city"),
    # Europe
    "Paris": (48.857, 2.352, "city"), "Rue Saint-Denis": (48.865, 2.351, "city"), "Bordeaux": (44.838, -0.579, "city"),
    "Chateaubriand": (47.717, -1.376, "city"), "Châteaubriant": (47.717, -1.376, "city"), "Lyon": (45.764, 4.836, "city"),
    "Marseille": (43.296, 5.370, "city"), "Corsica": (42.1, 9.0, "region"), "Rome": (41.903, 12.496, "city"),
    "Naples": (40.852, 14.268, "city"), "Florence": (43.770, 11.256, "city"), "Venice": (45.441, 12.316, "city"),
    "Berlin": (52.520, 13.405, "city"), "Hanover": (52.376, 9.732, "city"), "Hamburg": (53.551, 9.994, "city"),
    "Vienna": (48.208, 16.373, "city"), "Amsterdam": (52.370, 4.895, "city"), "Brussels": (50.850, 4.352, "city"),
    "Geneva": (46.204, 6.143, "city"), "Madrid": (40.417, -3.704, "city"), "Lisbon": (38.722, -9.139, "city"),
    "St. Petersburg": (59.934, 30.336, "city"), "Moscow": (55.756, 37.617, "city"), "Christiansand": (58.146, 7.996, "city"),
    "Kristiansand": (58.146, 7.996, "city"), "Christianshaven": (58.146, 7.996, "city"), "Malta": (35.9, 14.45, "region"),
    "Athens": (37.984, 23.728, "city"), "Constantinople": (41.008, 28.978, "city"),
    "France": (46.6, 2.4, "country"), "Germany": (51.2, 10.4, "country"), "Italy": (42.8, 12.6, "country"),
    "Russia": (60.0, 60.0, "country"), "European Russia": (56.0, 40.0, "region"), "Norway": (61.0, 9.0, "country"),
    "Spain": (40.2, -3.6, "country"), "Switzerland": (46.8, 8.2, "country"), "Holland": (52.2, 5.3, "country"),
    "Netherlands": (52.2, 5.3, "country"), "Belgium": (50.6, 4.6, "country"), "Austria": (47.6, 14.1, "country"),
    "Poland": (52.0, 19.4, "country"), "Greece": (39.1, 22.0, "country"), "Europe": (50.0, 10.0, "continent"),
    # The Americas
    "New York City": (40.713, -74.006, "city"), "New York": (40.713, -74.006, "city"), "Boston": (42.360, -71.059, "city"),
    "Philadelphia": (39.953, -75.164, "city"), "Washington, D.C.": (38.907, -77.037, "city"), "Washington": (38.907, -77.037, "city"),
    "Chicago": (41.878, -87.630, "city"), "San Francisco": (37.775, -122.419, "city"), "Cincinnati": (39.103, -84.512, "city"),
    "New Orleans": (29.951, -90.072, "city"), "Nashua": (42.765, -71.468, "city"), "Duluth": (46.787, -92.100, "city"),
    "Baltimore": (39.290, -76.612, "city"), "Charleston": (32.777, -79.931, "city"), "Richmond": (37.541, -77.436, "city"),
    "St. Louis": (38.627, -90.199, "city"), "Pittsburgh": (40.441, -79.996, "city"), "Detroit": (42.331, -83.046, "city"),
    "James Town": (37.209, -76.775, "city"), "Jamestown": (37.209, -76.775, "city"),
    "Quebec": (46.813, -71.208, "city"), "Trois-Rivières": (46.343, -72.543, "city"), "Montreal": (45.502, -73.567, "city"),
    "Toronto": (43.653, -79.383, "city"), "Halifax": (44.649, -63.575, "city"),
    "New York State": (42.9, -75.5, "region"), "Massachusetts": (42.3, -71.8, "region"), "Virginia": (37.5, -78.8, "region"),
    "Maine": (45.3, -69.2, "region"), "California": (37.2, -119.5, "region"), "Ohio": (40.4, -82.8, "region"),
    "Pennsylvania": (40.9, -77.8, "region"), "New Hampshire": (43.7, -71.6, "region"), "Minnesota": (46.3, -94.3, "region"),
    "Kentucky": (37.5, -85.3, "region"), "Texas": (31.0, -99.0, "region"), "Illinois": (40.0, -89.2, "region"),
    "West Indies": (17.0, -70.0, "region"), "Jamaica": (18.1, -77.3, "region"),
    "United States": (39.8, -98.6, "country"), "America": (39.8, -98.6, "country"), "Canada": (56.0, -96.0, "country"),
    "Mexico": (23.6, -102.5, "country"), "Brazil": (-10.0, -52.0, "country"),
    # Africa, Asia, Oceania
    "Cairo": (30.044, 31.236, "city"), "Memphis": (29.845, 31.250, "city"), "Alexandria": (31.200, 29.919, "city"),
    "Galilee": (32.8, 35.5, "region"), "Jerusalem": (31.778, 35.235, "city"), "Zululand": (-28.0, 31.5, "region"),
    "Cape Town": (-33.925, 18.424, "city"), "Bombay": (18.940, 72.835, "city"), "Calcutta": (22.573, 88.364, "city"),
    "Madras": (13.083, 80.270, "city"), "Canton": (23.129, 113.264, "city"), "Peking": (39.904, 116.407, "city"),
    "Sydney": (-33.869, 151.209, "city"), "Melbourne": (-37.814, 144.963, "city"), "New South Wales": (-32.5, 147.0, "region"),
    "Egypt": (26.8, 30.8, "country"), "India": (21.0, 78.0, "country"), "China": (35.0, 103.0, "country"),
    "Japan": (36.2, 138.3, "country"), "Guinea": (10.0, -11.0, "country"), "South Africa": (-29.0, 24.0, "country"),
    "Australia": (-25.3, 133.8, "country"), "New Zealand": (-41.3, 174.0, "country"), "Israel": (31.5, 34.9, "country"),
    "Palestine": (31.9, 35.2, "country"), "Turkey": (39.0, 35.2, "country"), "Persia": (32.4, 53.7, "country"),
    "Grimsey": (66.54, -18.0, "city"), "Iceland": (64.9, -18.6, "country"), "Spion Kop": (-28.65, 29.52, "city"),
    "Ladysmith": (-28.56, 29.78, "city"), "Pretoria": (-25.75, 28.19, "city"), "Transvaal": (-25.5, 29.0, "region"), "Timbuktu": (16.77, -3.01, "city"), "Mesopotamia": (33.0, 44.0, "region"),
    "United States of America": (39.8, -98.6, "country"),
    "Asia": (34.0, 100.0, "continent"), "Africa": (2.0, 21.0, "continent"), "Caribbean": (17.0, -70.0, "region"),
    # Wider than a country
    "Great Britain": (54.0, -2.5, "country"), "United Kingdom": (54.0, -2.5, "country"), "Britain": (54.0, -2.5, "country"),
    "Great Britain and Ireland": (54.0, -4.0, "country"),
}

# Spellings and aliases that should share one pin.
CANON = {"New York City": "New York", "Newcastle": "Newcastle upon Tyne", "Stratford-upon-Avon": "Stratford", "Kristiansand": "Christiansand",
         "Christianshaven": "Christiansand", "Jamestown": "James Town", "Devon": "Devonshire", "Washington, D.C.": "Washington",
         "Châteaubriant": "Chateaubriand", "Highlands": "Scottish Highlands", "Rue Saint-Denis": "Paris"}

def resolve(place):
    hit = _resolve(place)
    return hit and (CANON.get(hit[0], hit[0]), *hit[1:])

def _resolve(place):
    """Return (key, lat, lon, level, district) for the most specific known component, or None.
    district is the London street or area when the place is inside London."""
    parts = [p.strip() for p in place.split(",") if p.strip()]
    joined = ", ".join(parts[:2])
    if joined in GAZ:  # "Washington, D.C."
        lat, lon, level = GAZ[joined]
        return joined, lat, lon, level, ""
    for i, p in enumerate(parts):
        if p in GAZ:
            lat, lon, level = GAZ[p]
            if p in ("London", "Westminster") or "London" in parts[i:]:
                return "London", *GAZ["London"], (parts[0] if i > 0 or p == "Westminster" else "")
            return p, lat, lon, level, ""
    return None
