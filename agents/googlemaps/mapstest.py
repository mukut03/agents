import os
from google.auth import credentials
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
from google.protobuf.field_mask_pb2 import FieldMask
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.json_format import MessageToJson
from datetime import datetime, timedelta

# Initialize the Routes client
client = routing_v2.RoutesClient()

def create_waypoint(lat, lng):
    """Helper function to create a Waypoint."""
    return Waypoint(location=Location(lat_lng={"latitude": lat, "longitude": lng}))

import json

def main():
    # Define origin and destination coordinates
    origin = create_waypoint(37.7749, -122.4194)  # San Francisco, CA
    destination = create_waypoint(34.0522, -118.2437)  # Los Angeles, CA

    # Optional: Define intermediate waypoints
    intermediates = [
        create_waypoint(36.1627, -86.7816)  # Nashville, TN
    ]

    # Set departure time to now
    departure_time = Timestamp()
    departure_time.FromDatetime(datetime.utcnow() + timedelta(minutes=5))

    

    # Create the ComputeRoutesRequest
    request = ComputeRoutesRequest(
        origin=origin,
        destination=destination,
        intermediates=intermediates,
        travel_mode=RouteTravelMode.DRIVE,
        routing_preference=RoutingPreference.TRAFFIC_AWARE,
        polyline_quality=PolylineQuality.HIGH_QUALITY,
        departure_time=departure_time,
        route_modifiers=RouteModifiers(avoid_tolls=False),
        
    )
    
    field_mask = 'routes.distanceMeters,routes.duration,routes.legs'
#     field_mask = (
#     'routes.duration,routes.distanceMeters,'
#     'routes.legs.steps.navigationInstruction,'
#     'routes.travelAdvisory.tollInfo,'
#     'routes.legs.travelAdvisory.tollInfo,'
#     'routes.travelAdvisory.speedReadingIntervals,'
#     'routes.routeLabels,'
#     'routes.legs.summary,'
#     'routes.legs.speedLimits,'
#     'routes.polyline.encodedPolyline'
# )
    #field_mask = '*'

    
    # Set the X-Goog-FieldMask header to '*' to retrieve all fields
    metadata = [('x-goog-fieldmask', field_mask)]

    # Execute the request
    response = client.compute_routes(request=request, metadata=metadata)

    response_json = MessageToJson(response._pb)

    # Define the output file path
    output_file_path = 'routes_response.json'

    # Write the JSON string to a file
    with open(output_file_path, 'w') as json_file:
        json_file.write(response_json)

    print(f"Response has been saved to {output_file_path}")
    
    # Process the response
    # if response.routes:
    #     with open("routes_response.json", "r") as file:
    #         response_json = json.load(file)
    #         process_route_response(response_json)
    #         #print(json.dumps(cleaned_data, indent=2))
    #         #print(cleaned_data)
    # else:
    #     print("No routes found.")

if __name__ == "__main__":
    main()
