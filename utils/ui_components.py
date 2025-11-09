"""
VexaAI Data Analyst Pro - Shared UI Components
Reusable UI elements and styling for consistent design across all pages
"""

import streamlit as st


def apply_modern_css():
    """Apply modern professional CSS to any page"""
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
        
        /* Page Header */
        .page-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            color: white;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }
        
        .page-header h1 {
            font-size: 2.5rem;
            font-weight: 800;
            margin: 0;
            letter-spacing: -0.5px;
        }
        
        .page-header p {
            font-size: 1.1rem;
            margin: 0.5rem 0 0 0;
            opacity: 0.95;
        }
        
        /* Section Headers */
        .section-header {
            font-size: 1.8rem;
            font-weight: 700;
            color: #1a202c;
            margin: 2rem 0 1rem 0;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        
        .section-header::before {
            content: '';
            width: 4px;
            height: 1.8rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 2px;
        }
        
        /* Cards */
        .custom-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            border: 1px solid #e8ecf4;
            margin: 1rem 0;
        }
        
        /* Stats Cards */
        .stats-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            border: 1px solid #e8ecf4;
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
        
        .stats-card h2 {
            font-size: 2.5rem;
            font-weight: 800;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .stats-card p {
            color: #4a5568;
            font-size: 0.9rem;
            margin: 0.5rem 0 0 0;
            font-weight: 500;
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 25px rgba(102, 126, 234, 0.4);
        }
        
        # /* Sidebar */
        # [data-testid="stSidebar"] {
        #     background: white;
        #     border-right: 1px solid #e8ecf4;
        # }
        
        # [data-testid="stSidebar"] h1, 
        # [data-testid="stSidebar"] h2, 
        # [data-testid="stSidebar"] h3 {
        #     color: #1a202c;
        # }
        
        /* Metric containers */
        [data-testid="stMetricValue"] {
            font-size: 2rem;
            font-weight: 700;
            color: #667eea;
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
            gap: 0.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: white;
            border-radius: 12px;
            padding: 0.75rem 1.5rem;
            border: 1px solid #e8ecf4;
            font-weight: 600;
            color: #4a5568;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-color: transparent;
        }
        
        /* Success/Error/Warning boxes */
        .stAlert {
            border-radius: 12px;
            border: 1px solid #e8ecf4;
        }
        
        /* Dataframe */
        .dataframe {
            border-radius: 12px;
            overflow: hidden;
        }
        
        /* File uploader */
        [data-testid="stFileUploader"] {
            border-radius: 12px;
            border: 2px dashed #667eea;
            padding: 2rem;
            background: white;
        }
        
        /* Select boxes */
        .stSelectbox > div > div {
            border-radius: 8px;
        }
        
        /* Text inputs */
        .stTextInput > div > div > input {
            border-radius: 8px;
        }
    </style>
    """, unsafe_allow_html=True)


def render_page_header(title: str, subtitle: str = "", icon: str = ""):
    """Render a consistent page header"""
    full_title = f"{icon} {title}" if icon else title
    subtitle_html = f"<p>{subtitle}</p>" if subtitle else ""
    
    st.markdown(f"""
    <div class="page-header">
        <h1>{full_title}</h1>
        {subtitle_html}
    </div>
    """, unsafe_allow_html=True)


def render_metric_card(value: str, label: str):
    """Render a metric card"""
    st.markdown(f"""
    <div class="stats-card">
        <h2>{value}</h2>
        <p>{label}</p>
    </div>
    """, unsafe_allow_html=True)


def render_section_header(title: str):
    """Render a section header with accent bar"""
    st.markdown(f'<h2 class="section-header">{title}</h2>', unsafe_allow_html=True)