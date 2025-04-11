"""
Tests for the agent's action extraction functionality.
"""
import unittest
import json
from typing import Dict, Any, List

from agents.refactored.core.agent import Agent
from agents.refactored.core.memory import MemoryStore
from agents.refactored.core.tool_executor import ToolRegistry
from agents.refactored.core.llm_client import MockLLMClient
from agents.refactored.core.errors import ParsingError


class TestAgentActionExtraction(unittest.TestCase):
    """Tests for the agent's action extraction functionality."""
    
    def setUp(self):
        """Set up the test case."""
        # Create a mock LLM client
        self.llm_client = MockLLMClient()
        
        # Create a tool registry
        self.tool_registry = ToolRegistry()
        
        # Register a test tool
        self.tool_registry.register(
            "test_tool",
            lambda **kwargs: kwargs,
            {
                "type": "object",
                "properties": {
                    "param1": {"type": "string"},
                    "param2": {"type": "integer"}
                },
                "required": ["param1"]
            },
            "A test tool"
        )
        
        # Create a test agent
        self.agent = TestAgent(
            llm_client=self.llm_client,
            tool_registry=self.tool_registry
        )
    
    def test_extract_action_valid(self):
        """Test extracting a valid action."""
        # Valid action JSON
        action_json = """
        <action>
        {
          "tool": "test_tool",
          "tool_input": {
            "param1": "test",
            "param2": 42
          },
          "reasoning": "This is a test."
        }
        </action>
        """
        
        # Extract the action
        action = self.agent.extract_action(action_json)
        
        # Check that the action was extracted correctly
        self.assertEqual(action["tool"], "test_tool")
        self.assertEqual(action["tool_input"]["param1"], "test")
        self.assertEqual(action["tool_input"]["param2"], 42)
        self.assertEqual(action["reasoning"], "This is a test.")
    
    def test_extract_action_invalid_json(self):
        """Test extracting an action with invalid JSON."""
        # Invalid JSON (missing closing brace)
        action_json = """
        <action>
        {
          "tool": "test_tool",
          "tool_input": {
            "param1": "test",
            "param2": 42
          },
          "reasoning": "This is a test."
        </action>
        """
        
        # Extract the action (should raise a ParsingError)
        with self.assertRaises(ParsingError):
            self.agent.extract_action(action_json)
    
    def test_extract_action_invalid_format(self):
        """Test extracting an action with an invalid format."""
        # Invalid format (missing <action> tags)
        action_json = """
        {
          "tool": "test_tool",
          "tool_input": {
            "param1": "test",
            "param2": 42
          },
          "reasoning": "This is a test."
        }
        """
        
        # Extract the action (should return an answer action)
        action = self.agent.extract_action(action_json)
        self.assertEqual(action["tool"], "answer")
        self.assertEqual(action["tool_input"]["text"], action_json.strip())
    
    def test_extract_action_with_trailing_comma(self):
        """Test extracting an action with a trailing comma in the JSON."""
        # JSON with a trailing comma (invalid JSON but common mistake)
        action_json = """
        <action>
        {
          "tool": "test_tool",
          "tool_input": {
            "param1": "test",
            "param2": 42,
          },
          "reasoning": "This is a test."
        }
        </action>
        """
        
        # Extract the action (should raise a ParsingError)
        with self.assertRaises(ParsingError):
            self.agent.extract_action(action_json)
    
    def test_extract_action_with_single_quotes(self):
        """Test extracting an action with single quotes in the JSON."""
        # JSON with single quotes (invalid JSON but common mistake)
        action_json = """
        <action>
        {
          'tool': 'test_tool',
          'tool_input': {
            'param1': 'test',
            'param2': 42
          },
          'reasoning': 'This is a test.'
        }
        </action>
        """
        
        # Extract the action (should raise a ParsingError)
        with self.assertRaises(ParsingError):
            self.agent.extract_action(action_json)
    
    def test_extract_action_with_multiple_actions(self):
        """Test extracting an action when multiple actions are present."""
        # Multiple actions (should only extract the first one)
        action_json = """
        <action>
        {
          "tool": "test_tool",
          "tool_input": {
            "param1": "test1",
            "param2": 42
          },
          "reasoning": "This is the first test."
        }
        </action>
        
        <action>
        {
          "tool": "test_tool",
          "tool_input": {
            "param1": "test2",
            "param2": 43
          },
          "reasoning": "This is the second test."
        }
        </action>
        """
        
        # Extract the action (should only extract the first one)
        action = self.agent.extract_action(action_json)
        self.assertEqual(action["tool"], "test_tool")
        self.assertEqual(action["tool_input"]["param1"], "test1")
        self.assertEqual(action["tool_input"]["param2"], 42)
        self.assertEqual(action["reasoning"], "This is the first test.")
    
    def test_extract_action_with_non_dict_tool_input(self):
        """Test extracting an action with a non-dict tool_input."""
        # Action with a string tool_input
        action_json = """
        <action>
        {
          "tool": "test_tool",
          "tool_input": "This is not a dict",
          "reasoning": "This is a test."
        }
        </action>
        """
        
        # Extract the action (should convert tool_input to a dict)
        action = self.agent.extract_action(action_json)
        self.assertEqual(action["tool"], "test_tool")
        self.assertEqual(action["tool_input"]["text"], "This is not a dict")
        self.assertEqual(action["reasoning"], "This is a test.")


# Test agent class that inherits from Agent
class TestAgent(Agent):
    """A test agent for testing."""
    
    def process_query(self, query: str, stream: bool = False) -> str:
        """
        Process a user query.
        
        Args:
            query: The user query
            stream: Whether to stream the response
            
        Returns:
            The response
        """
        return "This is a test response."


if __name__ == "__main__":
    unittest.main()
