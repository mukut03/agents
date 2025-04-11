"""
Google Maps API client for the agent framework.

This module provides a client for interacting with the Google Maps API.
"""
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta

from google.maps import routing_v2
from google.maps.routing_v2.types import (
    ComputeRoutesRequest,
    Waypoint,
    Location,
    RouteTravelMode,
    RoutingPreference,
    PolylineQuality,
    RouteModifiers
)
from google.protobuf.timestamp_pb2 import Timestamp
import polyline

from agents.refactored.core.errors import APIError


class GoogleMapsClient:
    """Client for interacting with the Google Maps API."""
    
    def __init__(self):
        """Initialize the Google Maps client."""
        self.routing_client = routing_v2.RoutesClient()
    
    def create_waypoint(self, lat: float, lng: float) -> Waypoint:
        """
        Create a Google Maps Waypoint object from latitude and longitude.
        
        Args:
            lat: Latitude of the location
            lng: Longitude of the location
            
        Returns:
            A Google Maps Waypoint object
        """
        return Waypoint(location=Location(lat_lng={"latitude": lat, "longitude": lng}))
    
    def get_route(
        self, 
        origin: Tuple[float, float], 
        destination: Tuple[float, float], 
        waypoints: Optional[List[Tuple[float, float]]] = None,
        travel_mode: str = "DRIVE",
        avoid_tolls: bool = False,
        high_quality_polyline: bool = True
    ) -> Dict[str, Any]:
        """
        Get a route from the Google Maps Routes API.
        
        Args:
            origin: (latitude, longitude) of the starting point
            destination: (latitude, longitude) of the destination
            waypoints: Optional list of (latitude, longitude) tuples as intermediate stops
            travel_mode: Travel mode (DRIVE, BICYCLE, WALK, etc.)
            avoid_tolls: Whether to avoid tolls
            high_quality_polyline: Whether to request a high-quality polyline
            
        Returns:
            A dictionary containing route information
            
        Raises:
            APIError: If the API request fails
        """
        try:
            # Create waypoints
            origin_wp = self.create_waypoint(*origin)
            destination_wp = self.create_waypoint(*destination)
            intermediate_wps = [self.create_waypoint(*wp) for wp in (waypoints or [])]
            
            # Set departure time to 5 minutes from now
            departure_time = Timestamp()
            departure_time.FromDatetime(datetime.utcnow() + timedelta(minutes=5))
            
            # Map travel mode string to enum
            travel_mode_map = {
                "DRIVE": RouteTravelMode.DRIVE,
                "BICYCLE": RouteTravelMode.BICYCLE,
                "WALK": RouteTravelMode.WALK,
                "TWO_WHEELER": RouteTravelMode.TWO_WHEELER
            }
            route_travel_mode = travel_mode_map.get(travel_mode, RouteTravelMode.DRIVE)
            
            # Create request
            request = ComputeRoutesRequest(
                origin=origin_wp,
                destination=destination_wp,
                intermediates=intermediate_wps,
                travel_mode=route_travel_mode,
                routing_preference=RoutingPreference.TRAFFIC_AWARE,
                polyline_quality=(
                    PolylineQuality.HIGH_QUALITY if high_quality_polyline 
                    else PolylineQuality.OVERVIEW
                ),
                departure_time=departure_time,
                route_modifiers=RouteModifiers(avoid_tolls=avoid_tolls)
            )
            
            # Set field mask to limit response size
            field_mask = 'routes.distanceMeters,routes.duration,routes.polyline.encodedPolyline'
            metadata = [('x-goog-fieldmask', field_mask)]
            
            # Send request
            response = self.routing_client.compute_routes(request=request, metadata=metadata)
            
            if not response.routes:
                return {"error": "No route found."}
            
            # Process response
            route = response.routes[0]
            encoded_polyline = route.polyline.encoded_polyline
            decoded_coords = polyline.decode(encoded_polyline)
            
            # Format distance and duration
            distance_km = route.distance_meters / 1000
            duration_minutes = route.duration.seconds / 60
            
            return {
                "polyline": encoded_polyline,
                "polyline_coords": decoded_coords,
                "distance_meters": route.distance_meters,
                "distance_text": f"{distance_km:.1f} km",
                "duration_seconds": route.duration.seconds,
                "duration_text": f"{duration_minutes:.0f} minutes"
            }
        except Exception as e:
            raise APIError("google_maps", f"Failed to get route: {str(e)}")
