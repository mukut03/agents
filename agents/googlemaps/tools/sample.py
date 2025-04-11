# tools/sample.py
from agents.googlemaps.routechat import sample_polyline

def tool_sample_polyline(encoded_polyline: str, method: str = "interval", interval_km: float = 5.0, every_nth: int = 10) -> list:
    """
    Samples latitude/longitude points from an encoded polyline using interval or index sampling.

    Args:
        encoded_polyline: Encoded Google Maps polyline string.
        method: 'interval' or 'nth'.
        interval_km: Sampling interval in km.
        every_nth: Sample every nth point.

    Returns:
        List of (lat, lon) points.
    """
    return sample_polyline(encoded_polyline, method=method, interval_km=interval_km, every_nth=every_nth)


def schema_sample_polyline():
    return {
        "type": "object",
        "properties": {
            "encoded_polyline": {"type": "string", "example": "xyz123..."},
            "method": {"type": "string", "enum": ["interval", "nth"], "default": "interval"},
            "interval_km": {"type": "number", "default": 5.0},
            "every_nth": {"type": "integer", "default": 10}
        },
        "required": ["encoded_polyline"]
    }

