"""
Tool specifications for the agent framework.

This module provides specifications for tools that can be used by agents.
"""
from typing import Dict, Any


# Google Maps tool specifications
GOOGLEMAPS_TOOL_SPECS: Dict[str, Dict[str, Any]] = {
    "get_route": {
        "description": "Calculate a new driving route between a given origin and destination, possibly with waypoints.",
        "parameters": {
            "origin": {
                "type": "array",
                "description": "The [latitude, longitude] of the starting point."
            },
            "destination": {
                "type": "array",
                "description": "The [latitude, longitude] of the destination."
            },
            "waypoints": {
                "type": "array",
                "description": "Optional list of [latitude, longitude] tuples as intermediate stops."
            },
            "travel_mode": {
                "type": "string",
                "description": "Travel mode (DRIVE, BICYCLE, WALK, TWO_WHEELER). Defaults to DRIVE."
            },
            "avoid_tolls": {
                "type": "boolean",
                "description": "Whether to avoid tolls. Defaults to false."
            }
        },
        "required": ["origin", "destination"],
        "examples": [
            {
                "tool": "get_route",
                "tool_input": {
                    "origin": [37.7749, -122.4194],
                    "destination": [34.0522, -118.2437]
                },
                "reasoning": "The user wants directions between San Francisco and Los Angeles."
            }
        ]
    },
    
    "sample_polyline": {
        "description": "Reduce the number of lat/lon points along a route to simplify later processing.",
        "parameters": {
            "encoded_polyline": {
                "type": "string",
                "description": "The encoded polyline string from Google Maps."
            },
            "method": {
                "type": "string",
                "description": "Sampling method: 'interval' for distance-based or 'nth' for index-based."
            },
            "interval_km": {
                "type": "number",
                "description": "Distance interval in kilometers between samples (if method is 'interval')."
            },
            "every_nth": {
                "type": "integer",
                "description": "Take every nth point (if method is 'nth')."
            }
        },
        "required": ["encoded_polyline"],
        "examples": [
            {
                "tool": "sample_polyline",
                "tool_input": {
                    "encoded_polyline": "abc123...",
                    "method": "interval",
                    "interval_km": 5.0
                },
                "reasoning": "Reduce route points to simplify place lookup."
            }
        ]
    },
    
    "get_places": {
        "description": "Find towns and cities along the route using lat/lon points.",
        "parameters": {
            "polyline_coords": {
                "type": "array",
                "description": "List of [latitude, longitude] tuples representing the route."
            },
            "radius_m": {
                "type": "integer",
                "description": "Search radius in meters around each point."
            },
            "method": {
                "type": "string",
                "description": "'node' for per-point buffer or 'way' for polyline query."
            }
        },
        "required": ["polyline_coords"],
        "examples": [
            {
                "tool": "get_places",
                "tool_input": {
                    "polyline_coords": [[37.7, -122.4], [36.7, -121.8]],
                    "radius_m": 3000,
                    "method": "node"
                },
                "reasoning": "The user wants to know which towns are along the route."
            }
        ]
    },
    
    "get_natural_features": {
        "description": "Find natural landmarks like rivers, parks, and forests along the route.",
        "parameters": {
            "polyline_coords": {
                "type": "array",
                "description": "List of [latitude, longitude] tuples representing the route."
            },
            "radius_m": {
                "type": "integer",
                "description": "Search radius in meters around each point."
            },
            "method": {
                "type": "string",
                "description": "'node' for per-point buffer or 'way' for polyline query."
            }
        },
        "required": ["polyline_coords"],
        "examples": [
            {
                "tool": "get_natural_features",
                "tool_input": {
                    "polyline_coords": [[37.7, -122.4], [36.7, -121.8]],
                    "radius_m": 2000,
                    "method": "way"
                },
                "reasoning": "The user asked about natural landmarks along the route."
            }
        ]
    },
    
    "render_map": {
        "description": "Generate an HTML map showing the route and any available cities or landmarks.",
        "parameters": {
            "polyline_coords": {
                "type": "array",
                "description": "List of [latitude, longitude] tuples representing the route."
            },
            "places": {
                "type": "array",
                "description": "Optional list of place dictionaries."
            },
            "features": {
                "type": "array",
                "description": "Optional list of feature dictionaries."
            },
            "places_path": {
                "type": "string",
                "description": "Optional path to JSON file with places data."
            },
            "features_path": {
                "type": "string",
                "description": "Optional path to JSON file with features data."
            },
            "output_file": {
                "type": "string",
                "description": "Output HTML file path."
            }
        },
        "required": ["polyline_coords"],
        "examples": [
            {
                "tool": "render_map",
                "tool_input": {
                    "polyline_coords": [[37.7, -122.4], [36.7, -121.8]],
                    "places_path": "places_along_route.json",
                    "features_path": "natural_features_along_route.json",
                    "output_file": "route_map.html"
                },
                "reasoning": "The user asked to see a visual map of the route with places and features."
            }
        ]
    },
    
    "answer": {
        "description": "Provide a natural language answer using memory and reasoning.",
        "parameters": {
            "text": {
                "type": "string",
                "description": "The answer text to provide to the user."
            }
        },
        "required": ["text"],
        "examples": [
            {
                "tool": "answer",
                "tool_input": {
                    "text": "Based on the route, Springfield, IL is approximately halfway along the way."
                },
                "reasoning": "The user asked for a clarification based on already known information."
            }
        ]
    }
}


# Mock tool specifications for testing
MOCK_TOOL_SPECS: Dict[str, Dict[str, Any]] = {
    "mock_tool": {
        "description": "A mock tool for testing purposes.",
        "parameters": {
            "param1": {
                "type": "string",
                "description": "A string parameter."
            },
            "param2": {
                "type": "integer",
                "description": "An integer parameter."
            }
        },
        "required": ["param1"],
        "examples": [
            {
                "tool": "mock_tool",
                "tool_input": {
                    "param1": "test",
                    "param2": 42
                },
                "reasoning": "This is a test."
            }
        ]
    },
    
    "answer": {
        "description": "Provide a natural language answer.",
        "parameters": {
            "text": {
                "type": "string",
                "description": "The answer text to provide to the user."
            }
        },
        "required": ["text"],
        "examples": [
            {
                "tool": "answer",
                "tool_input": {
                    "text": "This is a test answer."
                },
                "reasoning": "The user asked a question."
            }
        ]
    }
}
