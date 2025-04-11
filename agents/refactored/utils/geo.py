"""
Geospatial utilities for the agent framework.

This module provides utility functions for working with geospatial data.
"""
from typing import List, Tuple, Optional
from geopy.distance import geodesic
import polyline


def decode_polyline(encoded_polyline: str) -> List[Tuple[float, float]]:
    """
    Decode a Google Maps encoded polyline string into a list of coordinates.
    
    Args:
        encoded_polyline: The encoded polyline string
        
    Returns:
        A list of (latitude, longitude) tuples
    """
    return polyline.decode(encoded_polyline)


def encode_polyline(coords: List[Tuple[float, float]]) -> str:
    """
    Encode a list of coordinates into a Google Maps polyline string.
    
    Args:
        coords: A list of (latitude, longitude) tuples
        
    Returns:
        The encoded polyline string
    """
    return polyline.encode(coords)


def sample_polyline_by_distance(
    coords: List[Tuple[float, float]], 
    interval_km: float = 5.0
) -> List[Tuple[float, float]]:
    """
    Sample points from a polyline at regular distance intervals.
    
    Args:
        coords: A list of (latitude, longitude) tuples
        interval_km: Distance interval in kilometers between samples
        
    Returns:
        A list of sampled (latitude, longitude) tuples
    """
    if not coords:
        return []
    
    sampled = [coords[0]]
    last_point = coords[0]
    
    for point in coords[1:]:
        if geodesic(last_point, point).km >= interval_km:
            sampled.append(point)
            last_point = point
    
    # Always include the last point if it's not already included
    if sampled[-1] != coords[-1]:
        sampled.append(coords[-1])
    
    return sampled


def sample_polyline_by_index(
    coords: List[Tuple[float, float]], 
    every_nth: int = 10
) -> List[Tuple[float, float]]:
    """
    Sample points from a polyline by taking every nth point.
    
    Args:
        coords: A list of (latitude, longitude) tuples
        every_nth: Take every nth point
        
    Returns:
        A list of sampled (latitude, longitude) tuples
    """
    if not coords:
        return []
    
    # Always include the first and last points
    if len(coords) <= every_nth:
        return [coords[0], coords[-1]] if len(coords) > 1 else coords
    
    sampled = coords[::every_nth]
    
    # Add the last point if it's not already included
    if sampled[-1] != coords[-1]:
        sampled.append(coords[-1])
    
    return sampled


def sample_polyline(
    encoded_polyline: str, 
    method: str = "interval", 
    interval_km: float = 5.0, 
    every_nth: int = 10
) -> List[Tuple[float, float]]:
    """
    Sample points from an encoded polyline using the specified method.
    
    Args:
        encoded_polyline: The encoded polyline string
        method: Sampling method: "interval" for distance-based or "nth" for index-based
        interval_km: Distance interval in kilometers between samples (if method is "interval")
        every_nth: Take every nth point (if method is "nth")
        
    Returns:
        A list of sampled (latitude, longitude) tuples
        
    Raises:
        ValueError: If an invalid method is specified
    """
    coords = decode_polyline(encoded_polyline)
    
    if method == "interval":
        return sample_polyline_by_distance(coords, interval_km)
    elif method == "nth":
        return sample_polyline_by_index(coords, every_nth)
    else:
        raise ValueError("Unsupported sampling method. Use 'interval' or 'nth'.")


def calculate_distance(
    point1: Tuple[float, float], 
    point2: Tuple[float, float]
) -> float:
    """
    Calculate the distance between two points in kilometers.
    
    Args:
        point1: (latitude, longitude) of the first point
        point2: (latitude, longitude) of the second point
        
    Returns:
        Distance in kilometers
    """
    return geodesic(point1, point2).km


def calculate_route_length(coords: List[Tuple[float, float]]) -> float:
    """
    Calculate the total length of a route in kilometers.
    
    Args:
        coords: A list of (latitude, longitude) tuples
        
    Returns:
        Total length in kilometers
    """
    if len(coords) < 2:
        return 0.0
    
    total_distance = 0.0
    for i in range(len(coords) - 1):
        total_distance += calculate_distance(coords[i], coords[i + 1])
    
    return total_distance


def find_nearest_point(
    target: Tuple[float, float], 
    points: List[Tuple[float, float]]
) -> Optional[Tuple[float, float]]:
    """
    Find the nearest point to a target from a list of points.
    
    Args:
        target: (latitude, longitude) of the target point
        points: A list of (latitude, longitude) tuples
        
    Returns:
        The nearest point, or None if the list is empty
    """
    if not points:
        return None
    
    nearest_point = min(points, key=lambda p: calculate_distance(target, p))
    return nearest_point


def find_nearest_point_with_index(
    target: Tuple[float, float], 
    points: List[Tuple[float, float]]
) -> Tuple[Optional[Tuple[float, float]], Optional[int]]:
    """
    Find the nearest point to a target from a list of points, along with its index.
    
    Args:
        target: (latitude, longitude) of the target point
        points: A list of (latitude, longitude) tuples
        
    Returns:
        A tuple containing the nearest point and its index, or (None, None) if the list is empty
    """
    if not points:
        return None, None
    
    distances = [calculate_distance(target, p) for p in points]
    min_index = distances.index(min(distances))
    return points[min_index], min_index
