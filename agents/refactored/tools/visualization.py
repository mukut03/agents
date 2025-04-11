"""
Visualization tools for the agent framework.

This module provides tools for visualizing geospatial data.
"""
from typing import Dict, List, Any, Tuple, Optional, Union
import json

from agents.refactored.utils.visualization import render_route_map, render_points_map, save_to_json
from agents.refactored.utils.validation import validate_coordinates
from agents.refactored.core.tool_executor import tool


@tool(
    name="render_map",
    description="Generate an HTML map showing the route and any available cities or landmarks.",
    schema={
        "type": "object",
        "properties": {
            "polyline_coords": {
                "type": "array",
                "description": "List of [latitude, longitude] tuples representing the route"
            },
            "places": {
                "type": "array",
                "description": "Optional list of place dictionaries"
            },
            "features": {
                "type": "array",
                "description": "Optional list of feature dictionaries"
            },
            "places_path": {
                "type": "string",
                "description": "Optional path to JSON file with places data"
            },
            "features_path": {
                "type": "string",
                "description": "Optional path to JSON file with features data"
            },
            "output_file": {
                "type": "string",
                "description": "Output HTML file path"
            }
        },
        "required": ["polyline_coords"]
    }
)
def render_map(
    polyline_coords: List[Tuple[float, float]],
    places: Optional[List[Dict[str, Any]]] = None,
    features: Optional[List[Dict[str, Any]]] = None,
    places_path: Optional[str] = None,
    features_path: Optional[str] = None,
    output_file: str = "route_map.html"
) -> str:
    """
    Render an interactive HTML map with the route, places, and natural features.
    
    Args:
        polyline_coords: List of (lat, lon) tuples representing the route
        places: Optional list of place dictionaries
        features: Optional list of feature dictionaries
        places_path: Optional path to JSON file with places data
        features_path: Optional path to JSON file with features data
        output_file: Output HTML file path
        
    Returns:
        The path to the generated HTML file
    """
    # Validate coordinates
    validated_coords = [validate_coordinates(coord) for coord in polyline_coords]
    
    # Render the map
    map_path = render_route_map(
        polyline_coords=validated_coords,
        places=places,
        features=features,
        places_path=places_path,
        features_path=features_path,
        output_file=output_file
    )
    
    return map_path


@tool(
    name="render_points_map",
    description="Render a simple map with markers for a list of points."
)
def render_points_map_tool(
    points: List[Tuple[float, float]],
    output_file: str = "points_map.html"
) -> str:
    """
    Render a simple map with markers for a list of points.
    
    Args:
        points: List of (lat, lon) tuples
        output_file: Output HTML file path
        
    Returns:
        The path to the generated HTML file
    """
    # Validate coordinates
    validated_points = [validate_coordinates(point) for point in points]
    
    # Render the map
    map_path = render_points_map(
        points=validated_points,
        output_file=output_file
    )
    
    return map_path


@tool(
    name="save_to_json",
    description="Save data to a JSON file."
)
def save_to_json_tool(
    data: Any,
    output_file: str
) -> str:
    """
    Save data to a JSON file.
    
    Args:
        data: The data to save
        output_file: Output JSON file path
        
    Returns:
        The path to the generated JSON file
    """
    # Save the data
    file_path = save_to_json(
        data=data,
        output_file=output_file
    )
    
    return file_path


@tool(
    name="generate_route_summary",
    description="Generate a summary of the route with places and features."
)
def generate_route_summary(
    origin: List[float],
    destination: List[float],
    distance_text: str,
    duration_text: str,
    places: Optional[List[Dict[str, Any]]] = None,
    features: Optional[List[Dict[str, Any]]] = None,
    max_places: int = 10,
    max_features: int = 10
) -> Dict[str, Any]:
    """
    Generate a summary of the route with places and features.
    
    Args:
        origin: The [latitude, longitude] of the starting point
        destination: The [latitude, longitude] of the destination
        distance_text: The distance text (e.g., "123.4 km")
        duration_text: The duration text (e.g., "2 hours 30 minutes")
        places: Optional list of place dictionaries
        features: Optional list of feature dictionaries
        max_places: Maximum number of places to include in the summary
        max_features: Maximum number of features to include in the summary
        
    Returns:
        A dictionary containing the route summary
    """
    # Validate coordinates
    origin_coords = validate_coordinates(origin)
    destination_coords = validate_coordinates(destination)
    
    # Filter places by type
    cities = []
    towns = []
    villages = []
    
    if places:
        for place in places:
            place_type = place.get("type")
            if place_type == "city":
                cities.append(place)
            elif place_type == "town":
                towns.append(place)
            elif place_type == "village":
                villages.append(place)
    
    # Filter features by type
    water_features = []
    mountain_features = []
    forest_features = []
    other_features = []
    
    if features:
        for feature in features:
            feature_type = feature.get("type")
            if feature_type in ["water", "river", "lake", "stream"]:
                water_features.append(feature)
            elif feature_type in ["peak", "mountain"]:
                mountain_features.append(feature)
            elif feature_type in ["wood", "forest"]:
                forest_features.append(feature)
            else:
                other_features.append(feature)
    
    # Build the summary
    summary = {
        "origin": {
            "lat": origin_coords[0],
            "lon": origin_coords[1]
        },
        "destination": {
            "lat": destination_coords[0],
            "lon": destination_coords[1]
        },
        "distance": distance_text,
        "duration": duration_text,
        "places": {
            "cities": cities[:max_places],
            "towns": towns[:max_places],
            "villages": villages[:max_places],
            "total_count": len(cities) + len(towns) + len(villages)
        },
        "features": {
            "water": water_features[:max_features],
            "mountains": mountain_features[:max_features],
            "forests": forest_features[:max_features],
            "other": other_features[:max_features],
            "total_count": len(water_features) + len(mountain_features) + len(forest_features) + len(other_features)
        }
    }
    
    return summary
