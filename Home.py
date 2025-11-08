"""
VexaAI Data Analyst Pro - Main Application
Professional Data Science Platform with MLOps Practices
"""
import streamlit as st
import sys
from pathlib import Path
from dotenv import load_dotenv
import os
from database.supabase_manager import get_supabase_manager
from utils.logger import get_logger

# --- Setup ---
sys.path.insert(0, str(Path(__file__).parent))
logger = get_logger(__name__)

# Load .env file (must be in project root)
load_dotenv()

# --- Initialize Supabase ---
if "supabase_client" not in st.session_state:
    try:
        supabase_manager = get_supabase_manager()
        if supabase_manager.is_connected():
            st.session_state.supabase_client = supabase_manager.client
            logger.info("✅ Supabase client initialized successfully.")
            print("✅ Supabase client initialized successfully.")
        else:
            st.session_state.supabase_client = None
            logger.warning("⚠️ Supabase credentials missing or invalid.")
            print("⚠️ Supabase credentials missing or invalid.")
    except Exception as e:
        st.session_state.supabase_client = None
        logger.error(f"❌ Error initializing Supabase: {e}")
        print(f"❌ Error initializing Supabase: {e}")

# Import after Supabase initialization
from core.auth import check_authentication
from config.settings import APP_NAME, APP_VERSION, APP_AUTHOR


# Page configuration
st.set_page_config(
    page_title=f"{APP_NAME} v{APP_VERSION}",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main {
        padding-top: 1rem;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        font-family: 'Inter', sans-serif;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
    }
    
    .feature-card h3 {
        color: #667eea;
        margin-bottom: 1rem;
    }
    
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stats-card h2 {
        font-size: 2.5rem;
        margin: 0;
        font-weight: 700;
    }
    
    .stats-card p {
        margin: 0.5rem 0 0 0;
        font-size: 1rem;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Check authentication
   # Get Supabase client if configured
# Retrieve Supabase client from session
    supabase_client = st.session_state.get("supabase_client", None)

    # Authentication check
    if not check_authentication(supabase_client):
        return

    
    
    # Header
    st.markdown(f"""
    <div class="main-header">
        <h1>🤖 {APP_NAME}</h1>
        <p style="font-size: 1.3rem;">Professional Data Science Platform with MLOps Practices</p>
        <p style="font-size: 1rem; opacity: 0.9;">Version {APP_VERSION} | By {APP_AUTHOR}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Welcome message
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"### 👋 Welcome back, **{st.session_state.username}**!")
        st.markdown("---")
    
    # Platform statistics
    st.markdown("### 📊 Platform Capabilities")
    stat_cols = st.columns(4)
    
    with stat_cols[0]:
        st.markdown("""
        <div class="stats-card">
            <h2>15+</h2>
            <p>Preprocessing<br>Techniques</p>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_cols[1]:
        st.markdown("""
        <div class="stats-card">
            <h2>20+</h2>
            <p>Feature Engineering<br>Operations</p>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_cols[2]:
        st.markdown("""
        <div class="stats-card">
            <h2>10+</h2>
            <p>Statistical<br>Tests</p>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_cols[3]:
        st.markdown("""
        <div class="stats-card">
            <h2>∞</h2>
            <p>AI-Powered<br>Insights</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Feature showcase
    st.markdown("### 🚀 Key Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🧹 Advanced Data Cleaning</h3>
            <p>Comprehensive preprocessing with multiple strategies for handling missing data, outliers, duplicates, and more.</p>
            <ul>
                <li>9 missing data handling strategies</li>
                <li>3 outlier detection methods</li>
                <li>Automated data type conversion</li>
                <li>Text cleaning and normalization</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3>📈 Advanced Analytics</h3>
            <p>Statistical testing and comprehensive analysis capabilities.</p>
            <ul>
                <li>T-tests, ANOVA, Chi-square tests</li>
                <li>Correlation analysis</li>
                <li>Normality testing</li>
                <li>Multicollinearity detection</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3>📊 Interactive Visualizations</h3>
            <p>Auto-generated charts and custom visualizations.</p>
            <ul>
                <li>10+ chart types</li>
                <li>Interactive plots with Plotly</li>
                <li>Correlation heatmaps</li>
                <li>Distribution analysis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>⚙️ Feature Engineering</h3>
            <p>Advanced feature creation and transformation tools.</p>
            <ul>
                <li>Polynomial features</li>
                <li>Interaction features</li>
                <li>Mathematical transformations</li>
                <li>Date feature extraction</li>
                <li>Rolling window features</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3>🤖 AI-Powered Insights</h3>
            <p>Natural language queries powered by Grok AI.</p>
            <ul>
                <li>Convert questions to SQL</li>
                <li>Automated insights generation</li>
                <li>Ultra-fast Grok reasoning</li>
                <li>Multiple AI models available</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3>💾 Data Management</h3>
            <p>Supabase integration for persistent storage.</p>
            <ul>
                <li>Save and version datasets</li>
                <li>Track analysis history</li>
                <li>Export in multiple formats</li>
                <li>Audit logging</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick start guide
    st.markdown("---")
    st.markdown("### 🎯 Quick Start Guide")
    
    with st.expander("📖 How to Get Started", expanded=True):
        st.markdown("""
        **Step 1: Configure API**
        - Get your xAI API key from [x.ai](https://x.ai) or [console.x.ai](https://console.x.ai)
        - Enter it in the sidebar (on any page)
        
        **Step 2: Upload Data**
        - Go to "📂 Data Upload" page
        - Upload CSV or Excel file (up to 200MB)
        - View data preview and statistics
        
        **Step 3: Clean Your Data**
        - Navigate to "🧹 Data Cleaning" page
        - Apply preprocessing techniques
        - Handle missing values, outliers, duplicates
        - Engineer new features
        
        **Step 4: Analyze & Visualize**
        - Use "📈 Analysis & Insights" for statistical analysis
        - Explore "📊 Visualizations" for interactive charts
        - Check "🎛️ Dashboard" for comprehensive overview
        
        **Step 5: Query with AI**
        - Ask questions in natural language
        - Get instant SQL queries and insights
        - Download results and reports
        """)
    
    # Navigation tips
    st.markdown("### 🧭 Navigation")
    nav_cols = st.columns(3)
    
    with nav_cols[0]:
        st.info("📂 **Data Upload**: Upload and explore your data")
    
    with nav_cols[1]:
        st.info("🧹 **Data Cleaning**: Preprocess and engineer features")
    
    with nav_cols[2]:
        st.info("📈 **Analysis**: Statistical tests and AI insights")
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
    border-radius: 15px; color: white;">
        <h4>🤖 {APP_NAME}</h4>
        <p>Empowering data-driven decisions with AI and MLOps</p>
        <p><strong>Developed by {APP_AUTHOR}</strong> | VexaAI © 2025</p>
        <p><small>Built with ❤️ using Streamlit, Grok AI, Supabase, and Modern MLOps</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
