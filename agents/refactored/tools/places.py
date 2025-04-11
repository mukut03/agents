"""
Place-related tools for the agent framework.

This module provides tools for working with places and natural features along a route.
"""
from typing import Dict, List, Any, Tuple, Optional, Union
import json

from agents.refactored.clients.overpass import OverpassClient
from agents.refactored.utils.validation import validate_coordinates
from agents.refactored.core.tool_executor import tool


@tool(
    name="get_places",
    description="Find towns and cities along the route using lat/lon points.",
    schema={
        "type": "object",
        "properties": {
            "polyline_coords": {
                "type": "array",
                "description": "List of [latitude, longitude] tuples representing the route"
            },
            "radius_m": {
                "type": "integer",
                "description": "Search radius in meters around each point"
            },
            "method": {
                "type": "string",
                "description": "'node' for per-point buffer or 'way' for polyline query"
            }
        },
        "required": ["polyline_coords"]
    }
)
def get_places(
    polyline_coords: List[Tuple[float, float]],
    radius_m: int = 3000,
    method: str = "node"
) -> List[Dict[str, Any]]:
    """
    Find towns and cities along the route.
    
    Args:
        polyline_coords: List of (lat, lon) tuples representing the route
        radius_m: Search radius in meters around each point
        method: 'node' for per-point buffer or 'way' for polyline query
        
    Returns:
        A list of place dictionaries with name, type, lat, lon
    """
    # Validate method
    if method not in ["node", "way"]:
        raise ValueError("Method must be 'node' or 'way'.")
    
    # Validate coordinates
    validated_coords = [validate_coordinates(coord) for coord in polyline_coords]
    
    # Query places using Overpass API
    client = OverpassClient()
    places = client.get_places_along_polyline(
        polyline_coords=validated_coords,
        radius_m=radius_m,
        method=method
    )
    
    # Sort places by type (city, town, village) and name
    def place_sort_key(place):
        # Define type priority (city > town > village > other)
        type_priority = {
            "city": 0,
            "town": 1,
            "village": 2,
            "hamlet": 3,
            "suburb": 4,
            "neighbourhood": 5
        }
        return (type_priority.get(place.get("type", ""), 99), place.get("name", ""))
    
    places.sort(key=place_sort_key)
    
    return places


@tool(
    name="get_natural_features",
    description="Find natural landmarks like rivers, parks, and forests along the route.",
    schema={
        "type": "object",
        "properties": {
            "polyline_coords": {
                "type": "array",
                "description": "List of [latitude, longitude] tuples representing the route"
            },
            "radius_m": {
                "type": "integer",
                "description": "Search radius in meters around each point"
            },
            "method": {
                "type": "string",
                "description": "'node' for per-point buffer or 'way' for polyline query"
            }
        },
        "required": ["polyline_coords"]
    }
)
def get_natural_features(
    polyline_coords: List[Tuple[float, float]],
    radius_m: int = 2000,
    method: str = "way"
) -> List[Dict[str, Any]]:
    """
    Find natural features along the route.
    
    Args:
        polyline_coords: List of (lat, lon) tuples representing the route
        radius_m: Search radius in meters around each point
        method: 'node' for per-point buffer or 'way' for polyline query
        
    Returns:
        A list of feature dictionaries with name, type, lat, lon
    """
    # Validate method
    if method not in ["node", "way"]:
        raise ValueError("Method must be 'node' or 'way'.")
    
    # Validate coordinates
    validated_coords = [validate_coordinates(coord) for coord in polyline_coords]
    
    # Query natural features using Overpass API
    client = OverpassClient()
    features = client.get_natural_features_along_polyline(
        polyline_coords=validated_coords,
        radius_m=radius_m,
        method=method
    )
    
    # Sort features by type and name
    def feature_sort_key(feature):
        # Define type priority
        type_priority = {
            "water": 0,
            "river": 1,
            "lake": 2,
            "peak": 3,
            "wood": 4,
            "forest": 5,
            "beach": 6,
            "cliff": 7,
            "valley": 8,
            "stream": 9
        }
        return (type_priority.get(feature.get("type", ""), 99), feature.get("name", ""))
    
    features.sort(key=feature_sort_key)
    
    return features


@tool(
    name="filter_places",
    description="Filter places by type, name, or other criteria."
)
def filter_places(
    places: List[Dict[str, Any]],
    types: Optional[List[str]] = None,
    name_contains: Optional[str] = None,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Filter places by type, name, or other criteria.
    
    Args:
        places: List of place dictionaries
        types: Optional list of place types to include (e.g., ["city", "town"])
        name_contains: Optional string to filter place names
        limit: Optional maximum number of places to return
        
    Returns:
        A filtered list of place dictionaries
    """
    filtered_places = places
    
    # Filter by type
    if types:
        filtered_places = [p for p in filtered_places if p.get("type") in types]
    
    # Filter by name
    if name_contains:
        name_lower = name_contains.lower()
        filtered_places = [p for p in filtered_places if name_lower in p.get("name", "").lower()]
    
    # Apply limit
    if limit is not None and limit > 0:
        filtered_places = filtered_places[:limit]
    
    return filtered_places


@tool(
    name="filter_features",
    description="Filter natural features by type, name, or other criteria."
)
def filter_features(
    features: List[Dict[str, Any]],
    types: Optional[List[str]] = None,
    name_contains: Optional[str] = None,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Filter natural features by type, name, or other criteria.
    
    Args:
        features: List of feature dictionaries
        types: Optional list of feature types to include (e.g., ["river", "lake"])
        name_contains: Optional string to filter feature names
        limit: Optional maximum number of features to return
        
    Returns:
        A filtered list of feature dictionaries
    """
    filtered_features = features
    
    # Filter by type
    if types:
        filtered_features = [f for f in filtered_features if f.get("type") in types]
    
    # Filter by name
    if name_contains:
        name_lower = name_contains.lower()
        filtered_features = [f for f in filtered_features if name_lower in f.get("name", "").lower()]
    
    # Apply limit
    if limit is not None and limit > 0:
        filtered_features = filtered_features[:limit]
    
    return filtered_features
