"""
Memory management for the agent framework.

This module provides memory management capabilities for storing conversation history,
intermediate tool outputs, and other contextual information needed by the agent.
"""
from typing import Dict, List, Any, Optional, TypeVar, Generic, Callable
from datetime import datetime
import json
import copy

from agents.refactored.core.errors import MemoryError


T = TypeVar('T')


class MemoryItem(Generic[T]):
    """A single item in memory with metadata."""
    
    def __init__(self, key: str, value: T, metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a memory item.
        
        Args:
            key: The key for the item
            value: The value of the item
            metadata: Optional metadata for the item
        """
        self.key = key
        self.value = value
        self.metadata = metadata or {}
        self.created_at = datetime.now()
        self.updated_at = self.created_at
    
    def update(self, value: T, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Update the value and optionally the metadata of the item.
        
        Args:
            value: The new value
            metadata: Optional new metadata to merge with existing metadata
        """
        self.value = value
        if metadata:
            self.metadata.update(metadata)
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the memory item to a dictionary."""
        return {
            "key": self.key,
            "value": self.value,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class Message:
    """A message in the conversation history."""
    
    def __init__(
        self, 
        role: str, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a message.
        
        Args:
            role: The role of the message sender (e.g., "user", "assistant", "system")
            content: The content of the message
            metadata: Optional metadata for the message
        """
        self.role = role
        self.content = content
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the message to a dictionary."""
        return {
            "role": self.role,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }
    
    def to_llm_format(self) -> Dict[str, str]:
        """Convert the message to the format expected by LLMs."""
        return {
            "role": self.role,
            "content": self.content
        }


class ConversationHistory:
    """Manages the conversation history."""
    
    def __init__(self, max_messages: int = 100):
        """
        Initialize the conversation history.
        
        Args:
            max_messages: Maximum number of messages to keep in history
        """
        self.messages: List[Message] = []
        self.max_messages = max_messages
    
    def add(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a message to the conversation history.
        
        Args:
            role: The role of the message sender
            content: The content of the message
            metadata: Optional metadata for the message
        """
        message = Message(role, content, metadata)
        self.messages.append(message)
        
        # Trim history if it exceeds max_messages
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def get_messages(self, include_roles: Optional[List[str]] = None) -> List[Message]:
        """
        Get messages from the conversation history, optionally filtered by role.
        
        Args:
            include_roles: Optional list of roles to include
            
        Returns:
            List of messages
        """
        if include_roles is None:
            return copy.deepcopy(self.messages)
        
        return [msg for msg in self.messages if msg.role in include_roles]
    
    def get_last_n_messages(self, n: int) -> List[Message]:
        """
        Get the last n messages from the conversation history.
        
        Args:
            n: Number of messages to retrieve
            
        Returns:
            List of the last n messages
        """
        return copy.deepcopy(self.messages[-n:]) if n > 0 else []
    
    def clear(self) -> None:
        """Clear the conversation history."""
        self.messages = []
    
    def to_llm_format(self) -> List[Dict[str, str]]:
        """
        Convert the conversation history to the format expected by LLMs.
        
        Returns:
            List of message dictionaries in LLM format
        """
        return [msg.to_llm_format() for msg in self.messages]


class MemoryStore:
    """
    Memory store for the agent.
    
    Provides storage for both conversation history and key-value data.
    """
    
    def __init__(self, max_conversation_history: int = 100):
        """
        Initialize the memory store.
        
        Args:
            max_conversation_history: Maximum number of messages to keep in conversation history
        """
        self.conversation = ConversationHistory(max_messages=max_conversation_history)
        self.data: Dict[str, MemoryItem] = {}
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a message to the conversation history.
        
        Args:
            role: The role of the message sender
            content: The content of the message
            metadata: Optional metadata for the message
        """
        self.conversation.add(role, content, metadata)
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get the conversation history in LLM format.
        
        Returns:
            List of message dictionaries in LLM format
        """
        return self.conversation.to_llm_format()
    
    def remember(self, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Store a value in memory.
        
        Args:
            key: The key to store the value under
            value: The value to store
            metadata: Optional metadata for the value
        """
        if key in self.data:
            self.data[key].update(value, metadata)
        else:
            self.data[key] = MemoryItem(key, value, metadata)
    
    def recall(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from memory.
        
        Args:
            key: The key to retrieve
            
        Returns:
            The value if found, None otherwise
        """
        item = self.data.get(key)
        return item.value if item else None
    
    def recall_with_metadata(self, key: str) -> Optional[MemoryItem]:
        """
        Retrieve a value with its metadata from memory.
        
        Args:
            key: The key to retrieve
            
        Returns:
            The MemoryItem if found, None otherwise
        """
        return copy.deepcopy(self.data.get(key))
    
    def forget(self, key: str) -> bool:
        """
        Remove a value from memory.
        
        Args:
            key: The key to remove
            
        Returns:
            True if the key was found and removed, False otherwise
        """
        if key in self.data:
            del self.data[key]
            return True
        return False
    
    def has_key(self, key: str) -> bool:
        """
        Check if a key exists in memory.
        
        Args:
            key: The key to check
            
        Returns:
            True if the key exists, False otherwise
        """
        return key in self.data
    
    def get_all_keys(self) -> List[str]:
        """
        Get all keys in memory.
        
        Returns:
            List of all keys
        """
        return list(self.data.keys())
    
    def clear_data(self) -> None:
        """Clear all data from memory."""
        self.data = {}
    
    def clear_all(self) -> None:
        """Clear all data and conversation history from memory."""
        self.clear_data()
        self.conversation.clear()
    
    def to_json(self) -> str:
        """
        Serialize the memory store to JSON.
        
        Returns:
            JSON string representation of the memory store
        
        Raises:
            MemoryError: If serialization fails
        """
        try:
            data_dict = {k: v.to_dict() for k, v in self.data.items()}
            messages = [msg.to_dict() for msg in self.conversation.messages]
            
            memory_dict = {
                "data": data_dict,
                "conversation": messages
            }
            
            return json.dumps(memory_dict)
        except Exception as e:
            raise MemoryError(f"Failed to serialize memory to JSON: {str(e)}")
    
    @classmethod
    def from_json(cls, json_str: str) -> 'MemoryStore':
        """
        Create a memory store from a JSON string.
        
        Args:
            json_str: JSON string representation of a memory store
            
        Returns:
            A new MemoryStore instance
            
        Raises:
            MemoryError: If deserialization fails
        """
        try:
            memory_dict = json.loads(json_str)
            memory_store = cls()
            
            # Restore data
            for key, item_dict in memory_dict.get("data", {}).items():
                value = item_dict.get("value")
                metadata = item_dict.get("metadata", {})
                memory_store.remember(key, value, metadata)
            
            # Restore conversation
            for msg_dict in memory_dict.get("conversation", []):
                role = msg_dict.get("role", "")
                content = msg_dict.get("content", "")
                metadata = msg_dict.get("metadata", {})
                memory_store.add_message(role, content, metadata)
            
            return memory_store
        except Exception as e:
            raise MemoryError(f"Failed to deserialize memory from JSON: {str(e)}")
