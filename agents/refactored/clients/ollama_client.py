"""
Ollama client implementation for the agent framework.

This module provides a client for interacting with the Ollama API.
"""
import requests
import json
import time
from typing import Dict, List, Any, Optional, Iterator, Union

from agents.refactored.core.llm_client import BaseLLMClient
from agents.refactored.core.errors import LLMError


class OllamaClient(BaseLLMClient):
    """
    Client for interacting with the Ollama API.
    
    This client supports both the Ollama-specific API endpoints and the
    OpenAI-compatible endpoints.
    """
    
    def __init__(
        self, 
        base_url: str = "http://localhost:11434", 
        default_model: str = "llama3.2:latest"
    ):
        """
        Initialize the Ollama client.
        
        Args:
            base_url: The base URL of the Ollama API
            default_model: The default model to use for queries
        """
        super().__init__(default_model)
        self.base_url = base_url
        
        # API endpoints
        self.api_generate = f"{base_url}/api/generate"  # Legacy endpoint
        self.api_chat = f"{base_url}/api/chat"
        self.api_completions = f"{base_url}/v1/completions"  # OpenAI-compatible
        self.api_chat_completions = f"{base_url}/v1/chat/completions"  # OpenAI-compatible
    
    def chat(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Send a chat request to the Ollama API.
        
        Args:
            messages: List of message objects with 'role' and 'content'
            model: Optional model to use
            temperature: Controls randomness (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate
            stream: Whether to stream the response
            
        Returns:
            Response from the API
            
        Raises:
            LLMError: If the LLM request fails
        """
        model = model or self.default_model
        
        # Try the Ollama-specific chat endpoint first
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream
        }
        
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        
        try:
            response = requests.post(self.api_chat, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            # If the Ollama-specific endpoint fails, try the OpenAI-compatible endpoint
            try:
                response = requests.post(self.api_chat_completions, json=payload)
                response.raise_for_status()
                openai_response = response.json()
                
                # Convert OpenAI response format to Ollama format
                return {
                    "model": model,
                    "message": {
                        "role": "assistant",
                        "content": openai_response.get("choices", [{}])[0].get("message", {}).get("content", "")
                    },
                    "done": True
                }
            except requests.exceptions.RequestException as e2:
                raise LLMError(
                    f"Failed to call Ollama API: {e}, {e2}",
                    {
                        "model": model,
                        "base_url": self.base_url,
                        "first_error": str(e),
                        "second_error": str(e2)
                    }
                )
    
    def stream_chat(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Iterator[str]:
        """
        Stream a chat response from the Ollama API.
        
        Args:
            messages: List of message objects with 'role' and 'content'
            model: Optional model to use
            temperature: Controls randomness (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate
            
        Yields:
            Chunks of the generated response
            
        Raises:
            LLMError: If the LLM request fails
        """
        model = model or self.default_model
        
        # Try the Ollama-specific chat endpoint first
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": True
        }
        
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        
        try:
            response = requests.post(self.api_chat, json=payload, stream=True)
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    content = chunk.get("message", {}).get("content", "")
                    if content:
                        yield content
        except requests.exceptions.RequestException as e:
            # If the Ollama-specific endpoint fails, try the OpenAI-compatible endpoint
            try:
                response = requests.post(
                    self.api_chat_completions, 
                    json=payload, 
                    stream=True
                )
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if line:
                        try:
                            # Skip empty lines
                            if line.strip() == b'':
                                continue
                            
                            # Handle data: prefix in SSE
                            if line.startswith(b'data: '):
                                line = line[6:]  # Remove 'data: ' prefix
                            
                            # Skip [DONE] message
                            if line.strip() == b'[DONE]':
                                break
                            
                            chunk = json.loads(line)
                            content = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
            except requests.exceptions.RequestException as e2:
                raise LLMError(
                    f"Failed to stream from Ollama API: {e}, {e2}",
                    {
                        "model": model,
                        "base_url": self.base_url,
                        "first_error": str(e),
                        "second_error": str(e2)
                    }
                )
    
    def extract_content(self, response: Dict[str, Any]) -> str:
        """
        Extract the content from an Ollama response.
        
        Args:
            response: The Ollama response
            
        Returns:
            The extracted content as a string
            
        Raises:
            LLMError: If content extraction fails
        """
        try:
            # For Ollama-specific response format
            if "message" in response:
                return response["message"].get("content", "")
            
            # For OpenAI-compatible response format
            if "choices" in response:
                return response["choices"][0].get("message", {}).get("content", "")
            
            # Fallback
            return str(response)
        except Exception as e:
            raise LLMError(f"Failed to extract content from Ollama response: {e}")
    
    def is_available(self) -> bool:
        """
        Check if the Ollama API is available.
        
        Returns:
            True if available, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/version")
            return response.status_code == 200
        except:
            return False
    
    def list_models(self) -> List[Dict[str, Any]]:
        """
        List all available models in the Ollama instance.
        
        Returns:
            A list of available models
            
        Raises:
            LLMError: If the request fails
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            return response.json().get("models", [])
        except requests.exceptions.RequestException as e:
            raise LLMError(f"Failed to list models: {e}")
