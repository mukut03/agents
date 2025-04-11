#!/usr/bin/env python3
"""
Test script for checking the connection to Ollama.
This script tests if the OllamaClient can connect to the Ollama API.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import the modules
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from agents.ollama_client import OllamaClient

def test_ollama_connection():
    """
    Test the connection to Ollama.
    """
    print("Testing connection to Ollama...")
    
    # Create the client
    client = OllamaClient()
    
    # Check if Ollama is available
    is_available = client.is_available()
    print(f"Ollama is available: {is_available}")
    
    if is_available:
        # List available models
        print("\nListing available models...")
        models = client.list_models()
        if models:
            print("Available models:")
            for model in models:
                print(f" - {model.get('name')}")
        else:
            print("No models found.")
        
        # Test a simple query
        print("\nTesting a simple query...")
        try:
            response = client.query("Hello, world!")
            print(f"Response: {response.get('response')}")
            print("Query test successful!")
        except Exception as e:
            print(f"Error testing query: {e}")
    
    return is_available

def main():
    """
    Main function to run the test.
    """
    print("OLLAMA CONNECTION TEST")
    print("=====================")
    
    # Test the connection
    success = test_ollama_connection()
    
    # Print the result
    print("\nTEST RESULT")
    print("===========")
    print(f"Connection to Ollama: {'PASS' if success else 'FAIL'}")
    
    if success:
        print("\nThe connection to Ollama is working correctly.")
    else:
        print("\nThe connection to Ollama failed. Please check that Ollama is running.")
        print("You can start Ollama by running the 'ollama serve' command.")
        print("You can download Ollama from: https://ollama.ai/")

if __name__ == "__main__":
    main()
