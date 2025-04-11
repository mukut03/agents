AGENT_BEHAVIOR_SPEC = {
    "get_route": {
        "description": "Calculate a new driving route between a given origin and destination, possibly with waypoints.",
        "use_cases": [
            "How do I get from A to B?",
            "Give me driving directions from San Francisco to LA"
        ],
        "action_example": {
            "tool": "get_route",
            "tool_input": {
                "origin": [37.7749, -122.4194],
                "destination": [34.0522, -118.2437]
            },
            "reasoning": "The user wants directions between two cities."
        },
        "summarize": lambda r: f"The trip is approximately {r.get('duration_text')} long and covers {r.get('distance_text')}."
    },

    "sample_polyline": {
        "description": "Reduce the number of lat/lon points along a route to simplify later processing. Not used for direct conversation.",
        "use_cases": [
            "Pre-process the route for other tools",
            "Downsample coordinates before finding cities or landmarks"
        ],
        "action_example": {
            "tool": "sample_polyline",
            "tool_input": {
                "encoded_polyline": "abc123...",
                "method": "nth",
                "every_nth": 10
            },
            "reasoning": "Reduce route points to simplify place lookup."
        },
        "summarize": lambda r: f"Polyline sampled to {len(r)} points." if isinstance(r, list) else "Sampled route."
    },

    "get_places": {
        "description": "Find towns and cities along the route using lat/lon points.",
        "use_cases": [
            "Which towns do we pass?",
            "What cities are on the way?"
        ],
        "action_example": {
            "tool": "get_places",
            "tool_input": {
                "polyline_coords": [[37.7, -122.4], [36.7, -121.8]]
            },
            "reasoning": "The user wants to know which towns are along the route."
        },
        "summarize": lambda r: f"Found {len(r)} towns and cities along the route." if isinstance(r, list) else "Place info retrieved."
    },

    "get_natural_features": {
        "description": "Find natural landmarks like rivers, parks, and forests along the route.",
        "use_cases": [
            "Do we pass any rivers or mountains?",
            "What natural features are along the way?"
        ],
        "action_example": {
            "tool": "get_natural_features",
            "tool_input": {
                "polyline_coords": [[37.7, -122.4], [36.7, -121.8]]
            },
            "reasoning": "The user asked about natural landmarks along the route."
        },
        "summarize": lambda r: f"Found {len(r)} natural features along the route." if isinstance(r, list) else "Natural feature info retrieved."
    },

    "render_map": {
        "description": "Generate an HTML map showing the route and any available cities or landmarks.",
        "use_cases": [
            "Can you show me the map?",
            "Render the route"
        ],
        "action_example": {
            "tool": "render_map",
            "tool_input": {
                "polyline_coords": [[37.7, -122.4], [36.7, -121.8]]
            },
            "reasoning": "The user asked to see a visual map."
        },
        "summarize": lambda r: "Map rendered to HTML."
    },

    "answer": {
        "description": "Summarize or clarify based on what the agent already knows. Used for follow-up or reflection.",
        "use_cases": [
            "What does that convert to in miles?",
            "Which place is closest to the start?",
            "Can you summarize the features we found?"
        ],
        "action_example": {
            "tool": "answer",
            "tool_input": {
                "text": "Sure, 289 minutes is about 4.8 hours and 427.2 km is roughly 265 miles."
            },
            "reasoning": "The user asked for a clarification based on already known information."
        },
        "summarize": lambda r: r if isinstance(r, str) else str(r)
    }
}
