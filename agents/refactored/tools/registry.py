"""
Tool registry for the agent framework.

This module provides a registry of all available tools.
"""
from agents.refactored.core.tool_executor import ToolRegistry, register_tools

# Import tool modules
from agents.refactored.tools import routes
from agents.refactored.tools import places
from agents.refactored.tools import visualization
from agents.refactored.tools import answer


def create_tool_registry() -> ToolRegistry:
    """
    Create a tool registry with all available tools.
    
    Returns:
        A ToolRegistry instance with all tools registered
    """
    registry = ToolRegistry()
    
    # Register tools from each module
    register_tools(registry, routes)
    register_tools(registry, places)
    register_tools(registry, visualization)
    register_tools(registry, answer)
    
    return registry


# Create a global tool registry instance
TOOL_REGISTRY = create_tool_registry()


def get_tool_registry() -> ToolRegistry:
    """
    Get the global tool registry.
    
    Returns:
        The global ToolRegistry instance
    """
    return TOOL_REGISTRY
