"""
Error definitions for the agent framework.
"""
from enum import Enum
from typing import Optional, Dict, Any


class ErrorCode(Enum):
    """Error codes for agent framework errors."""
    UNKNOWN_ERROR = "unknown_error"
    TOOL_NOT_FOUND = "tool_not_found"
    TOOL_EXECUTION_ERROR = "tool_execution_error"
    INVALID_TOOL_INPUT = "invalid_tool_input"
    LLM_ERROR = "llm_error"
    PARSING_ERROR = "parsing_error"
    API_ERROR = "api_error"
    VALIDATION_ERROR = "validation_error"
    MEMORY_ERROR = "memory_error"
    CONFIG_ERROR = "config_error"


class AgentError(Exception):
    """Base exception class for agent framework errors."""
    
    def __init__(
        self, 
        code: ErrorCode, 
        message: str, 
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize an AgentError.
        
        Args:
            code: The error code
            message: A human-readable error message
            details: Additional error details (optional)
        """
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)
    
    def __str__(self) -> str:
        """Return a string representation of the error."""
        if self.details:
            return f"{self.code.value}: {self.message} - {self.details}"
        return f"{self.code.value}: {self.message}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the error to a dictionary representation."""
        return {
            "code": self.code.value,
            "message": self.message,
            "details": self.details
        }


class ToolNotFoundError(AgentError):
    """Raised when a requested tool is not found in the registry."""
    
    def __init__(self, tool_name: str):
        super().__init__(
            ErrorCode.TOOL_NOT_FOUND,
            f"Tool '{tool_name}' not found in registry",
            {"tool_name": tool_name}
        )


class ToolExecutionError(AgentError):
    """Raised when a tool execution fails."""
    
    def __init__(self, tool_name: str, cause: Exception):
        super().__init__(
            ErrorCode.TOOL_EXECUTION_ERROR,
            f"Error executing tool '{tool_name}': {str(cause)}",
            {
                "tool_name": tool_name,
                "cause": str(cause),
                "cause_type": type(cause).__name__
            }
        )


class InvalidToolInputError(AgentError):
    """Raised when tool input validation fails."""
    
    def __init__(self, tool_name: str, validation_errors: Dict[str, str]):
        super().__init__(
            ErrorCode.INVALID_TOOL_INPUT,
            f"Invalid input for tool '{tool_name}'",
            {
                "tool_name": tool_name,
                "validation_errors": validation_errors
            }
        )


class LLMError(AgentError):
    """Raised when there's an error with the LLM."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            ErrorCode.LLM_ERROR,
            message,
            details
        )


class ParsingError(AgentError):
    """Raised when parsing LLM output fails."""
    
    def __init__(self, message: str, raw_output: str):
        super().__init__(
            ErrorCode.PARSING_ERROR,
            message,
            {"raw_output": raw_output}
        )


class APIError(AgentError):
    """Raised when an external API call fails."""
    
    def __init__(
        self, 
        api_name: str, 
        message: str, 
        status_code: Optional[int] = None,
        response_body: Optional[str] = None
    ):
        details = {
            "api_name": api_name
        }
        if status_code is not None:
            details["status_code"] = status_code
        if response_body is not None:
            details["response_body"] = response_body
            
        super().__init__(
            ErrorCode.API_ERROR,
            f"API error ({api_name}): {message}",
            details
        )


class ValidationError(AgentError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        details = {}
        if field is not None:
            details["field"] = field
            
        super().__init__(
            ErrorCode.VALIDATION_ERROR,
            message,
            details
        )


class MemoryError(AgentError):
    """Raised when there's an error with the memory store."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            ErrorCode.MEMORY_ERROR,
            message,
            details
        )


class ConfigError(AgentError):
    """Raised when there's an error with the configuration."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            ErrorCode.CONFIG_ERROR,
            message,
            details
        )
