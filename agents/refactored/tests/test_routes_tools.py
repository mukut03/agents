"""
Tests for the routes tools.
"""
import unittest
from unittest.mock import patch, MagicMock
from typing import Dict, List, Any, Tuple

from agents.refactored.tools.routes import (
    get_route,
    sample_polyline_tool,
    save_route_data
)


class TestRoutesTools(unittest.TestCase):
    """Tests for the routes tools."""
    
    @patch('agents.refactored.tools.routes.GoogleMapsClient')
    @patch('agents.refactored.tools.routes.validate_coordinates')
    def test_get_route(self, mock_validate_coordinates, mock_client_class):
        """Test the get_route tool."""
        # Set up mocks
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock the get_route method
        mock_client.get_route.return_value = {
            "polyline": "test_polyline",
            "polyline_coords": [(1.0, 2.0), (3.0, 4.0)],
            "distance_text": "100 km",
            "duration_text": "1 hour"
        }
        
        # Mock the validate_coordinates function
        mock_validate_coordinates.side_effect = lambda coords: coords
        
        # Call the tool
        result = get_route(
            origin=[37.7749, -122.4194],
            destination=[34.0522, -118.2437],
            waypoints=[[36.1627, -86.7816]],
            travel_mode="DRIVE",
            avoid_tolls=False
        )
        
        # Check that the client was called correctly
        mock_client_class.assert_called_once()
        mock_client.get_route.assert_called_once_with(
            origin=[37.7749, -122.4194],
            destination=[34.0522, -118.2437],
            waypoints=[[36.1627, -86.7816]],
            travel_mode="DRIVE",
            avoid_tolls=False
        )
        
        # Check that the result is correct
        self.assertEqual(result["polyline"], "test_polyline")
        self.assertEqual(result["polyline_coords"], [(1.0, 2.0), (3.0, 4.0)])
        self.assertEqual(result["distance_text"], "100 km")
        self.assertEqual(result["duration_text"], "1 hour")
    
    @patch('agents.refactored.tools.routes.sample_polyline')
    def test_sample_polyline_tool(self, mock_sample_polyline):
        """Test the sample_polyline_tool."""
        # Set up mock
        mock_sample_polyline.return_value = [(1.0, 2.0), (3.0, 4.0)]
        
        # Call the tool
        result = sample_polyline_tool(
            encoded_polyline="test_polyline",
            method="interval",
            interval_km=5.0,
            every_nth=10
        )
        
        # Check that the sample_polyline function was called correctly
        mock_sample_polyline.assert_called_once_with(
            encoded_polyline="test_polyline",
            method="interval",
            interval_km=5.0,
            every_nth=10
        )
        
        # Check that the result is correct
        self.assertEqual(result, [(1.0, 2.0), (3.0, 4.0)])
    
    def test_sample_polyline_tool_invalid_method(self):
        """Test the sample_polyline_tool with an invalid method."""
        # Call the tool with an invalid method
        with self.assertRaises(ValueError):
            sample_polyline_tool(
                encoded_polyline="test_polyline",
                method="invalid_method",
                interval_km=5.0,
                every_nth=10
            )
    
    @patch('builtins.open', unittest.mock.mock_open())
    @patch('json.dump')
    def test_save_route_data(self, mock_json_dump):
        """Test the save_route_data tool."""
        # Call the tool
        result = save_route_data(
            polyline_coords=[(1.0, 2.0), (3.0, 4.0)],
            polyline="test_polyline",
            places=[{"name": "Test Place"}],
            features=[{"name": "Test Feature"}],
            polyline_file="test_polyline.json",
            places_file="test_places.json",
            features_file="test_features.json"
        )
        
        # Check that the files were opened correctly
        self.assertEqual(open.call_count, 3)
        
        # Check that json.dump was called correctly
        self.assertEqual(mock_json_dump.call_count, 3)
        
        # Check that the result is correct
        self.assertEqual(result["polyline_file"], "test_polyline.json")
        self.assertEqual(result["places_file"], "test_places.json")
        self.assertEqual(result["features_file"], "test_features.json")


if __name__ == "__main__":
    unittest.main()
