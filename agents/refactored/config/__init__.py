"""
Configuration for the agent framework.

This package provides configuration for the agent framework.
"""
from agents.refactored.config.prompts import (
    BASE_SYSTEM_PROMPT,
    GOOGLEMAPS_SYSTEM_PROMPT,
    MOCK_SYSTEM_PROMPT
)
from agents.refactored.config.tool_specs import (
    GOOGLEMAPS_TOOL_SPECS,
    MOCK_TOOL_SPECS
)
from agents.refactored.config.settings import (
    get_settings,
    get_log_level,
    DEFAULT_SETTINGS
)
