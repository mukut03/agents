# Google Maps Agent - Refactored Implementation

This is a refactored implementation of the Google Maps agent with improved:
- Modularity
- Readability
- Scalability
- Error handling
- Debugging capabilities

## Architecture

The refactored architecture follows these design principles:

1. **Separation of Concerns**: Clear boundaries between different components
2. **Dependency Injection**: Components receive their dependencies rather than creating them
3. **Interface-Based Design**: Components interact through well-defined interfaces
4. **Testability**: Components are designed to be easily testable
5. **Error Handling**: Consistent error handling throughout the codebase
6. **Logging**: Comprehensive logging for debugging and monitoring

## Project Structure

```
agents/refactored/
├── core/                  # Core agent framework
│   ├── agent.py           # Base agent class
│   ├── memory.py          # Memory management
│   ├── tool_executor.py   # Tool execution framework
│   ├── llm_client.py      # LLM client interface
│   └── errors.py          # Error definitions
├── clients/               # External API clients
│   ├── ollama_client.py   # Ollama API client
│   ├── google_maps.py     # Google Maps API client
│   └── overpass.py        # Overpass API client
├── tools/                 # Tool implementations
│   ├── registry.py        # Tool registry
│   ├── routes.py          # Route-related tools
│   ├── places.py          # Place-related tools
│   ├── features.py        # Natural features tools
│   ├── visualization.py   # Map visualization tools
│   └── answer.py          # Answer tool
├── utils/                 # Utility functions
│   ├── logging.py         # Logging utilities
│   ├── validation.py      # Input validation
│   └── geo.py             # Geospatial utilities
├── config/                # Configuration
│   ├── prompts.py         # System prompts
│   ├── tool_specs.py      # Tool specifications
│   └── settings.py        # Global settings
└── googlemaps_agent.py    # Main agent implementation
```

## Usage

```python
from agents.refactored.googlemaps_agent import GoogleMapsAgent

agent = GoogleMapsAgent()
response = agent.process_query("How do I get from San Francisco to Los Angeles?")
print(response)
