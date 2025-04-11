"""
LLM client interface for the agent framework.

This module provides the LLM client interface and a base implementation.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Iterator, Union


class LLMClient(ABC):
    """
    Abstract base class for LLM clients.
    
    This class defines the interface that all LLM clients must implement.
    """
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the LLM client is available.
        
        Returns:
            True if the client is available, False otherwise
        """
        pass
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Any:
        """
        Send a chat request to the LLM.
        
        Args:
            messages: The messages to send to the LLM
            **kwargs: Additional arguments to pass to the LLM
            
        Returns:
            The LLM response
        """
        pass
    
    @abstractmethod
    def stream_chat(self, messages: List[Dict[str, str]], **kwargs) -> Iterator[str]:
        """
        Send a streaming chat request to the LLM.
        
        Args:
            messages: The messages to send to the LLM
            **kwargs: Additional arguments to pass to the LLM
            
        Returns:
            An iterator of response chunks
        """
        pass
    
    @abstractmethod
    def extract_content(self, response: Any) -> str:
        """
        Extract the content from an LLM response.
        
        Args:
            response: The LLM response
            
        Returns:
            The extracted content
        """
        pass


class BaseLLMClient(LLMClient):
    """
    Base implementation of the LLM client interface.
    
    This class provides a base implementation of the LLM client interface
    that can be extended by specific LLM client implementations.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize the base LLM client.
        
        Args:
            **kwargs: Additional arguments for the client
        """
        self.kwargs = kwargs
    
    def is_available(self) -> bool:
        """
        Check if the LLM client is available.
        
        Returns:
            True if the client is available, False otherwise
        """
        return True
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Any:
        """
        Send a chat request to the LLM.
        
        Args:
            messages: The messages to send to the LLM
            **kwargs: Additional arguments to pass to the LLM
            
        Returns:
            The LLM response
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    def stream_chat(self, messages: List[Dict[str, str]], **kwargs) -> Iterator[str]:
        """
        Send a streaming chat request to the LLM.
        
        Args:
            messages: The messages to send to the LLM
            **kwargs: Additional arguments to pass to the LLM
            
        Returns:
            An iterator of response chunks
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    def extract_content(self, response: Any) -> str:
        """
        Extract the content from an LLM response.
        
        Args:
            response: The LLM response
            
        Returns:
            The extracted content
        """
        if isinstance(response, str):
            return response
        elif isinstance(response, dict) and "content" in response:
            return response["content"]
        elif isinstance(response, dict) and "choices" in response:
            return response["choices"][0]["message"]["content"]
        else:
            return str(response)


class MockLLMClient(BaseLLMClient):
    """
    Mock LLM client for testing.
    
    This class provides a mock implementation of the LLM client interface
    that can be used for testing.
    """
    
    def __init__(self, responses: Optional[List[str]] = None, **kwargs):
        """
        Initialize the mock LLM client.
        
        Args:
            responses: Optional list of responses to return
            **kwargs: Additional arguments for the client
        """
        super().__init__(**kwargs)
        self.responses = responses or ["This is a mock response."]
        self.response_index = 0
    
    def is_available(self) -> bool:
        """
        Check if the mock LLM client is available.
        
        Returns:
            Always returns True
        """
        return True
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Send a chat request to the mock LLM.
        
        Args:
            messages: The messages to send to the LLM
            **kwargs: Additional arguments to pass to the LLM
            
        Returns:
            A mock response
        """
        response = self.responses[self.response_index % len(self.responses)]
        self.response_index += 1
        
        return {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": response
                    }
                }
            ]
        }
    
    def stream_chat(self, messages: List[Dict[str, str]], **kwargs) -> Iterator[str]:
        """
        Send a streaming chat request to the mock LLM.
        
        Args:
            messages: The messages to send to the LLM
            **kwargs: Additional arguments to pass to the LLM
            
        Returns:
            An iterator of response chunks
        """
        response = self.responses[self.response_index % len(self.responses)]
        self.response_index += 1
        
        # Split the response into chunks of 10 characters
        chunk_size = 10
        for i in range(0, len(response), chunk_size):
            yield response[i:i+chunk_size]
    
    def extract_content(self, response: Any) -> str:
        """
        Extract the content from a mock LLM response.
        
        Args:
            response: The mock LLM response
            
        Returns:
            The extracted content
        """
        return super().extract_content(response)
    
    def set_responses(self, responses: List[str]) -> None:
        """
        Set the responses to return.
        
        Args:
            responses: The responses to return
        """
        self.responses = responses
        self.response_index = 0
