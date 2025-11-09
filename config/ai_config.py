"""
AI Configuration Manager
Auto-loads API keys from .env and initializes providers
"""

import os
from dotenv import load_dotenv
from core.ai_client import get_unified_client
from utils.logger import get_logger

logger = get_logger(__name__)

# Load environment variables
load_dotenv()


def initialize_ai_from_env():
    """
    Initialize AI providers from environment variables
    Returns dict with initialization status
    """
    unified_client = get_unified_client()
    initialized_providers = []
    errors = []
    
    # xAI / Grok
    xai_key = os.getenv("XAI_API_KEY")
    if xai_key and xai_key.strip():
        try:
            if "xai" not in unified_client.get_available_providers():
                unified_client.add_client("xai", xai_key)
                logger.info("✅ xAI initialized from .env")
                initialized_providers.append("xai")
        except Exception as e:
            logger.warning(f"Failed to initialize xAI from .env: {e}")
            errors.append(("xai", str(e)))
    
    # Groq
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key and groq_key.strip():
        try:
            if "groq" not in unified_client.get_available_providers():
                unified_client.add_client("groq", groq_key)
                logger.info("✅ Groq initialized from .env")
                initialized_providers.append("groq")
        except Exception as e:
            logger.warning(f"Failed to initialize Groq from .env: {e}")
            errors.append(("groq", str(e)))
    
    # Gemini
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key and gemini_key.strip():
        try:
            if "gemini" not in unified_client.get_available_providers():
                unified_client.add_client("gemini", gemini_key)
                logger.info("✅ Gemini initialized from .env")
                initialized_providers.append("gemini")
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini from .env: {e}")
            errors.append(("gemini", str(e)))
    
    # Set default provider if specified
    if initialized_providers:
        default_provider = os.getenv("DEFAULT_AI_PROVIDER", initialized_providers[0])
        default_model = os.getenv("DEFAULT_AI_MODEL")
        
        if default_provider in initialized_providers:
            try:
                unified_client.set_active_provider(default_provider, default_model)
                logger.info(f"✅ Default provider set to: {default_provider}")
            except Exception as e:
                logger.warning(f"Failed to set default provider: {e}")
                # Fallback to first available
                unified_client.set_active_provider(initialized_providers[0])
    
    return {
        "initialized": initialized_providers,
        "errors": errors,
        "has_providers": len(initialized_providers) > 0
    }


def get_ai_status():
    """
    Get current AI configuration status
    Returns dict with status information
    """
    unified_client = get_unified_client()
    available_providers = unified_client.get_available_providers()
    
    return {
        "configured": len(available_providers) > 0,
        "providers": available_providers,
        "active_provider": unified_client.active_provider,
        "active_model": unified_client.active_model,
        "source": "env" if len(available_providers) > 0 else "none"
    }