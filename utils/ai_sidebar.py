"""
Reusable AI Configuration Sidebar
Auto-detects .env config and allows manual override
"""

import streamlit as st
from core.ai_client import get_unified_client
from config.ai_config import initialize_ai_from_env, get_ai_status


def render_ai_sidebar():
    """
    Render smart AI configuration sidebar
    - Auto-loads from .env if available
    - Allows manual configuration if needed
    - Shows current status
    
    Returns True if AI is configured, False otherwise
    """
    with st.sidebar:
        st.markdown("### 🤖 AI Configuration")
        
        # Initialize from .env on first run
        if 'ai_initialized' not in st.session_state:
            with st.spinner("Initializing AI providers..."):
                init_result = initialize_ai_from_env()
                st.session_state['ai_initialized'] = True
                st.session_state['env_providers'] = init_result['initialized']
        
        # Get current status
        unified_client = get_unified_client()
        available_providers = unified_client.get_available_providers()
        
        # Display current configuration
        if available_providers:
            st.success(f"✅ AI Configured ({len(available_providers)} provider(s))")
            
            # Show active configuration
            with st.expander("📊 Current Configuration", expanded=False):
                info = unified_client.get_provider_info()
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Active Provider", info['active_provider'].upper())
                with col2:
                    st.metric("Model", info['active_model'])
                
                # Show all available providers
                st.markdown("**Available Providers:**")
                for provider in available_providers:
                    models = unified_client.get_available_models(provider)
                    is_active = provider == info['active_provider']
                    status = "🟢" if is_active else "⚪"
                    st.text(f"{status} {provider.upper()}: {len(models)} models")
            
            # Allow switching provider/model
            st.markdown("---")
            st.markdown("**Change Provider:**")
            
            provider_names = {
                "xai": "xAI Grok",
                "groq": "Groq",
                "gemini": "Google Gemini"
            }
            
            # Create display names for available providers
            provider_options = {
                provider_names.get(p, p): p 
                for p in available_providers
            }
            
            selected_display = st.selectbox(
                "Switch to:",
                options=list(provider_options.keys()),
                key="switch_provider"
            )
            selected_provider = provider_options[selected_display]
            
            # Get models for selected provider
            available_models = unified_client.get_available_models(selected_provider)
            
            if available_models:
                selected_model = st.selectbox(
                    "Model:",
                    options=available_models,
                    key=f"switch_model_{selected_provider}"
                )
                
                if st.button("🔄 Switch", use_container_width=True):
                    unified_client.set_active_provider(selected_provider, selected_model)
                    st.success(f"✅ Switched to {selected_display}")
                    st.rerun()
            
            st.session_state['ai_ready'] = True
            return True
        
        else:
            # No providers configured - show manual configuration
            st.warning("⚠️ No AI providers configured")
            st.info("💡 Add API keys to your `.env` file or configure manually below")
            
            with st.expander("📝 Manual Configuration", expanded=True):
                st.markdown("**Add API Key Manually:**")
                
                provider_options = {
                    "xAI Grok": "xai",
                    "Groq": "groq",
                    "Google Gemini": "gemini"
                }
                
                selected_provider_name = st.selectbox(
                    "Provider:",
                    options=list(provider_options.keys()),
                    key="manual_provider_select"
                )
                selected_provider = provider_options[selected_provider_name]
                
                api_key = st.text_input(
                    "API Key:",
                    type="password",
                    placeholder=f"Enter {selected_provider_name} API key...",
                    key=f"manual_api_key_{selected_provider}"
                )
                
                if api_key:
                    try:
                        unified_client.add_client(selected_provider, api_key)
                        
                        # Get available models
                        available_models = unified_client.get_available_models(selected_provider)
                        
                        if available_models:
                            selected_model = st.selectbox(
                                "Model:",
                                options=available_models,
                                key=f"manual_model_{selected_provider}"
                            )
                            
                            if st.button("💾 Save Configuration", use_container_width=True):
                                unified_client.set_active_provider(selected_provider, selected_model)
                                st.session_state['ai_ready'] = True
                                st.success(f"✅ {selected_provider_name} configured!")
                                st.rerun()
                        else:
                            st.error("No models available")
                            
                    except Exception as e:
                        st.error(f"❌ Configuration error: {e}")
            
            # Instructions for .env configuration
            with st.expander("ℹ️ Configure via .env (Recommended)"):
                st.markdown("""
                **For permanent setup, add to your `.env` file:**
```bash
                # AI API Keys
                XAI_API_KEY=xai-your-key-here
                GROQ_API_KEY=gsk_your-key-here
                GEMINI_API_KEY=your-gemini-key-here
                
                # Default provider (optional)
                DEFAULT_AI_PROVIDER=xai
                DEFAULT_AI_MODEL=grok-2-1212
```
                
                Then restart the app.
                """)
                
                st.markdown("**Get API Keys:**")
                st.markdown("- [xAI Console](https://console.x.ai)")
                st.markdown("- [Groq Console](https://console.groq.com)")
                st.markdown("- [Google AI Studio](https://makersuite.google.com/app/apikey)")
            
            st.session_state['ai_ready'] = False
            return False


def check_ai_configured() -> bool:
    """Check if AI is configured and ready"""
    return st.session_state.get('ai_ready', False)


def get_ai_info() -> dict:
    """Get current AI configuration info"""
    unified_client = get_unified_client()
    return {
        'configured': len(unified_client.get_available_providers()) > 0,
        'provider': unified_client.active_provider,
        'model': unified_client.active_model,
        'providers': unified_client.get_available_providers()
    }