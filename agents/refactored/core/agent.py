"""
Base agent implementation for the agent framework.

This module provides the base Agent class that defines the core functionality
and interfaces for all agent implementations.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable, Iterator, Union
import json
import re
import logging
import time
from datetime import datetime

from agents.refactored.core.memory import MemoryStore
from agents.refactored.core.llm_client import LLMClient
from agents.refactored.core.tool_executor import ToolRegistry, ToolResult
from agents.refactored.core.errors import (
    AgentError,
    ParsingError,
    ToolNotFoundError,
    ToolExecutionError
)


class Agent(ABC):
    """
    Base agent class that defines the core functionality for all agents.
    
    This abstract class provides the foundation for building specialized agents
    by implementing common functionality like memory management, tool execution,
    and the reasoning loop.
    """
    
    def __init__(
        self,
        llm_client: LLMClient,
        tool_registry: ToolRegistry,
        memory: Optional[MemoryStore] = None,
        system_prompt: str = "You are a helpful assistant.",
        max_iterations: int = 10,
        debug: bool = False
    ):
        """
        Initialize the agent.
        
        Args:
            llm_client: The LLM client to use for generating responses
            tool_registry: The tool registry containing available tools
            memory: Optional memory store (created if not provided)
            system_prompt: The system prompt to use
            max_iterations: Maximum number of reasoning iterations
            debug: Whether to enable debug logging
        """
        self.llm_client = llm_client
        self.tool_registry = tool_registry
        self.memory = memory or MemoryStore()
        self.system_prompt = system_prompt
        self.max_iterations = max_iterations
        self.debug = debug
        
        # Set up logging
        self.logger = self._setup_logger()
        
        # Hook for subclasses to initialize additional components
        self._initialize()
    
    def _setup_logger(self) -> logging.Logger:
        """
        Set up the logger for the agent.
        
        Returns:
            A configured logger instance
        """
        logger = logging.getLogger(f"agent.{self.__class__.__name__}")
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        logger.setLevel(logging.DEBUG if self.debug else logging.INFO)
        return logger
    
    def _initialize(self) -> None:
        """
        Hook for subclasses to initialize additional components.
        
        This method is called at the end of __init__ and can be overridden
        by subclasses to perform additional initialization.
        """
        pass
    
    def log(self, level: int, message: str, *args, **kwargs) -> None:
        """
        Log a message at the specified level.
        
        Args:
            level: The logging level
            message: The message to log
            *args: Additional positional arguments for the logger
            **kwargs: Additional keyword arguments for the logger
        """
        self.logger.log(level, message, *args, **kwargs)
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a message to the conversation history.
        
        Args:
            role: The role of the message sender
            content: The content of the message
            metadata: Optional metadata for the message
        """
        self.log(logging.DEBUG, f"Adding message - role: {role}, content: {content[:100]}...")
        self.memory.add_message(role, content, metadata)
    
    def extract_action(self, response_text: str) -> Dict[str, Any]:
        """
        Extract an action from the LLM response.
        
        Args:
            response_text: The LLM response text
            
        Returns:
            The extracted action as a dictionary
            
        Raises:
            ParsingError: If action extraction fails
        """
        self.log(logging.DEBUG, "Extracting action from response")
        
        try:
            # Look for an action block in the format <action>...</action>
            match = re.search(r"<action>(.*?)</action>", response_text, re.DOTALL)
            if not match:
                self.log(logging.DEBUG, "No <action> block found in response")
                return {
                    "tool": "answer",
                    "tool_input": {"text": response_text.strip()},
                    "reasoning": "No <action> block found."
                }
            
            action_json = match.group(1).strip()
            
            # Try to fix common JSON errors before parsing
            # Replace single quotes with double quotes
            action_json = action_json.replace("'", "\"")
            
            # Remove trailing commas in objects and arrays
            action_json = re.sub(r',\s*}', '}', action_json)
            action_json = re.sub(r',\s*]', ']', action_json)
            
            # Try to parse the JSON
            try:
                action = json.loads(action_json)
            except json.JSONDecodeError:
                # If parsing fails, try a more aggressive approach
                self.log(logging.WARNING, "Initial JSON parsing failed, trying more aggressive fixes")
                
                # Remove all whitespace and try again
                action_json_compact = re.sub(r'\s+', '', action_json)
                
                # Try to parse again
                try:
                    action = json.loads(action_json_compact)
                except json.JSONDecodeError:
                    # If still failing, raise the original error
                    self.log(logging.ERROR, "Failed to parse JSON even after fixes")
                    raise ParsingError(f"Failed to parse action JSON", response_text)
            
            # Ensure tool_input is a dictionary
            if "tool_input" in action and not isinstance(action["tool_input"], dict):
                action["tool_input"] = {"text": str(action["tool_input"])}
            
            # Ensure required fields are present
            if "tool" not in action:
                action["tool"] = "answer"
            
            if "tool_input" not in action:
                action["tool_input"] = {}
            
            if "reasoning" not in action:
                action["reasoning"] = "No reasoning provided."
            
            self.log(logging.DEBUG, f"Parsed action: {action}")
            return action
        except json.JSONDecodeError as e:
            self.log(logging.ERROR, f"Failed to parse JSON from <action> block: {e}")
            raise ParsingError(f"Failed to parse action JSON: {e}", response_text)
        except Exception as e:
            self.log(logging.ERROR, f"Error extracting action: {e}")
            raise ParsingError(f"Error extracting action: {e}", response_text)
    
    def execute_action(self, action: Dict[str, Any]) -> ToolResult:
        """
        Execute a tool based on the action.
        
        Args:
            action: The action to execute
            
        Returns:
            The result of the tool execution
        """
        tool_name = action.get("tool", "answer")
        tool_input = action.get("tool_input", {})
        reasoning = action.get("reasoning", "")
        
        self.log(logging.INFO, f"Executing action - tool: {tool_name}, reasoning: {reasoning}")
        
        try:
            # Inject memory into tool input if needed
            tool_input = self._inject_memory_into_tool_input(tool_name, tool_input)
            
            # Execute the tool
            result = self.tool_registry.execute(tool_name, tool_input)
            
            # Update memory based on tool result
            if result.success:
                self._update_memory_from_tool_result(tool_name, result.result)
            
            return result
        except ToolNotFoundError as e:
            self.log(logging.ERROR, f"Tool not found: {e}")
            return ToolResult(
                success=False,
                error=e,
                metadata={"tool_name": tool_name, "tool_input": tool_input}
            )
        except Exception as e:
            self.log(logging.ERROR, f"Error executing action: {e}")
            return ToolResult(
                success=False,
                error=ToolExecutionError(tool_name, e),
                metadata={"tool_name": tool_name, "tool_input": tool_input}
            )
    
    def _inject_memory_into_tool_input(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inject memory into tool input if needed.
        
        Args:
            tool_name: The name of the tool
            tool_input: The tool input parameters
            
        Returns:
            The updated tool input parameters
        """
        # Make a copy of the input to avoid modifying the original
        tool_input = tool_input.copy()
        
        # Tool-specific memory injection logic
        if tool_name == "sample_polyline" and "encoded_polyline" not in tool_input:
            polyline = self.memory.recall("encoded_polyline")
            if polyline:
                tool_input["encoded_polyline"] = polyline
                self.log(logging.DEBUG, f"Injected encoded_polyline into {tool_name} from memory")
        
        elif tool_name in ["get_places", "get_natural_features", "render_map"] and "polyline_coords" not in tool_input:
            coords = self.memory.recall("polyline_coords")
            if coords:
                tool_input["polyline_coords"] = coords
                self.log(logging.DEBUG, f"Injected polyline_coords into {tool_name} from memory")
        
        # For render_map, also inject places and features paths
        if tool_name == "render_map":
            if self.memory.has_key("places") and "places_path" not in tool_input:
                tool_input["places_path"] = "places_along_route.json"
                self.log(logging.DEBUG, "Injected places_path into render_map")
            
            if self.memory.has_key("features") and "features_path" not in tool_input:
                tool_input["features_path"] = "natural_features_along_route.json"
                self.log(logging.DEBUG, "Injected features_path into render_map")
        
        return tool_input
    
    def _update_memory_from_tool_result(self, tool_name: str, result: Any) -> None:
        """
        Update memory based on tool result.
        
        Args:
            tool_name: The name of the tool
            result: The result of the tool execution
        """
        # Tool-specific memory update logic
        if tool_name == "get_route" and isinstance(result, dict):
            if "polyline" in result:
                self.memory.remember("encoded_polyline", result["polyline"])
                self.log(logging.DEBUG, "Stored encoded_polyline in memory")
            
            if "polyline_coords" in result:
                self.memory.remember("polyline_coords", result["polyline_coords"])
                self.log(logging.DEBUG, "Stored polyline_coords in memory")
        
        elif tool_name == "sample_polyline" and isinstance(result, list):
            self.memory.remember("polyline_coords", result)
            self.log(logging.DEBUG, "Updated polyline_coords from sampled polyline")
        
        elif tool_name == "get_places" and isinstance(result, list):
            self.memory.remember("places", result)
            self.log(logging.DEBUG, "Stored places in memory")
        
        elif tool_name == "get_natural_features" and isinstance(result, list):
            self.memory.remember("features", result)
            self.log(logging.DEBUG, "Stored features in memory")
    
    def format_tool_result(self, tool_name: str, result: ToolResult) -> str:
        """
        Format a tool result for inclusion in the conversation.
        
        Args:
            tool_name: The name of the tool
            result: The result of the tool execution
            
        Returns:
            A formatted string representation of the result
        """
        if not result.success:
            return f"Error executing tool '{tool_name}': {result.error}"
        
        # Default formatting for different result types
        if isinstance(result.result, list):
            if not result.result:
                return f"Tool '{tool_name}' returned an empty list."
            
            # For lists, summarize the number of items and show a sample
            sample_size = min(3, len(result.result))
            sample = result.result[:sample_size]
            
            if isinstance(sample[0], dict):
                # For lists of dictionaries, show key-value pairs
                sample_str = "\n".join([
                    ", ".join([f"{k}: {v}" for k, v in item.items()])
                    for item in sample
                ])
            else:
                # For lists of other types, just join the items
                sample_str = "\n".join([str(item) for item in sample])
            
            return (
                f"Tool '{tool_name}' returned {len(result.result)} items. "
                f"Here's a sample:\n{sample_str}"
            )
        
        elif isinstance(result.result, dict):
            # For dictionaries, show key-value pairs
            return (
                f"Tool '{tool_name}' returned:\n" +
                "\n".join([f"{k}: {v}" for k, v in result.result.items()])
            )
        
        else:
            # For other types, just convert to string
            return f"Tool '{tool_name}' returned: {result.result}"
    
    def process_query(self, query: str, stream: bool = False) -> str:
        """
        Process a user query using the agent's reasoning loop.
        
        Args:
            query: The user query
            stream: Whether to stream the response
            
        Returns:
            The final response
        """
        if not self.llm_client.is_available():
            return "LLM client is not available."
        
        # Add the user query to memory
        self.add_message("user", query)
        
        # Build the initial context
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.memory.get_conversation_history())
        
        # First LLM call
        self.log(logging.INFO, "Sending initial query to LLM")
        
        if stream:
            response_text = self._stream_llm_response(messages)
        else:
            response = self.llm_client.chat(messages)
            response_text = self.llm_client.extract_content(response)
        
        self.log(logging.DEBUG, f"Initial LLM response: {response_text[:500]}...")
        
        # Extract action from response
        action = self.extract_action(response_text)
        
        # Reasoning loop
        iterations = 0
        while action["tool"] != "answer" and iterations < self.max_iterations:
            # Execute the tool specified by the action
            tool_name = action["tool"]
            tool_result = self.execute_action(action)
            
            # Format the result for inclusion in the conversation
            result_str = self.format_tool_result(tool_name, tool_result)
            
            # Add the observation to memory
            self.add_message("assistant", f"Observation: {result_str}")
            
            # Rebuild the context including the latest observation
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend(self.memory.get_conversation_history())
            
            # Query the LLM with the updated context
            self.log(logging.INFO, f"Sending follow-up query to LLM (iteration {iterations + 1})")
            
            if stream:
                response_text = self._stream_llm_response(messages)
            else:
                response = self.llm_client.chat(messages)
                response_text = self.llm_client.extract_content(response)
            
            self.log(logging.DEBUG, f"Follow-up LLM response: {response_text[:500]}...")
            
            # Extract the next action
            action = self.extract_action(response_text)
            iterations += 1
        
        # Final answer
        final_answer = action.get("tool_input", {}).get("text", "")
        if not final_answer:
            final_answer = "I couldn't determine an answer to your query."
        
        # Add the final answer to memory
        self.add_message("assistant", final_answer)
        
        return final_answer
    
    def _stream_llm_response(self, messages: List[Dict[str, str]]) -> str:
        """
        Stream a response from the LLM and return the full response.
        
        Args:
            messages: The messages to send to the LLM
            
        Returns:
            The full response text
        """
        full_response = ""
        for chunk in self.llm_client.stream_chat(messages):
            full_response += chunk
            # This is where you would yield chunks for real-time display
        return full_response
    
    def run_interactive(self) -> None:
        """Run the agent in interactive mode."""
        print(f"Agent ready. Type 'exit' to quit.")
        
        if not self.llm_client.is_available():
            print("LLM client is not available.")
            return
        
        while True:
            query = input("\nYou: ")
            if query.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            print("\nAgent:", end=" ")
            response = self.process_query(query, stream=True)
            print(response)
