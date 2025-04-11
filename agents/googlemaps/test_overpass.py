import requests

def get_overpass_places(sampled_points: list, radius_m: int = 1000) -> list:
    """
    Queries Overpass API to find nearby cities, towns, and villages around sampled lat/lng points.

    Args:
        sampled_points (list): A list of (latitude, longitude) tuples sampled along the route.
        radius_m (int): Search radius in meters around each point.

    Returns:
        list: A list of dictionaries containing place information (name, type, lat, lon).
    """
    # Start constructing the Overpass QL query
    query = "[out:json][timeout:25];\n"
    query += "(\n"
    for lat, lon in sampled_points:
        query += f"  node(around:{radius_m},{lat},{lon})[\"place\"~\"city|town|village\"];\n"
    query += ");\n"
    query += "out center;"

    # Send the query using a POST request
    response = requests.post("http://overpass-api.de/api/interpreter", data={"data": query})
    if response.status_code != 200:
        raise Exception(f"Overpass API error: {response.status_code} - {response.text}")

    elements = response.json().get("elements", [])
    seen = set()
    places = []

    for elem in elements:
        name = elem.get("tags", {}).get("name")
        place_type = elem.get("tags", {}).get("place")
        lat = elem.get("lat")
        lon = elem.get("lon")

        if name and (name, place_type) not in seen:
            places.append({
                "name": name,
                "type": place_type,
                "lat": lat,
                "lon": lon
            })
            seen.add((name, place_type))

    return places



# sampled_points = [
#     (34.0522, -118.2437),  # Los Angeles, CA
#     (36.7783, -119.4179),  # Near Fresno, CA
#     (37.7749, -122.4194),  # San Francisco, CA
#     # Add more points as needed
# ]

# places_along_route = get_overpass_places(sampled_points, radius_m=50000)

# for place in places_along_route:
#     print(f"Name: {place['name']}, Type: {place['type']}, Lat: {place['lat']}, Lon: {place['lon']}")


def get_places_along_polyline(polyline_coords: list, radius_m: int = 2000, method: str = "node") -> list: #out of RAM for long polylines; failed for SF to LA
    """
    Queries Overpass API for places (city/town/village) along a polyline using 'node' or 'way' method.

    Args:
        polyline_coords (list): List of (lat, lon) tuples representing the full polyline route.
        radius_m (int): Radius in meters for searching places along the polyline.
        method (str): 'node' for per-point buffer or 'way' for polyline query.

    Returns:
        list: List of place dicts with name, type, lat, lon.
    """
    if not polyline_coords:
        return []

    def format_polyline_for_overpass(coords):
        return " ".join([f"{lat} {lon}" for lat, lon in coords])

    if method == "way":
        poly_string = format_polyline_for_overpass(polyline_coords)
        query = f"""
        [out:json][timeout:60];
        way(poly:"{poly_string}")->.route;
        node["place"~"city|town|village"](around.route:{radius_m});
        out center;
        """
    elif method == "node":
        query = "[out:json][timeout:60];(\n"
        for lat, lon in polyline_coords:
            query += f'  node(around:{radius_m},{lat},{lon})["place"~"city|town|village"];\n'
        query += ");out center;"
    else:
        raise ValueError("Method must be 'way' or 'node'.")

    response = requests.post("http://overpass-api.de/api/interpreter", data={"data": query})
    print(response.json())
    if response.status_code != 200:
        raise Exception(f"Overpass API error: {response.status_code} - {response.text}")

    elements = response.json().get("elements", [])
    seen = set()
    places = []

    for elem in elements:
        name = elem.get("tags", {}).get("name")
        place_type = elem.get("tags", {}).get("place")
        lat = elem.get("lat")
        lon = elem.get("lon")

        if name and (name, place_type) not in seen:
            places.append({
                "name": name,
                "type": place_type,
                "lat": lat,
                "lon": lon
            })
            seen.add((name, place_type))

    return places

import json

# Load sampled points from file
with open("sampled_points.json", "r") as f:
    sampled_points = json.load(f)

# Query Overpass for places along the route using the 'way' method
places_along_route = get_places_along_polyline(sampled_points, method="way", radius_m=2000)

# Print or save results
for place in places_along_route:
    print(f"{place['name']} ({place['type']}) - Lat: {place['lat']}, Lon: {place['lon']}")
