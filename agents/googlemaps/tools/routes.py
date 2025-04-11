# tools/routes.py
from agents.googlemaps.routechat import get_google_route

def tool_get_route(origin: tuple, destination: tuple, waypoints: list = []) -> dict:
    """
    Fetches a driving route using Google Maps Routes API.

    Args:
        origin: Tuple (lat, lon) of origin.
        destination: Tuple (lat, lon) of destination.
        waypoints: Optional list of intermediate (lat, lon) tuples.

    Returns:
        Dict with polyline, distance, duration, steps, etc.
    """
    return get_google_route(origin, destination, waypoints)


def schema_get_route():
    return {
        "type": "object",
        "properties": {
            "origin": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2, "example": [37.7749, -122.4194]},
            "destination": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2, "example": [34.0522, -118.2437]},
            "waypoints": {
                "type": "array",
                "items": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2},
                "default": [],
                "example": [[36.7783, -119.4179]]
            }
        },
        "required": ["origin", "destination"]
    }
