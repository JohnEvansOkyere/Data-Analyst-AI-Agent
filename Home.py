"""
VexaAI Data Analyst Pro - Main Application
Professional Data Science Platform with MLOps Practices
"""

import streamlit as st
import sys
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent))

from core.auth import check_authentication
from config.settings import APP_NAME, APP_VERSION, APP_AUTHOR

# Page configuration
st.set_page_config(
    page_title=f"{APP_NAME} v{APP_VERSION}",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern Professional CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main {
        padding-top: 0rem;
        background: #f8f9fc;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main Header */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at 30% 50%, rgba(255,255,255,0.1) 0%, transparent 60%);
        pointer-events: none;
    }
    
    .main-header h1 {
        font-size: 3rem;
        font-weight: 800;
        margin: 0 0 0.5rem 0;
        letter-spacing: -1px;
        position: relative;
        z-index: 1;
    }
    
    .main-header p {
        font-size: 1.2rem;
        margin: 0.5rem 0;
        opacity: 0.95;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }
    
    .main-header .version {
        font-size: 0.9rem;
        opacity: 0.8;
        margin-top: 1rem;
    }
    
    /* User Info Card */
    .user-info-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #e8ecf4;
    }
    
    .user-info-card h3 {
        color: #1a202c;
        font-size: 1.4rem;
        font-weight: 700;
        margin: 0 0 1rem 0;
    }
    
    .user-info-card p {
        color: #4a5568;
        font-size: 0.95rem;
        margin: 0.5rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .user-info-card .badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }
    
    /* Stats Cards */
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .stats-card {
        background: white;
        border-radius: 16px;
        padding: 2rem 1.5rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #e8ecf4;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .stats-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .stats-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.2);
    }
    
    .stats-card h2 {
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .stats-card p {
        color: #4a5568;
        font-size: 0.95rem;
        margin: 0.5rem 0 0 0;
        font-weight: 500;
    }
    
    /* Feature Cards */
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin: 1rem 0;
        border: 1px solid #e8ecf4;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.15);
        border-color: #667eea;
    }
    
    .feature-card h3 {
        color: #1a202c;
        font-size: 1.4rem;
        font-weight: 700;
        margin: 0 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .feature-card p {
        color: #4a5568;
        font-size: 1rem;
        line-height: 1.6;
        margin: 0 0 1rem 0;
    }
    
    .feature-card ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .feature-card ul li {
        color: #2d3748;
        font-size: 0.95rem;
        padding: 0.5rem 0;
        padding-left: 1.5rem;
        position: relative;
        line-height: 1.5;
    }
    
    .feature-card ul li::before {
        content: '✓';
        position: absolute;
        left: 0;
        color: #667eea;
        font-weight: bold;
        font-size: 1.1rem;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 2rem;
        font-weight: 700;
        color: #1a202c;
        margin: 3rem 0 1.5rem 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .section-header::before {
        content: '';
        width: 4px;
        height: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 2px;
    }
    
    /* Info Boxes */
    .info-box {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #e8ecf4;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .info-box strong {
        color: #667eea;
        font-weight: 600;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 3rem 2rem;
        margin-top: 4rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    
    .footer h4 {
        font-size: 1.5rem;
        margin: 0 0 1rem 0;
        font-weight: 700;
    }
    
    .footer p {
        margin: 0.5rem 0;
        opacity: 0.95;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: white;
        border-radius: 12px;
        border: 1px solid #e8ecf4;
        font-weight: 600;
        color: #1a202c;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: white;
        border-radius: 12px;
        padding: 1rem 2rem;
        border: 1px solid #e8ecf4;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Check authentication
    if not check_authentication():
        return
    
    # Header
    st.markdown(f"""
    <div class="main-header">
        <h1>🤖 {APP_NAME}</h1>
        <p>Professional Data Science Platform with MLOps Practices</p>
        <p class="version">Version {APP_VERSION} | By {APP_AUTHOR}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # User welcome section
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username = st.session_state.get('username', 'User')
        full_name = st.session_state.get('user_full_name', '')
        email = st.session_state.get('user_email', '')
        is_admin = st.session_state.get('is_admin', False)
        
        st.markdown(f"""
        <div class="user-info-card">
            <h3>👋 Welcome back, {full_name if full_name else username}!</h3>
            <p><span style="font-weight: 600;">👤 Username:</span> {username} {'<span class="badge">ADMIN</span>' if is_admin else ''}</p>
            <p><span style="font-weight: 600;">📧 Email:</span> {email}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 Logout", use_container_width=True, type="primary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Platform statistics
    st.markdown('<h2 class="section-header">📊 Platform Capabilities</h2>', unsafe_allow_html=True)
    
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
    
    # Feature showcase
    st.markdown('<h2 class="section-header">🚀 Key Features</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🧹 Advanced Data Cleaning</h3>
            <p>Comprehensive preprocessing with multiple strategies for handling missing data, outliers, duplicates, and more.</p>
            <ul>
                <li>9 missing data handling strategies</li>
                <li>3 outlier detection methods (IQR, Z-score, Isolation Forest)</li>
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
                <li>Correlation analysis (Pearson, Spearman, Kendall)</li>
                <li>Normality testing (Shapiro-Wilk)</li>
                <li>Multicollinearity detection (VIF)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3>📊 Interactive Visualizations</h3>
            <p>Auto-generated charts and custom visualizations powered by Plotly.</p>
            <ul>
                <li>10+ chart types (histogram, scatter, box, heatmap, etc.)</li>
                <li>Interactive plots with zoom and hover</li>
                <li>Correlation heatmaps</li>
                <li>Distribution analysis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>⚙️ Feature Engineering</h3>
            <p>Advanced feature creation and transformation tools for better model performance.</p>
            <ul>
                <li>Polynomial features (degree 2-4)</li>
                <li>Interaction features (multiply, divide, add, subtract)</li>
                <li>Mathematical transformations (log, sqrt, power)</li>
                <li>Date feature extraction (year, month, quarter, weekend)</li>
                <li>Rolling window features</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3>🤖 AI-Powered Insights</h3>
            <p>Natural language queries powered by ultra-fast Grok AI models.</p>
            <ul>
                <li>Convert questions to SQL automatically</li>
                <li>Automated insights generation</li>
                <li>Ultra-fast Grok reasoning engine</li>
                <li>Multiple AI models available (Grok-4, Grok-2)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3>💾 Data Management</h3>
            <p>Supabase integration for persistent storage and collaboration.</p>
            <ul>
                <li>Save and version datasets in cloud</li>
                <li>Track complete analysis history</li>
                <li>Export in 5 formats (CSV, Excel, Parquet, JSON, Feather)</li>
                <li>Comprehensive audit logging</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick start guide
    st.markdown('<h2 class="section-header">🎯 Quick Start Guide</h2>', unsafe_allow_html=True)
    
    with st.expander("📖 How to Get Started", expanded=False):
        st.markdown("""
        ### Step 1: Configure API Key
        - Visit [console.x.ai](https://console.x.ai) to get your xAI API key
        - Enter it in the sidebar on any page
        - Select your preferred AI model
        
        ### Step 2: Upload Your Data
        - Navigate to **📂 Data Upload** page
        - Upload CSV or Excel file (up to 200MB)
        - View data preview and quality metrics
        
        ### Step 3: Clean Your Data
        - Go to **🧹 Data Cleaning** page
        - Apply preprocessing techniques
        - Handle missing values, outliers, and duplicates
        - Engineer new features
        
        ### Step 4: Analyze & Visualize
        - Use **📈 Analysis & Insights** for statistical tests
        - Explore **📊 Visualizations** for interactive charts
        - Check **🎛️ Dashboard** for comprehensive overview
        
        ### Step 5: Query with AI
        - Ask questions in natural language
        - Get instant SQL queries and insights
        - Download results and reports
        """)
    
    # Navigation tips
    st.markdown('<h2 class="section-header">🧭 Quick Navigation</h2>', unsafe_allow_html=True)
    
    nav_cols = st.columns(3)
    
    with nav_cols[0]:
        st.markdown("""
        <div class="info-box">
            <strong>📂 Data Upload</strong><br>
            Upload and explore your datasets with quality metrics
        </div>
        """, unsafe_allow_html=True)
    
    with nav_cols[1]:
        st.markdown("""
        <div class="info-box">
            <strong>🧹 Data Cleaning</strong><br>
            Preprocess and engineer features with 35+ operations
        </div>
        """, unsafe_allow_html=True)
    
    with nav_cols[2]:
        st.markdown("""
        <div class="info-box">
            <strong>📈 Analysis</strong><br>
            Run statistical tests and get AI-powered insights
        </div>
        """, unsafe_allow_html=True)
    
    # Admin panel link
    if is_admin:
        st.markdown("---")
        st.info("🔑 **Admin Access Granted** - You have additional privileges for user management and system administration")
    
    # Footer
    st.markdown(f"""
    <div class="footer">
        <h4>🤖 {APP_NAME}</h4>
        <p>Empowering data-driven decisions with AI and MLOps</p>
        <p><strong>Developed by {APP_AUTHOR}</strong> | VexaAI © 2025</p>
        <p style="font-size: 0.9rem; margin-top: 1rem;">Built with ❤️ using Streamlit, Grok AI, Supabase, and Modern MLOps</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()