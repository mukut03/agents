"""
Overpass API client for the agent framework.

This module provides a client for interacting with the Overpass API to query
OpenStreetMap data for places and natural features along a route.
"""
from typing import Dict, List, Any, Optional, Tuple, Set
import requests

from agents.refactored.core.errors import APIError


class OverpassClient:
    """Client for interacting with the Overpass API."""
    
    def __init__(self, api_url: str = "http://overpass-api.de/api/interpreter"):
        """
        Initialize the Overpass client.
        
        Args:
            api_url: The URL of the Overpass API
        """
        self.api_url = api_url
    
    def execute_query(self, query: str) -> Dict[str, Any]:
        """
        Execute an Overpass QL query.
        
        Args:
            query: The Overpass QL query
            
        Returns:
            The response from the API
            
        Raises:
            APIError: If the API request fails
        """
        try:
            response = requests.post(self.api_url, data={"data": query})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise APIError(
                "overpass", 
                f"Failed to execute Overpass query: {str(e)}",
                status_code=getattr(e.response, "status_code", None),
                response_body=getattr(e.response, "text", None)
            )
    
    def get_places_along_polyline(
        self, 
        polyline_coords: List[Tuple[float, float]], 
        radius_m: int = 2000, 
        method: str = "node"
    ) -> List[Dict[str, Any]]:
        """
        Query places (cities, towns, villages) along a polyline.
        
        Args:
            polyline_coords: List of (lat, lon) tuples representing the route
            radius_m: Search radius in meters
            method: 'node' for per-point buffer or 'way' for polyline query
            
        Returns:
            List of place dictionaries with name, type, lat, lon
            
        Raises:
            APIError: If the API request fails
            ValueError: If an invalid method is specified
        """
        if not polyline_coords:
            return []
        
        try:
            # Build the query based on the method
            if method == "way":
                # Format polyline for Overpass
                poly_string = " ".join([f"{lat} {lon}" for lat, lon in polyline_coords])
                query = f"""
                [out:json][timeout:60];
                way(poly:"{poly_string}")->.route;
                node["place"~"city|town|village"](around.route:{radius_m});
                out center;
                """
            elif method == "node":
                # Query around each point
                query = "[out:json][timeout:60];(\n"
                for lat, lon in polyline_coords:
                    query += f'  node(around:{radius_m},{lat},{lon})["place"~"city|town|village"];\n'
                query += ");out center;"
            else:
                raise ValueError("Method must be 'way' or 'node'.")
            
            # Execute the query
            response = self.execute_query(query)
            
            # Process the results
            elements = response.get("elements", [])
            seen: Set[Tuple[str, str]] = set()
            places = []
            
            for elem in elements:
                tags = elem.get("tags", {})
                name = tags.get("name")
                place_type = tags.get("place")
                lat = elem.get("lat")
                lon = elem.get("lon")
                
                if name and place_type and lat and lon and (name, place_type) not in seen:
                    places.append({
                        "name": name,
                        "type": place_type,
                        "lat": lat,
                        "lon": lon
                    })
                    seen.add((name, place_type))
            
            return places
        except ValueError as e:
            # Re-raise ValueError
            raise e
        except Exception as e:
            raise APIError("overpass", f"Failed to get places along polyline: {str(e)}")
    
    def get_natural_features_along_polyline(
        self, 
        polyline_coords: List[Tuple[float, float]], 
        radius_m: int = 2000, 
        method: str = "way"
    ) -> List[Dict[str, Any]]:
        """
        Query natural features (rivers, lakes, mountains, etc.) along a polyline.
        
        Args:
            polyline_coords: List of (lat, lon) tuples representing the route
            radius_m: Search radius in meters
            method: 'node' for per-point buffer or 'way' for polyline query
            
        Returns:
            List of feature dictionaries with name, type, lat, lon
            
        Raises:
            APIError: If the API request fails
            ValueError: If an invalid method is specified
        """
        if not polyline_coords:
            return []
        
        try:
            # Build the query based on the method
            if method == "way":
                # Format polyline for Overpass
                poly_string = " ".join([f"{lat} {lon}" for lat, lon in polyline_coords])
                query = f"""
                [out:json][timeout:60];
                way(poly:"{poly_string}")->.route;
                (
                  node(around.route:{radius_m})["natural"~"water|peak|wood|beach|cliff|valley|scrub|wetland"];
                  way(around.route:{radius_m})["natural"~"water|peak|wood|beach|cliff|valley|scrub|wetland"];
                  node(around.route:{radius_m})["waterway"~"river|stream"];
                  way(around.route:{radius_m})["waterway"~"river|stream"];
                );
                out center;
                """
            elif method == "node":
                # Query around each point
                query = "[out:json][timeout:60];(\n"
                for lat, lon in polyline_coords:
                    query += f"""
                    node(around:{radius_m},{lat},{lon})["natural"~"water|peak|wood|beach|cliff|valley|scrub|wetland"];
                    way(around:{radius_m},{lat},{lon})["natural"~"water|peak|wood|beach|cliff|valley|scrub|wetland"];
                    node(around:{radius_m},{lat},{lon})["waterway"~"river|stream"];
                    way(around:{radius_m},{lat},{lon})["waterway"~"river|stream"];
                    """
                query += ");out center;"
            else:
                raise ValueError("Method must be 'way' or 'node'.")
            
            # Execute the query
            response = self.execute_query(query)
            
            # Process the results
            elements = response.get("elements", [])
            seen: Set[Tuple[Optional[str], str]] = set()
            features = []
            
            for elem in elements:
                tags = elem.get("tags", {})
                name = tags.get("name")
                nat_type = tags.get("natural") or tags.get("waterway")
                
                # Get coordinates (different for nodes and ways)
                if "lat" in elem and "lon" in elem:
                    lat = elem.get("lat")
                    lon = elem.get("lon")
                elif "center" in elem:
                    center = elem.get("center", {})
                    lat = center.get("lat")
                    lon = center.get("lon")
                else:
                    continue
                
                if nat_type and lat and lon and (name, nat_type) not in seen:
                    features.append({
                        "name": name or "unnamed",
                        "type": nat_type,
                        "lat": lat,
                        "lon": lon
                    })
                    seen.add((name, nat_type))
            
            return features
        except ValueError as e:
            # Re-raise ValueError
            raise e
        except Exception as e:
            raise APIError("overpass", f"Failed to get natural features along polyline: {str(e)}")
