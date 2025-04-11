"""
Google Maps agent implementation.

This module provides a specialized agent for working with Google Maps data.
"""
from typing import Dict, List, Any, Optional, Union
import logging

from agents.refactored.core.agent import Agent
from agents.refactored.core.memory import MemoryStore
from agents.refactored.core.llm_client import LLMClient
from agents.refactored.core.tool_executor import ToolRegistry
from agents.refactored.clients.ollama_client import OllamaClient
from agents.refactored.tools import TOOL_REGISTRY
from agents.refactored.config.prompts import GOOGLEMAPS_SYSTEM_PROMPT
from agents.refactored.config.settings import get_settings, get_log_level
from agents.refactored.utils.logging import get_logger


class GoogleMapsAgent(Agent):
    """
    A specialized agent for working with Google Maps data.
    
    This agent can:
    - Generate directions between locations
    - Find places and natural features along a route
    - Render maps with routes, places, and features
    - Answer questions about routes and locations
    """
    
    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        tool_registry: Optional[ToolRegistry] = None,
        memory: Optional[MemoryStore] = None,
        system_prompt: Optional[str] = None,
        max_iterations: Optional[int] = None,
        debug: Optional[bool] = None
    ):
        """
        Initialize the Google Maps agent.
        
        Args:
            llm_client: Optional LLM client (created if not provided)
            tool_registry: Optional tool registry (uses global registry if not provided)
            memory: Optional memory store (created if not provided)
            system_prompt: Optional system prompt (uses default if not provided)
            max_iterations: Optional maximum number of reasoning iterations
            debug: Optional debug flag
        """
        # Load settings
        settings = get_settings()
        
        # Create LLM client if not provided
        if llm_client is None:
            llm_model = settings["llm"]["model"]
            llm_client = OllamaClient(
                base_url=settings["llm"]["api_base"],
                default_model=llm_model
            )
        
        # Use global tool registry if not provided
        if tool_registry is None:
            tool_registry = TOOL_REGISTRY
        
        # Use default system prompt if not provided
        if system_prompt is None:
            system_prompt = GOOGLEMAPS_SYSTEM_PROMPT
        
        # Use settings for max_iterations if not provided
        if max_iterations is None:
            max_iterations = settings["agent"]["max_iterations"]
        
        # Use settings for debug if not provided
        if debug is None:
            debug = settings["agent"]["debug"]
        
        # Initialize the base agent
        super().__init__(
            llm_client=llm_client,
            tool_registry=tool_registry,
            memory=memory,
            system_prompt=system_prompt,
            max_iterations=max_iterations,
            debug=debug
        )
        
        # Set up logger
        log_level = get_log_level(settings["logging"]["level"])
        self.logger = get_logger(
            name="googlemaps_agent",
            level=log_level,
            console_output=settings["logging"]["console_output"],
            file_output=settings["logging"]["file_output"],
            log_dir=settings["logging"]["log_dir"],
            structured=settings["logging"]["structured"]
        )
    
    def _initialize(self) -> None:
        """Initialize additional components for the Google Maps agent."""
        self.log(logging.INFO, "Initializing Google Maps agent")
    
    def _inject_memory_into_tool_input(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inject memory into tool input if needed.
        
        This method extends the base implementation to handle Google Maps specific tools.
        
        Args:
            tool_name: The name of the tool
            tool_input: The tool input parameters
            
        Returns:
            The updated tool input parameters
        """
        # Call the base implementation first
        tool_input = super()._inject_memory_into_tool_input(tool_name, tool_input)
        
        # Google Maps specific memory injection
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
            if self.memory.has_key("places") and "places_path" not in tool_input and "places" not in tool_input:
                places = self.memory.recall("places")
                if places:
                    tool_input["places"] = places
                    self.log(logging.DEBUG, "Injected places into render_map")
            
            if self.memory.has_key("features") and "features_path" not in tool_input and "features" not in tool_input:
                features = self.memory.recall("features")
                if features:
                    tool_input["features"] = features
                    self.log(logging.DEBUG, "Injected features into render_map")
        
        return tool_input
    
    def _update_memory_from_tool_result(self, tool_name: str, result: Any) -> None:
        """
        Update memory based on tool result.
        
        This method extends the base implementation to handle Google Maps specific tools.
        
        Args:
            tool_name: The name of the tool
            result: The result of the tool execution
        """
        # Call the base implementation first
        super()._update_memory_from_tool_result(tool_name, result)
        
        # Google Maps specific memory updates
        if tool_name == "get_route" and isinstance(result, dict):
            if "polyline" in result:
                self.memory.remember("encoded_polyline", result["polyline"])
                self.log(logging.DEBUG, "Stored encoded_polyline in memory")
            
            if "polyline_coords" in result:
                self.memory.remember("polyline_coords", result["polyline_coords"])
                self.log(logging.DEBUG, "Stored polyline_coords in memory")
            
            if "distance_text" in result:
                self.memory.remember("distance_text", result["distance_text"])
                self.log(logging.DEBUG, "Stored distance_text in memory")
            
            if "duration_text" in result:
                self.memory.remember("duration_text", result["duration_text"])
                self.log(logging.DEBUG, "Stored duration_text in memory")
        
        elif tool_name == "sample_polyline" and isinstance(result, list):
            self.memory.remember("polyline_coords", result)
            self.log(logging.DEBUG, "Updated polyline_coords from sampled polyline")
        
        elif tool_name == "get_places" and isinstance(result, list):
            self.memory.remember("places", result)
            self.log(logging.DEBUG, "Stored places in memory")
        
        elif tool_name == "get_natural_features" and isinstance(result, list):
            self.memory.remember("features", result)
            self.log(logging.DEBUG, "Stored features in memory")
    
    def format_tool_result(self, tool_name: str, result: Any) -> str:
        """
        Format a tool result for inclusion in the conversation.
        
        This method extends the base implementation to provide better formatting
        for Google Maps specific tools.
        
        Args:
            tool_name: The name of the tool
            result: The result of the tool execution
            
        Returns:
            A formatted string representation of the result
        """
        # Handle Google Maps specific tools
        if tool_name == "get_route" and isinstance(result, dict):
            if "error" in result:
                return f"Error getting route: {result['error']}"
            
            distance = result.get("distance_text", "unknown distance")
            duration = result.get("duration_text", "unknown duration")
            return f"Route calculated: {distance}, {duration}"
        
        elif tool_name == "sample_polyline" and isinstance(result, list):
            return f"Route sampled to {len(result)} points."
        
        elif tool_name == "get_places" and isinstance(result, list):
            if not result:
                return "No places found along the route."
            
            # Count places by type
            cities = sum(1 for p in result if p.get("type") == "city")
            towns = sum(1 for p in result if p.get("type") == "town")
            villages = sum(1 for p in result if p.get("type") == "village")
            others = len(result) - cities - towns - villages
            
            # Format the result
            parts = []
            if cities > 0:
                parts.append(f"{cities} {'city' if cities == 1 else 'cities'}")
            if towns > 0:
                parts.append(f"{towns} {'town' if towns == 1 else 'towns'}")
            if villages > 0:
                parts.append(f"{villages} {'village' if villages == 1 else 'villages'}")
            if others > 0:
                parts.append(f"{others} other {'place' if others == 1 else 'places'}")
            
            summary = ", ".join(parts)
            return f"Found {len(result)} places along the route: {summary}"
        
        elif tool_name == "get_natural_features" and isinstance(result, list):
            if not result:
                return "No natural features found along the route."
            
            # Count features by type
            water = sum(1 for f in result if f.get("type") in ["water", "river", "lake", "stream"])
            peaks = sum(1 for f in result if f.get("type") in ["peak", "mountain"])
            forests = sum(1 for f in result if f.get("type") in ["wood", "forest"])
            others = len(result) - water - peaks - forests
            
            # Format the result
            parts = []
            if water > 0:
                parts.append(f"{water} water {'feature' if water == 1 else 'features'}")
            if peaks > 0:
                parts.append(f"{peaks} {'peak' if peaks == 1 else 'peaks'}")
            if forests > 0:
                parts.append(f"{forests} {'forest' if forests == 1 else 'forests'}")
            if others > 0:
                parts.append(f"{others} other {'feature' if others == 1 else 'features'}")
            
            summary = ", ".join(parts)
            return f"Found {len(result)} natural features along the route: {summary}"
        
        elif tool_name == "render_map":
            return f"Map rendered to {result}"
        
        # Fall back to the base implementation for other tools
        return super().format_tool_result(tool_name, result)


# Create a global agent instance
def create_agent(
    model: Optional[str] = None,
    debug: bool = False
) -> GoogleMapsAgent:
    """
    Create a Google Maps agent.
    
    Args:
        model: Optional model name to use
        debug: Whether to enable debug logging
        
    Returns:
        A GoogleMapsAgent instance
    """
    # Load settings
    settings = get_settings()
    
    # Use provided model or default from settings
    if model is None:
        model = settings["llm"]["model"]
    
    # Create LLM client
    llm_client = OllamaClient(
        base_url=settings["llm"]["api_base"],
        default_model=model
    )
    
    # Create agent
    agent = GoogleMapsAgent(
        llm_client=llm_client,
        debug=debug
    )
    
    return agent


if __name__ == "__main__":
    # Create and run the agent
    agent = create_agent(debug=True)
    agent.run_interactive()
