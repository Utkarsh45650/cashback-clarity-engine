"""
LLM Service - Ollama Integration
Handles communication with local Ollama instance running llama3
"""
import requests
import json
from typing import Optional

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"
TIMEOUT = 30


def call_ollama(prompt: str) -> Optional[str]:
    """
    Call Ollama API with given prompt.
    
    Args:
        prompt: The text prompt to send to the model
        
    Returns:
        The model's response text, or None if request fails
        
    Raises:
        ConnectionError if Ollama is not running
    """
    try:
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "temperature": 0.3,  # Lower temperature for more consistent answers
        }
        
        response = requests.post(
            OLLAMA_API_URL,
            json=payload,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "").strip()
        else:
            error_msg = f"Ollama API error: {response.status_code}"
            print(f"ERROR: {error_msg}")
            return None
            
    except requests.exceptions.ConnectionError:
        error_msg = "ERROR: Ollama is not running. Start Ollama with: ollama serve"
        print(error_msg)
        return None
    except requests.exceptions.Timeout:
        error_msg = "ERROR: Ollama request timed out. Check server status."
        print(error_msg)
        return None
    except Exception as e:
        error_msg = f"ERROR: Failed to call Ollama: {str(e)}"
        print(error_msg)
        return None


def is_ollama_available() -> bool:
    """Check if Ollama service is available"""
    try:
        response = requests.get(
            "http://localhost:11434/api/tags",
            timeout=5
        )
        return response.status_code == 200
    except:
        return False


if __name__ == "__main__":
    # Test the Ollama connection
    if is_ollama_available():
        print("✓ Ollama is running")
        result = call_ollama("What is 2+2?")
        print(f"Response: {result}")
    else:
        print("✗ Ollama is not running. Please start it with: ollama serve")
