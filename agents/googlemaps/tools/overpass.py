# tools/overpass.py
from agents.googlemaps.routechat import get_places_along_polyline, get_natural_features_along_polyline

def tool_get_places_along_polyline(polyline_coords: list, radius_m: int = 2000, method: str = "node") -> list:
    """
    Queries Overpass API for places (cities/towns/villages) near a polyline.

    Args:
        polyline_coords: List of (lat, lon) points.
        radius_m: Search radius in meters.
        method: 'node' or 'way'.

    Returns:
        List of place dicts.
    """
    return get_places_along_polyline(polyline_coords, radius_m, method)

def schema_get_places():
    return {
        "type": "object",
        "properties": {
            "polyline_coords": {"type": "array", "items": {"type": "array", "items": {"type": "number"}, "minItems": 2}, "example": [[37.78, -122.4], [36.7, -121.8]]},
            "radius_m": {"type": "integer", "default": 2000},
            "method": {"type": "string", "enum": ["node", "way"], "default": "node"}
        },
        "required": ["polyline_coords"]
    }

def tool_get_natural_features(polyline_coords: list, radius_m: int = 2000, method: str = "way") -> list:
    """
    Queries Overpass API for natural features (rivers, lakes, forests, etc.) along a polyline.

    Args:
        polyline_coords: List of (lat, lon) tuples.
        radius_m: Radius in meters.
        method: 'way' or 'node'.

    Returns:
        List of feature dicts.
    """
    return get_natural_features_along_polyline(polyline_coords, radius_m, method)

def schema_get_natural_features():
    return {
        "type": "object",
        "properties": {
            "polyline_coords": {"type": "array", "items": {"type": "array", "items": {"type": "number"}, "minItems": 2}, "example": [[37.78, -122.4], [36.7, -121.8]]},
            "radius_m": {"type": "integer", "default": 2000},
            "method": {"type": "string", "enum": ["node", "way"], "default": "node"}
        },
        "required": ["polyline_coords"]
    }
