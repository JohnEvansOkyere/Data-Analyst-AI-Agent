"""
VexaAI Data Analyst - Multi-Model AI Client
Supports: xAI Grok, Groq, Google Gemini
"""

import requests
from typing import Dict, List, Optional
from abc import ABC, abstractmethod
from utils.logger import get_logger

logger = get_logger(__name__)


class BaseAIClient(ABC):
    """Base class for all AI clients"""
    
    @abstractmethod
    def chat_completion(self, messages: List[Dict], **kwargs) -> Dict:
        """Generate chat completion"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        pass


class XAIClient(BaseAIClient):
    """xAI Grok API Client"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.x.ai/v1"
        self.provider = "xAI"
        
    def chat_completion(self, messages: List[Dict], model: str = "grok-2-1212", 
                       max_tokens: int = 500, temperature: float = 0.1) -> Dict:
        """Generate chat completion using xAI Grok"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            logger.info(f"✅ xAI ({model}) request successful")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ xAI API error: {str(e)}")
            raise Exception(f"xAI API error: {str(e)}")
    
    def get_available_models(self) -> List[str]:
        """Get available xAI models"""
        return [
            "grok-2-1212",
            "grok-2-vision-1212", 
            "grok-beta",
            "grok-vision-beta"
        ]


class GroqClient(BaseAIClient):
    """Groq API Client"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.groq.com/openai/v1"
        self.provider = "Groq"
        
    def chat_completion(self, messages: List[Dict], model: str = "llama-3.3-70b-versatile",
                       max_tokens: int = 500, temperature: float = 0.1) -> Dict:
        """Generate chat completion using Groq"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            logger.info(f"✅ Groq ({model}) request successful")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Groq API error: {str(e)}")
            raise Exception(f"Groq API error: {str(e)}")
    
    def get_available_models(self) -> List[str]:
        """Get available Groq models"""
        return [
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma2-9b-it"
        ]


class GeminiClient(BaseAIClient):
    """Google Gemini API Client"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.provider = "Gemini"
        
    def chat_completion(self, messages: List[Dict], model: str = "gemini-1.5-flash",
                       max_tokens: int = 500, temperature: float = 0.1) -> Dict:
        """Generate chat completion using Gemini"""
        
        # Convert OpenAI format messages to Gemini format
        gemini_messages = self._convert_messages(messages)
        
        url = f"{self.base_url}/models/{model}:generateContent?key={self.api_key}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "contents": gemini_messages,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            # Convert Gemini response to OpenAI format
            converted_result = self._convert_response(result)
            logger.info(f"✅ Gemini ({model}) request successful")
            return converted_result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Gemini API error: {str(e)}")
            raise Exception(f"Gemini API error: {str(e)}")
    
    def _convert_messages(self, messages: List[Dict]) -> List[Dict]:
        """Convert OpenAI format to Gemini format"""
        gemini_messages = []
        for msg in messages:
            role = "user" if msg["role"] in ["user", "system"] else "model"
            gemini_messages.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
        return gemini_messages
    
    def _convert_response(self, response: Dict) -> Dict:
        """Convert Gemini response to OpenAI format"""
        try:
            text = response["candidates"][0]["content"]["parts"][0]["text"]
            return {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": text
                    }
                }]
            }
        except (KeyError, IndexError) as e:
            logger.error(f"Error parsing Gemini response: {e}")
            raise Exception(f"Error parsing Gemini response: {e}")
    
    def get_available_models(self) -> List[str]:
        """Get available Gemini models"""
        return [
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-pro"
        ]


class UnifiedAIClient:
    """
    Unified client that manages multiple AI providers
    Supports: xAI Grok, Groq, Google Gemini
    """
    
    def __init__(self):
        self.clients: Dict[str, BaseAIClient] = {}
        self.active_provider = None
        self.active_model = None
        
    def add_client(self, provider: str, api_key: str):
        """Add an AI provider client"""
        provider_lower = provider.lower()
        
        try:
            if provider_lower in ["xai", "grok"]:
                self.clients["xai"] = XAIClient(api_key)
                logger.info("✅ xAI client initialized")
                
            elif provider_lower == "groq":
                self.clients["groq"] = GroqClient(api_key)
                logger.info("✅ Groq client initialized")
                
            elif provider_lower == "gemini":
                self.clients["gemini"] = GeminiClient(api_key)
                logger.info("✅ Gemini client initialized")
                
            else:
                raise ValueError(f"Unknown provider: {provider}")
                
        except Exception as e:
            logger.error(f"❌ Error adding {provider} client: {e}")
            raise
    
    def set_active_provider(self, provider: str, model: str = None):
        """Set the active AI provider and model"""
        provider_lower = provider.lower()
        
        if provider_lower not in self.clients:
            raise ValueError(f"Provider {provider} not initialized. Add it first with add_client()")
        
        self.active_provider = provider_lower
        
        # Set default model if not provided
        if model is None:
            if provider_lower == "xai":
                model = "grok-2-1212"
            elif provider_lower == "groq":
                model = "llama-3.3-70b-versatile"
            elif provider_lower == "gemini":
                model = "gemini-1.5-flash"
        
        self.active_model = model
        logger.info(f"✅ Active provider set to: {provider} ({model})")
    
    def chat_completion(self, messages: List[Dict], max_tokens: int = 500, 
                       temperature: float = 0.1, **kwargs) -> Dict:
        """
        Generate chat completion using active provider
        Falls back to other providers if active one fails
        """
        if not self.active_provider:
            raise ValueError("No active provider set. Use set_active_provider() first")
        
        # Try active provider first
        try:
            client = self.clients[self.active_provider]
            return client.chat_completion(
                messages=messages,
                model=self.active_model,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
        except Exception as e:
            logger.warning(f"⚠️ {self.active_provider} failed: {e}")
            
            # Try fallback to other providers
            for provider_name, client in self.clients.items():
                if provider_name != self.active_provider:
                    try:
                        logger.info(f"🔄 Trying fallback provider: {provider_name}")
                        models = client.get_available_models()
                        return client.chat_completion(
                            messages=messages,
                            model=models[0],  # Use first available model
                            max_tokens=max_tokens,
                            temperature=temperature,
                            **kwargs
                        )
                    except Exception as fallback_error:
                        logger.warning(f"⚠️ {provider_name} fallback failed: {fallback_error}")
                        continue
            
            # All providers failed
            raise Exception(f"All AI providers failed. Last error: {e}")
    
    def get_available_providers(self) -> List[str]:
        """Get list of initialized providers"""
        return list(self.clients.keys())
    
    def get_available_models(self, provider: str = None) -> List[str]:
        """Get available models for a provider"""
        if provider is None:
            provider = self.active_provider
        
        if provider not in self.clients:
            return []
        
        return self.clients[provider].get_available_models()
    
    def get_provider_info(self) -> Dict:
        """Get info about current configuration"""
        return {
            "active_provider": self.active_provider,
            "active_model": self.active_model,
            "available_providers": self.get_available_providers(),
            "total_providers": len(self.clients)
        }


# Global unified client instance
_unified_client = None


def get_unified_client() -> UnifiedAIClient:
    """Get or create the global unified AI client"""
    global _unified_client
    if _unified_client is None:
        _unified_client = UnifiedAIClient()
    return _unified_client