from .routes import tool_get_route, schema_get_route
from .sample import tool_sample_polyline, schema_sample_polyline
from .overpass import tool_get_places_along_polyline, tool_get_natural_features, schema_get_places, schema_get_natural_features
from .render import tool_render_map, schema_render_map
from .answer import tool_answer, schema_answer

from functools import wraps
import traceback
import jsonschema

# Tool registry with functions and schemas
RAW_REGISTRY = {
    "get_route": (tool_get_route, schema_get_route),
    "sample_polyline": (tool_sample_polyline, schema_sample_polyline),
    "get_places": (tool_get_places_along_polyline, schema_get_places),
    "get_natural_features": (tool_get_natural_features, schema_get_natural_features),
    "render_map": (tool_render_map, schema_render_map),
    "answer": (tool_answer, schema_answer),
}

# Safe wrapper with validation
def safe_tool(fn, schema_fn):
    @wraps(fn)
    def wrapped(params):
        try:
            schema = schema_fn()
            jsonschema.validate(instance=params, schema=schema)
            return fn(**params)
        except Exception as e:
            return {
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    return wrapped

# Final registry with wrapped functions
TOOL_REGISTRY = {name: safe_tool(fn, schema) for name, (fn, schema) in RAW_REGISTRY.items()}

# Example inputs for LLMs
example_inputs = {
    "get_route": {
        "origin": [37.7749, -122.4194],
        "destination": [34.0522, -118.2437],
        "waypoints": []
    },
    "sample_polyline": {
        "encoded_polyline": "xyz123...",
        "method": "nth",
        "every_nth": 10
    },
    "get_places": {
        "polyline_coords": [[37.78, -122.4], [36.7, -121.8]],
        "radius_m": 3000
    },
    "get_natural_features": {
        "polyline_coords": [[37.78, -122.4], [36.7, -121.8]],
        "method": "way"
    },
    "render_map": {
        "polyline_coords": [[37.78, -122.4], [36.7, -121.8]],
        "places_path": "places_along_route.json",
        "features_path": "natural_features_along_route.json"
    },
    "answer": {
    "text": "Based on the route, Springfield, IL is approximately halfway along the way."
}

}

def list_tools():
    """
    Lists all registered tools with descriptions, schemas, and example inputs.

    Returns:
        List of dicts with tool metadata.
    """
    return [
        {
            "name": name,
            "description": fn.__doc__.strip() if fn.__doc__ else "",
            "parameters": schema_fn(),
            "example_input": example_inputs.get(name, {})
        }
        for name, (fn, schema_fn) in RAW_REGISTRY.items()
    ]
