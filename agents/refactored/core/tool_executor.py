"""
Tool execution framework for the agent.

This module provides the infrastructure for registering, validating, and executing tools.
"""
from typing import Dict, Any, Callable, Optional, List, TypedDict, Union
import inspect
import json
import jsonschema
import traceback
from functools import wraps

from agents.refactored.core.errors import (
    ToolNotFoundError,
    ToolExecutionError,
    InvalidToolInputError,
    ValidationError
)


class ToolSpec(TypedDict, total=False):
    """Type definition for tool specifications."""
    name: str
    description: str
    parameters: Dict[str, Any]
    required: List[str]
    examples: List[Dict[str, Any]]


class ToolResult:
    """Represents the result of a tool execution."""
    
    def __init__(
        self, 
        success: bool, 
        result: Any = None, 
        error: Optional[Exception] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a tool result.
        
        Args:
            success: Whether the tool execution was successful
            result: The result of the tool execution (if successful)
            error: The error that occurred (if unsuccessful)
            metadata: Additional metadata about the tool execution
        """
        self.success = success
        self.result = result
        self.error = error
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the tool result to a dictionary."""
        result_dict = {
            "success": self.success,
            "metadata": self.metadata
        }
        
        if self.success:
            result_dict["result"] = self.result
        else:
            result_dict["error"] = str(self.error)
            if isinstance(self.error, Exception):
                result_dict["error_type"] = type(self.error).__name__
        
        return result_dict
    
    def __str__(self) -> str:
        """Return a string representation of the tool result."""
        if self.success:
            return f"Success: {self.result}"
        return f"Error: {self.error}"


class Tool:
    """Represents a tool that can be executed by the agent."""
    
    def __init__(
        self, 
        name: str, 
        func: Callable, 
        schema: Dict[str, Any],
        description: str = "",
        examples: Optional[List[Dict[str, Any]]] = None
    ):
        """
        Initialize a tool.
        
        Args:
            name: The name of the tool
            func: The function to execute
            schema: The JSON schema for the tool's parameters
            description: A description of the tool
            examples: Optional examples of tool usage
        """
        self.name = name
        self.func = func
        self.schema = schema
        self.description = description
        self.examples = examples or []
    
    def validate_input(self, params: Dict[str, Any]) -> None:
        """
        Validate the input parameters against the schema.
        
        Args:
            params: The parameters to validate
            
        Raises:
            InvalidToolInputError: If validation fails
        """
        try:
            jsonschema.validate(instance=params, schema=self.schema)
        except jsonschema.exceptions.ValidationError as e:
            validation_errors = {"error": str(e)}
            raise InvalidToolInputError(self.name, validation_errors)
    
    def execute(self, params: Dict[str, Any]) -> ToolResult:
        """
        Execute the tool with the given parameters.
        
        Args:
            params: The parameters to pass to the tool
            
        Returns:
            The result of the tool execution
        """
        try:
            # Validate input parameters
            self.validate_input(params)
            
            # Execute the tool function
            result = self.func(**params)
            
            return ToolResult(success=True, result=result)
        except InvalidToolInputError as e:
            # Re-raise validation errors
            raise e
        except Exception as e:
            # Wrap other exceptions in ToolExecutionError
            traceback_str = traceback.format_exc()
            metadata = {"traceback": traceback_str}
            return ToolResult(success=False, error=e, metadata=metadata)
    
    def to_spec(self) -> ToolSpec:
        """
        Convert the tool to a specification dictionary.
        
        Returns:
            A dictionary containing the tool's specification
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.schema.get("properties", {}),
            "required": self.schema.get("required", []),
            "examples": self.examples
        }


class ToolRegistry:
    """Registry for tools that can be executed by the agent."""
    
    def __init__(self):
        """Initialize an empty tool registry."""
        self.tools: Dict[str, Tool] = {}
    
    def register(
        self, 
        name: str, 
        func: Callable, 
        schema: Dict[str, Any],
        description: str = "",
        examples: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Register a tool.
        
        Args:
            name: The name of the tool
            func: The function to execute
            schema: The JSON schema for the tool's parameters
            description: A description of the tool
            examples: Optional examples of tool usage
        """
        self.tools[name] = Tool(name, func, schema, description, examples)
    
    def register_from_function(
        self, 
        func: Callable, 
        name: Optional[str] = None,
        description: Optional[str] = None,
        examples: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Register a tool from a function, automatically generating the schema.
        
        Args:
            func: The function to register
            name: Optional name for the tool (defaults to function name)
            description: Optional description (defaults to function docstring)
            examples: Optional examples of tool usage
        """
        tool_name = name or func.__name__
        tool_description = description or (func.__doc__ or "").strip()
        
        # Generate schema from function signature
        sig = inspect.signature(func)
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            # Skip self parameter for methods
            if param_name == "self":
                continue
            
            # Determine parameter type
            param_type = "object"  # Default type
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == str:
                    param_type = "string"
                elif param.annotation == int:
                    param_type = "integer"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"
                elif param.annotation == list or param.annotation == List:
                    param_type = "array"
                elif param.annotation == dict or param.annotation == Dict:
                    param_type = "object"
            
            # Add parameter to properties
            properties[param_name] = {
                "type": param_type,
                "description": f"Parameter: {param_name}"
            }
            
            # Add to required list if no default value
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
        
        schema = {
            "type": "object",
            "properties": properties,
            "required": required
        }
        
        self.register(tool_name, func, schema, tool_description, examples)
    
    def get(self, name: str) -> Tool:
        """
        Get a tool by name.
        
        Args:
            name: The name of the tool
            
        Returns:
            The tool
            
        Raises:
            ToolNotFoundError: If the tool is not found
        """
        if name not in self.tools:
            raise ToolNotFoundError(name)
        return self.tools[name]
    
    def execute(self, name: str, params: Dict[str, Any]) -> ToolResult:
        """
        Execute a tool by name.
        
        Args:
            name: The name of the tool
            params: The parameters to pass to the tool
            
        Returns:
            The result of the tool execution
            
        Raises:
            ToolNotFoundError: If the tool is not found
        """
        tool = self.get(name)
        return tool.execute(params)
    
    def list_tools(self) -> List[str]:
        """
        List all registered tools.
        
        Returns:
            A list of tool names
        """
        return list(self.tools.keys())
    
    def get_specs(self) -> Dict[str, ToolSpec]:
        """
        Get specifications for all registered tools.
        
        Returns:
            A dictionary mapping tool names to their specifications
        """
        return {name: tool.to_spec() for name, tool in self.tools.items()}


def tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
    schema: Optional[Dict[str, Any]] = None,
    examples: Optional[List[Dict[str, Any]]] = None
) -> Callable:
    """
    Decorator for registering a function as a tool.
    
    Args:
        name: Optional name for the tool (defaults to function name)
        description: Optional description (defaults to function docstring)
        schema: Optional JSON schema for the tool's parameters
        examples: Optional examples of tool usage
        
    Returns:
        A decorator function
    """
    def decorator(func: Callable) -> Callable:
        # Store tool metadata on the function
        func._tool_metadata = {
            "name": name or func.__name__,
            "description": description or (func.__doc__ or "").strip(),
            "schema": schema,
            "examples": examples or []
        }
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def register_tools(registry: ToolRegistry, module) -> None:
    """
    Register all tools in a module.
    
    Args:
        registry: The tool registry
        module: The module containing the tools
    """
    for name in dir(module):
        item = getattr(module, name)
        if callable(item) and hasattr(item, "_tool_metadata"):
            metadata = item._tool_metadata
            
            if metadata["schema"]:
                # Register with provided schema
                registry.register(
                    metadata["name"],
                    item,
                    metadata["schema"],
                    metadata["description"],
                    metadata["examples"]
                )
            else:
                # Auto-generate schema from function signature
                registry.register_from_function(
                    item,
                    metadata["name"],
                    metadata["description"],
                    metadata["examples"]
                )
