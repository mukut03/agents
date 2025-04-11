"""
Visualization utilities for the agent framework.

This module provides utility functions for visualizing geospatial data.
"""
from typing import Dict, List, Any, Optional, Tuple
import json
import folium


def render_route_map(
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
    # Define color mapping for different place and feature types
    place_colors = {
        "city": "red",
        "town": "orange",
        "village": "yellow",
        "hamlet": "beige",
        "suburb": "pink",
        "neighbourhood": "purple"
    }
    
    natural_colors = {
        "river": "blue",
        "stream": "lightblue",
        "lake": "blue",
        "water": "blue",
        "peak": "purple",
        "wood": "green",
        "forest": "darkgreen",
        "beach": "beige",
        "cliff": "gray",
        "valley": "gray",
        "scrub": "green",
        "wetland": "teal",
    }
    
    # Center map on the first point or a default location
    center = polyline_coords[0] if polyline_coords else (0, 0)
    m = folium.Map(location=center, zoom_start=7)
    
    # Add the route as a polyline
    if polyline_coords:
        folium.PolyLine(
            locations=polyline_coords,
            color="black",
            weight=4,
            opacity=0.8
        ).add_to(m)
    
    # Load places from file if provided
    if places_path and not places:
        try:
            with open(places_path, "r") as f:
                places = json.load(f)
        except Exception as e:
            print(f"Error loading places from {places_path}: {e}")
    
    # Add place markers
    if places:
        for place in places:
            name = place.get("name", "Unknown")
            place_type = place.get("type", "unknown")
            lat = place.get("lat")
            lon = place.get("lon")
            
            if lat is not None and lon is not None:
                color = place_colors.get(place_type, "gray")
                folium.CircleMarker(
                    location=(lat, lon),
                    radius=6,
                    color=color,
                    fill=True,
                    fill_opacity=0.9,
                    popup=f"{name} ({place_type})"
                ).add_to(m)
    
    # Load features from file if provided
    if features_path and not features:
        try:
            with open(features_path, "r") as f:
                features = json.load(f)
        except Exception as e:
            print(f"Error loading features from {features_path}: {e}")
    
    # Add feature markers
    if features:
        for feature in features:
            name = feature.get("name", "Unnamed")
            feature_type = feature.get("type", "unknown")
            lat = feature.get("lat")
            lon = feature.get("lon")
            
            if lat is not None and lon is not None:
                color = natural_colors.get(feature_type, "gray")
                folium.CircleMarker(
                    location=(lat, lon),
                    radius=5,
                    color=color,
                    fill=True,
                    fill_opacity=0.7,
                    popup=f"{name} ({feature_type})"
                ).add_to(m)
    
    # Save map to file
    m.save(output_file)
    return output_file


def render_points_map(
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
    if not points:
        # Create an empty map centered at a default location
        m = folium.Map(location=(0, 0), zoom_start=2)
    else:
        # Initialize a map centered around the first point
        m = folium.Map(location=points[0], zoom_start=10)
        
        # Add markers for each point
        for lat, lon in points:
            folium.Marker([lat, lon]).add_to(m)
    
    # Save the map to an HTML file
    m.save(output_file)
    return output_file


def save_to_json(data: Any, output_file: str) -> str:
    """
    Save data to a JSON file.
    
    Args:
        data: The data to save
        output_file: Output JSON file path
        
    Returns:
        The path to the generated JSON file
    """
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)
    return output_file
