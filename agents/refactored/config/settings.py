"""
Global settings for the agent framework.

This module provides global settings that can be used throughout the agent framework.
"""
from typing import Dict, Any, Optional
import os
import json
import logging


# Default settings
DEFAULT_SETTINGS = {
    # LLM settings
    "llm": {
        "provider": "ollama",  # ollama, openai, etc.
        "model": "llama3.2:latest",
        "temperature": 0.7,
        "max_tokens": None,
        "api_base": "http://localhost:11434",
        "api_key": None,
    },
    
    # Agent settings
    "agent": {
        "max_iterations": 10,
        "debug": False,
        "memory_max_messages": 100,
    },
    
    # Logging settings
    "logging": {
        "level": "INFO",
        "console_output": True,
        "file_output": False,
        "log_dir": "logs",
        "structured": False,
    },
    
    # Google Maps settings
    "google_maps": {
        "api_key": None,  # Set via environment variable GOOGLE_MAPS_API_KEY
    },
    
    # Overpass API settings
    "overpass": {
        "api_url": "http://overpass-api.de/api/interpreter",
        "timeout": 60,
    },
    
    # Visualization settings
    "visualization": {
        "output_dir": ".",
        "default_map_file": "route_map.html",
    },
}


# Load settings from environment variables
def load_from_env(settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Load settings from environment variables.
    
    Args:
        settings: The current settings
        
    Returns:
        The updated settings
    """
    # LLM settings
    if os.environ.get("LLM_PROVIDER"):
        settings["llm"]["provider"] = os.environ.get("LLM_PROVIDER")
    
    if os.environ.get("LLM_MODEL"):
        settings["llm"]["model"] = os.environ.get("LLM_MODEL")
    
    if os.environ.get("LLM_TEMPERATURE"):
        settings["llm"]["temperature"] = float(os.environ.get("LLM_TEMPERATURE"))
    
    if os.environ.get("LLM_API_BASE"):
        settings["llm"]["api_base"] = os.environ.get("LLM_API_BASE")
    
    if os.environ.get("LLM_API_KEY"):
        settings["llm"]["api_key"] = os.environ.get("LLM_API_KEY")
    
    # Agent settings
    if os.environ.get("AGENT_MAX_ITERATIONS"):
        settings["agent"]["max_iterations"] = int(os.environ.get("AGENT_MAX_ITERATIONS"))
    
    if os.environ.get("AGENT_DEBUG"):
        settings["agent"]["debug"] = os.environ.get("AGENT_DEBUG").lower() == "true"
    
    # Logging settings
    if os.environ.get("LOG_LEVEL"):
        settings["logging"]["level"] = os.environ.get("LOG_LEVEL")
    
    if os.environ.get("LOG_FILE_OUTPUT"):
        settings["logging"]["file_output"] = os.environ.get("LOG_FILE_OUTPUT").lower() == "true"
    
    if os.environ.get("LOG_DIR"):
        settings["logging"]["log_dir"] = os.environ.get("LOG_DIR")
    
    # Google Maps settings
    if os.environ.get("GOOGLE_MAPS_API_KEY"):
        settings["google_maps"]["api_key"] = os.environ.get("GOOGLE_MAPS_API_KEY")
    
    # Overpass API settings
    if os.environ.get("OVERPASS_API_URL"):
        settings["overpass"]["api_url"] = os.environ.get("OVERPASS_API_URL")
    
    return settings


# Load settings from a JSON file
def load_from_file(file_path: str, settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Load settings from a JSON file.
    
    Args:
        file_path: The path to the JSON file
        settings: The current settings
        
    Returns:
        The updated settings
    """
    try:
        with open(file_path, "r") as f:
            file_settings = json.load(f)
        
        # Merge file settings with current settings
        for section, section_settings in file_settings.items():
            if section in settings:
                settings[section].update(section_settings)
            else:
                settings[section] = section_settings
    except FileNotFoundError:
        logging.warning(f"Settings file not found: {file_path}")
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON in settings file: {file_path}")
    except Exception as e:
        logging.error(f"Error loading settings from file: {e}")
    
    return settings


# Get the global settings
def get_settings(
    config_file: Optional[str] = None,
    use_env: bool = True
) -> Dict[str, Any]:
    """
    Get the global settings.
    
    Args:
        config_file: Optional path to a JSON configuration file
        use_env: Whether to load settings from environment variables
        
    Returns:
        The global settings
    """
    # Start with default settings
    settings = DEFAULT_SETTINGS.copy()
    
    # Load settings from file if provided
    if config_file:
        settings = load_from_file(config_file, settings)
    
    # Load settings from environment variables if requested
    if use_env:
        settings = load_from_env(settings)
    
    return settings


# Convert string log level to int
def get_log_level(level_str: str) -> int:
    """
    Convert a string log level to the corresponding int value.
    
    Args:
        level_str: The string log level
        
    Returns:
        The int log level
    """
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    return level_map.get(level_str.upper(), logging.INFO)
