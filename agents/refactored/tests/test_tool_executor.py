"""
Tests for the tool executor module.
"""
import unittest
import json
from typing import Dict, Any

from agents.refactored.core.tool_executor import (
    ToolRegistry, 
    Tool, 
    tool, 
    register_tools,
    ToolResult
)
from agents.refactored.core.errors import (
    ToolNotFoundError,
    InvalidToolInputError
)


# Define some test tools
@tool(
    name="test_tool",
    description="A test tool"
)
def test_tool(param1: str, param2: int = 42) -> Dict[str, Any]:
    """A test tool for testing."""
    return {"param1": param1, "param2": param2}


@tool(
    name="test_tool_with_schema",
    description="A test tool with a custom schema",
    schema={
        "type": "object",
        "properties": {
            "param1": {"type": "string"},
            "param2": {"type": "integer"}
        },
        "required": ["param1"]
    }
)
def test_tool_with_schema(param1: str, param2: int = 42) -> Dict[str, Any]:
    """A test tool with a custom schema."""
    return {"param1": param1, "param2": param2}


class TestToolExecutor(unittest.TestCase):
    """Tests for the tool executor module."""
    
    def setUp(self):
        """Set up the test case."""
        self.registry = ToolRegistry()
        
        # Register the test tools
        self.registry.register_from_function(test_tool)
        self.registry.register(
            "test_tool_with_schema",
            test_tool_with_schema,
            {
                "type": "object",
                "properties": {
                    "param1": {"type": "string"},
                    "param2": {"type": "integer"}
                },
                "required": ["param1"]
            },
            "A test tool with a custom schema"
        )
    
    def test_register_tool(self):
        """Test registering a tool."""
        # Check that the tools were registered
        self.assertIn("test_tool", self.registry.tools)
        self.assertIn("test_tool_with_schema", self.registry.tools)
        
        # Check that the tools have the correct properties
        self.assertEqual(self.registry.tools["test_tool"].name, "test_tool")
        self.assertEqual(self.registry.tools["test_tool_with_schema"].name, "test_tool_with_schema")
    
    def test_execute_tool(self):
        """Test executing a tool."""
        # Execute the test tool
        result = self.registry.execute("test_tool", {"param1": "test"})
        
        # Check that the result is correct
        self.assertTrue(result.success)
        self.assertEqual(result.result["param1"], "test")
        self.assertEqual(result.result["param2"], 42)
    
    def test_execute_tool_with_schema(self):
        """Test executing a tool with a custom schema."""
        # Execute the test tool
        result = self.registry.execute("test_tool_with_schema", {"param1": "test", "param2": 43})
        
        # Check that the result is correct
        self.assertTrue(result.success)
        self.assertEqual(result.result["param1"], "test")
        self.assertEqual(result.result["param2"], 43)
    
    def test_execute_tool_with_missing_required_param(self):
        """Test executing a tool with a missing required parameter."""
        # Execute the test tool with a missing required parameter
        with self.assertRaises(InvalidToolInputError):
            self.registry.execute("test_tool_with_schema", {})
    
    def test_execute_nonexistent_tool(self):
        """Test executing a nonexistent tool."""
        # Execute a nonexistent tool
        with self.assertRaises(ToolNotFoundError):
            self.registry.execute("nonexistent_tool", {})
    
    def test_tool_decorator(self):
        """Test the tool decorator."""
        # Create a new registry
        registry = ToolRegistry()
        
        # Define a module-like object with the test tools
        class MockModule:
            pass
        
        mock_module = MockModule()
        mock_module.test_tool = test_tool
        mock_module.test_tool_with_schema = test_tool_with_schema
        
        # Register the tools from the mock module
        register_tools(registry, mock_module)
        
        # Check that the tools were registered
        self.assertIn("test_tool", registry.tools)
        self.assertIn("test_tool_with_schema", registry.tools)
    
    def test_tool_result(self):
        """Test the ToolResult class."""
        # Create a successful result
        success_result = ToolResult(True, {"key": "value"})
        
        # Check that the result is correct
        self.assertTrue(success_result.success)
        self.assertEqual(success_result.result, {"key": "value"})
        self.assertIsNone(success_result.error)
        
        # Create a failed result
        error = ValueError("Test error")
        failed_result = ToolResult(False, error=error)
        
        # Check that the result is correct
        self.assertFalse(failed_result.success)
        self.assertIsNone(failed_result.result)
        self.assertEqual(failed_result.error, error)
    
    def test_tool_input_validation(self):
        """Test tool input validation."""
        # Create a tool with a schema that requires specific types
        registry = ToolRegistry()
        registry.register(
            "type_test_tool",
            lambda x, y: {"x": x, "y": y},
            {
                "type": "object",
                "properties": {
                    "x": {"type": "number"},
                    "y": {"type": "string"}
                },
                "required": ["x", "y"]
            },
            "A tool for testing type validation"
        )
        
        # Test with correct types
        result = registry.execute("type_test_tool", {"x": 1, "y": "test"})
        self.assertTrue(result.success)
        
        # Test with incorrect types
        with self.assertRaises(InvalidToolInputError):
            registry.execute("type_test_tool", {"x": "not a number", "y": "test"})
        
        with self.assertRaises(InvalidToolInputError):
            registry.execute("type_test_tool", {"x": 1, "y": 2})
    
    def test_list_tools(self):
        """Test listing tools."""
        # List the tools
        tools = self.registry.list_tools()
        
        # Check that the list is correct
        self.assertIn("test_tool", tools)
        self.assertIn("test_tool_with_schema", tools)
    
    def test_get_specs(self):
        """Test getting tool specifications."""
        # Get the tool specifications
        specs = self.registry.get_specs()
        
        # Check that the specifications are correct
        self.assertIn("test_tool", specs)
        self.assertIn("test_tool_with_schema", specs)
        self.assertEqual(specs["test_tool"]["name"], "test_tool")
        self.assertEqual(specs["test_tool_with_schema"]["name"], "test_tool_with_schema")


if __name__ == "__main__":
    unittest.main()
