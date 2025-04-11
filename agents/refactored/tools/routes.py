"""
Route-related tools for the agent framework.

This module provides tools for working with routes, such as getting directions
and sampling points along a route.
"""
from typing import Dict, List, Any, Tuple, Optional, Union
import json

from agents.refactored.clients.google_maps import GoogleMapsClient
from agents.refactored.utils.geo import sample_polyline
from agents.refactored.utils.validation import validate_coordinates
from agents.refactored.core.tool_executor import tool


@tool(
    name="get_route",
    description="Calculate a new driving route between a given origin and destination, possibly with waypoints.",
    schema={
        "type": "object",
        "properties": {
            "origin": {
                "type": "array",
                "description": "The [latitude, longitude] of the starting point, or a string like 'City, State'"
            },
            "destination": {
                "type": "array",
                "description": "The [latitude, longitude] of the destination, or a string like 'City, State'"
            },
            "waypoints": {
                "type": "array",
                "description": "Optional list of [latitude, longitude] tuples as intermediate stops"
            },
            "travel_mode": {
                "type": "string",
                "description": "Travel mode (DRIVE, BICYCLE, WALK, TWO_WHEELER)"
            },
            "avoid_tolls": {
                "type": "boolean",
                "description": "Whether to avoid tolls"
            }
        },
        "required": ["origin", "destination"]
    }
)
def get_route(
    origin: Union[List[float], str],
    destination: Union[List[float], str],
    waypoints: Optional[List[List[float]]] = None,
    travel_mode: str = "DRIVE",
    avoid_tolls: bool = False
) -> Dict[str, Any]:
    """
    Calculate a new driving route between a given origin and destination.
    
    Args:
        origin: The [latitude, longitude] of the starting point, or a string like 'City, State'
        destination: The [latitude, longitude] of the destination, or a string like 'City, State'
        waypoints: Optional list of [latitude, longitude] tuples as intermediate stops
        travel_mode: Travel mode (DRIVE, BICYCLE, WALK, TWO_WHEELER)
        avoid_tolls: Whether to avoid tolls
        
    Returns:
        A dictionary containing route information
    """
    # Handle string locations (e.g., "San Francisco, CA")
    # For simplicity, we'll use a mock geocoding function
    # In a real implementation, you would use a geocoding service
    def geocode_location(location):
        if isinstance(location, str):
            # This is a very simple mock geocoding function
            # In a real implementation, you would use a geocoding service
            if "champaign" in location.lower():
                return (40.1164, -88.2434)
            elif "west lafayette" in location.lower():
                return (40.4259, -86.9081)
            elif "san francisco" in location.lower():
                return (37.7749, -122.4194)
            elif "los angeles" in location.lower():
                return (34.0522, -118.2437)
            else:
                # Default to a random location if we don't recognize the place
                return (0.0, 0.0)
        return location
    
    # Geocode locations if they are strings
    origin = geocode_location(origin)
    destination = geocode_location(destination)
    
    # Validate coordinates
    origin_coords = validate_coordinates(origin)
    destination_coords = validate_coordinates(destination)
    
    waypoint_coords = None
    if waypoints:
        waypoint_coords = [validate_coordinates(wp) for wp in waypoints]
    
    # Get route from Google Maps API
    client = GoogleMapsClient()
    route_data = client.get_route(
        origin=origin_coords,
        destination=destination_coords,
        waypoints=waypoint_coords,
        travel_mode=travel_mode,
        avoid_tolls=avoid_tolls
    )
    
    return route_data


@tool(
    name="sample_polyline",
    description="Reduce the number of lat/lon points along a route to simplify later processing."
)
def sample_polyline_tool(
    encoded_polyline: str,
    method: str = "interval",
    interval_km: float = 5.0,
    every_nth: int = 10
) -> List[Tuple[float, float]]:
    """
    Sample points from an encoded polyline to reduce the number of points.
    
    Args:
        encoded_polyline: The encoded polyline string from Google Maps
        method: Sampling method: "interval" for distance-based or "nth" for index-based
        interval_km: Distance interval in kilometers between samples (if method is "interval")
        every_nth: Take every nth point (if method is "nth")
        
    Returns:
        A list of sampled (latitude, longitude) tuples
    """
    # Validate method
    if method not in ["interval", "nth"]:
        raise ValueError("Method must be 'interval' or 'nth'.")
    
    # Sample the polyline
    sampled_points = sample_polyline(
        encoded_polyline=encoded_polyline,
        method=method,
        interval_km=interval_km,
        every_nth=every_nth
    )
    
    return sampled_points


@tool(
    name="save_route_data",
    description="Save route data to JSON files for later use."
)
def save_route_data(
    polyline_coords: List[Tuple[float, float]],
    polyline: Optional[str] = None,
    places: Optional[List[Dict[str, Any]]] = None,
    features: Optional[List[Dict[str, Any]]] = None,
    polyline_file: str = "polyline_route.json",
    places_file: str = "places_along_route.json",
    features_file: str = "natural_features_along_route.json"
) -> Dict[str, str]:
    """
    Save route data to JSON files for later use.
    
    Args:
        polyline_coords: List of (lat, lon) tuples representing the route
        polyline: Optional encoded polyline string
        places: Optional list of place dictionaries
        features: Optional list of feature dictionaries
        polyline_file: Output file for polyline coordinates
        places_file: Output file for places data
        features_file: Output file for features data
        
    Returns:
        A dictionary of file paths that were saved
    """
    saved_files = {}
    
    # Save polyline coordinates
    with open(polyline_file, "w") as f:
        json.dump(polyline_coords, f, indent=2)
    saved_files["polyline_file"] = polyline_file
    
    # Save places if provided
    if places:
        with open(places_file, "w") as f:
            json.dump(places, f, indent=2)
        saved_files["places_file"] = places_file
    
    # Save features if provided
    if features:
        with open(features_file, "w") as f:
            json.dump(features, f, indent=2)
        saved_files["features_file"] = features_file
    
    return saved_files
