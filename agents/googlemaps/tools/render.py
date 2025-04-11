# tools/render.py
from agents.googlemaps.routechat import render_route_map

def tool_render_map(polyline_coords: list, places_path: str, features_path: str, output_path: str = "route_map.html") -> str:
    """
    Renders a folium map of the route with nearby places and natural features.

    Args:
        polyline_coords: List of (lat, lon) tuples.
        places_path: Path to places JSON file.
        features_path: Path to features JSON file.
        output_path: Output HTML path.

    Returns:
        Path to saved HTML file.
    """
    render_route_map(polyline_coords, places_path, features_path, output_path)
    return output_path


def schema_render_map():
    return {
        "type": "object",
        "properties": {
            "polyline_coords": {"type": "array", "items": {"type": "array", "items": {"type": "number"}, "minItems": 2}, "example": [[37.78, -122.4], [36.7, -121.8]]},
            "places_path": {"type": "string", "example": "places_along_route.json"},
            "features_path": {"type": "string", "example": "natural_features_along_route.json"},
            "output_path": {"type": "string", "default": "route_map.html"}
        },
        "required": ["polyline_coords", "places_path", "features_path"]
    }