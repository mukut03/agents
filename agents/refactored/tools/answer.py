"""
Answer tool for the agent framework.

This module provides the answer tool, which is used to provide a natural language
answer to the user.
"""
from typing import Dict, Any, Optional
from agents.refactored.core.tool_executor import tool


@tool(
    name="answer",
    description="Provide a natural language answer using memory and reasoning."
)
def answer(text: str) -> str:
    """
    Provide a natural language answer to the user.
    
    This tool is used when the LLM decides no external tool is needed and wants
    to provide a direct answer based on its reasoning and memory.
    
    Args:
        text: The answer text to provide to the user
        
    Returns:
        The answer text
    """
    return text
