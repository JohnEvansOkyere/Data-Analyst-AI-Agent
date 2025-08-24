import json
import tempfile
import csv
import streamlit as st
import pandas as pd
import sqlite3
import io
import requests
import re
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="VexaAI Data Analyst",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styling */
    .main {
        padding-top: 1rem;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 2rem 3rem 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        font-family: 'Inter', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        font-weight: 300;
        margin-bottom: 1rem;
    }
    
    .company-info {
        font-size: 0.9rem;
        opacity: 0.8;
        font-style: italic;
    }
    
    /* Metric cards styling */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 6px 20px rgba(240, 147, 251, 0.3);
    }
    
    .success-box {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(79, 172, 254, 0.3);
    }
    
    .groq-box {
        background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9ff 0%, #e6eaff 100%);
    }
    
    /* Card styling */
    .data-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border: 1px solid #e0e6ff;
    }
    
    /* Progress bar */
    .custom-progress {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        height: 4px;
        border-radius: 2px;
        margin: 1rem 0;
    }
    
    /* Icon styling */
    .icon {
        font-size: 1.5rem;
        margin-right: 0.5rem;
        vertical-align: middle;
    }
    
    /* Upload area styling */
    .uploadedFile {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: linear-gradient(135deg, #f8f9ff 0%, #e6eaff 100%);
    }
    
    /* Results section */
    .results-container {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 6px 25px rgba(0,0,0,0.1);
        margin: 2rem 0;
        border-top: 4px solid #667eea;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        padding: 2rem;
        margin-top: 3rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        font-family: 'Inter', sans-serif;
    }
    
    /* Animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.6s ease-out;
    }
    
    /* Status indicators */
    .status-success {
        color: #10B981;
        font-weight: 600;
    }
    
    .status-warning {
        color: #F59E0B;
        font-weight: 600;
    }
    
    .status-error {
        color: #EF4444;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Groq API client class
class GroqClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.groq.com/openai/v1"
        
    def chat_completion(self, messages, model="llama-3.3-70b-versatile", max_tokens=500, temperature=0.1):
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
            
            # Debug information
            if response.status_code != 200:
                st.error(f"API Response Status: {response.status_code}")
                st.error(f"API Response: {response.text}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Groq API error: {str(e)}")

# Function to preprocess and save the uploaded file
def preprocess_and_save(file):
    try:
        # Read the uploaded file into a DataFrame
        if file.name.endswith('.csv'):
            # Reset file pointer in case it was read earlier
            file.seek(0)
            df = pd.read_csv(file, encoding='utf-8', na_values=['NA', 'N/A', 'missing'])
        elif file.name.endswith('.xlsx'):
            file.seek(0)
            df = pd.read_excel(file, na_values=['NA', 'N/A', 'missing'])
        else:
            st.error("Unsupported file format. Please upload a CSV or Excel file.")
            return None
        
        # Check if DataFrame has columns
        if df.empty or len(df.columns) == 0:
            st.error("Uploaded file has no data or no valid columns. Please check the file.")
            return None

        # Clean column names
        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
            .str.replace(' ', '_')
            .str.replace('[^A-Za-z0-9_]', '', regex=True)
        )
        
        # Parse dates and numeric columns
        for col in df.columns:
            if 'date' in col.lower():
                df[col] = pd.to_datetime(df[col], errors='coerce')
            elif df[col].dtype == 'object':
                try:
                    df[col] = pd.to_numeric(df[col], errors='ignore')
                except Exception:
                    pass
        
        return df

    except Exception as e:
        st.error(f"Error processing file: {e}")
        return None


def generate_sql_query(user_query, columns, table_name="data", client=None):
    """Generate SQL query using Groq"""
    column_info = ", ".join(columns)
    
    prompt = f"""
    You are a SQL expert. Given a user query and table schema, generate a precise SQL query.
    
    Table: {table_name}
    Columns: {column_info}
    
    User Query: {user_query}
    
    Rules:
    1. Return ONLY the SQL query, no explanations
    2. Use standard SQL syntax compatible with SQLite
    3. Use the exact column names provided
    4. If the query seems ambiguous, make reasonable assumptions
    5. For aggregations, use appropriate GROUP BY clauses
    6. Use table name '{table_name}' in your query
    7. Do not include markdown formatting or code blocks
    
    SQL Query:
    """
    
    try:
        messages = [{"role": "user", "content": prompt}]
        response = client.chat_completion(
            messages=messages,
            max_tokens=300,
            temperature=0.1
        )
        
        sql_query = response['choices'][0]['message']['content'].strip()
        
        # Clean the SQL query
        sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
        
        # Extract SQL if it's wrapped in text
        lines = sql_query.split('\n')
        for line in lines:
            line = line.strip()
            if line.upper().startswith('SELECT'):
                return line
        
        if sql_query.startswith('SELECT') or sql_query.startswith('select'):
            return sql_query
        else:
            return sql_query
            
    except Exception as e:
        st.error(f"Error generating SQL query: {e}")
        return None

def execute_query(df, sql_query):
    """Execute SQL query on DataFrame using SQLite"""
    try:
        # Create in-memory SQLite database
        conn = sqlite3.connect(':memory:')
        
        # Load DataFrame into SQLite
        df.to_sql('data', conn, index=False, if_exists='replace')
        
        # Execute query
        result = pd.read_sql_query(sql_query, conn)
        conn.close()
        
        return result
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return None

def interpret_results(query, sql_query, results, client):
    """Generate interpretation of results using Groq"""
    results_preview = results.head(10).to_string() if len(results) > 10 else results.to_string()
    
    prompt = f"""
    Analyze the following query results and provide a clear, concise interpretation:
    
    Original Question: {query}
    SQL Query Used: {sql_query}
    Results ({len(results)} rows):
    {results_preview}
    
    Please provide:
    1. A summary of what the data shows
    2. Key insights or patterns
    3. Answer to the original question
    
    Keep the response clear and business-friendly. Do not use markdown formatting.
    """
    
    try:
        messages = [{"role": "user", "content": prompt}]
        response = client.chat_completion(
            messages=messages,
            max_tokens=400,
            temperature=0.3
        )
        
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Results retrieved successfully, but couldn't generate interpretation: {e}"

# Main header
st.markdown("""
<div class="main-header fade-in">
    <h1>🤖 VexaAI Data Analyst</h1>
    <p>Transform your data into insights with AI-powered natural language queries</p>
    <div class="company-info">Developed by John Evans Okyere | VexaAI | Powered by Groq AI ⚡</div>
</div>
""", unsafe_allow_html=True)

# Sidebar with enhanced styling
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    
    # Groq info box
    st.markdown("""
    <div class="groq-box">
        <h4>⚡ Powered by Groq</h4>
        <p><strong>FREE & FAST AI</strong><br>
        • Lightning-fast inference<br>
        • 14,400 requests/day free<br>
        • No credit card required</p>
    </div>
    """, unsafe_allow_html=True)
    
    # API Key input with enhanced styling
    with st.container():
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.markdown("**🔑 Groq API Key**")
        
        # Instructions for getting Groq API key
        with st.expander("📝 Get Free Groq API Key", expanded=False):
            st.markdown("""
            **How to get your FREE Groq API Key:**
            
            1. Visit [console.groq.com](https://console.groq.com)
            2. Sign up with your email (free!)
            3. Go to API Keys section
            4. Click "Create API Key"
            5. Copy and paste it below
            
            **Free Tier Includes:**
            • 14,400 requests per day
            • Multiple AI models
            • Lightning fast responses
            • No credit card required
            """)
        
        groq_key = st.text_input(
            "Enter your Groq API key",
            type="password", 
            placeholder="gsk_...",
            label_visibility="collapsed",
            help="Get your free API key from console.groq.com"
        )
        
        if groq_key:
            st.session_state.groq_key = groq_key
            st.markdown('<p class="status-success">✅ Groq API key configured!</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-warning">⚠️ Free Groq API key required</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Model selection
    if "groq_key" in st.session_state:
        st.markdown("**🧠 AI Model Selection**")
        model_choice = st.selectbox(
            "Choose AI Model:",
            [
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant", 
                "gemma2-9b-it",
                "deepseek-r1-distill-llama-70b",
                "qwen/qwen3-32b"
            ],
            help="Different models offer various capabilities and speeds"
        )
        st.session_state.selected_model = model_choice
        
        # Model info
        model_info = {
            "llama-3.3-70b-versatile": "🚀 Best overall performance (Meta's latest)",
            "llama-3.1-8b-instant": "⚡ Fastest responses", 
            "gemma2-9b-it": "🎯 Efficient and accurate (Google)",
            "deepseek-r1-distill-llama-70b": "🧠 Advanced reasoning capabilities",
            "qwen/qwen3-32b": "🌐 Multilingual powerhouse"
        }
        
        st.info(model_info.get(model_choice, "Great choice!"))
    
    st.markdown("---")
    
    # How to use section
    with st.expander("📖 How to Use", expanded=True):
        st.markdown("""
        **Step-by-step guide:**
        
        1. 🔑 **Get Free API Key**
           - Visit console.groq.com
           - Sign up (completely free!)
           - Create API key
        
        2. 📂 **Upload Data**
           - Support for CSV & Excel files
           - Auto-detects data types
        
        3. 💬 **Ask Questions**
           - Use natural language
           - Get SQL queries automatically
        
        4. 📊 **Get Insights**
           - View results instantly
           - Download analysis
        """)
    
    # Sample questions
    with st.expander("💡 Example Questions"):
        st.markdown("""
        **Try these sample queries:**
        
        • *"What are the top 10 products by sales?"*
        • *"Show me monthly revenue trends"*
        • *"How many customers by region?"*
        • *"What's the average order value?"*
        • *"Which products have low inventory?"*
        """)
    
    # Status indicator
    st.markdown("---")
    st.markdown("### 🔄 Status")
    if "groq_key" in st.session_state:
        st.success("🟢 Ready to analyze with Groq AI")
    else:
        st.error("🔴 Waiting for free Groq API key")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # File upload with modern styling
    st.markdown("### 📂 Upload Your Data")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["csv", "xlsx"],
        help="Upload CSV or Excel files up to 200MB"
    )
    
    if uploaded_file is not None:
        st.markdown(f"""
        <div class="success-box">
            <strong>📄 {uploaded_file.name}</strong><br>
            <small>{uploaded_file.size / 1024:.1f} KB • {uploaded_file.type}</small>
        </div>
        """, unsafe_allow_html=True)

with col2:
    if uploaded_file is not None and "groq_key" in st.session_state:
        # Quick stats
        st.markdown("### 📈 Quick Stats")
        try:
            if uploaded_file.name.endswith('.csv'):
                temp_df = pd.read_csv(uploaded_file)
            else:
                temp_df = pd.read_excel(uploaded_file)
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Rows", f"{len(temp_df):,}")
                st.metric("Columns", len(temp_df.columns))
            with col_b:
                st.metric("Size", f"{uploaded_file.size / 1024:.1f} KB")
                st.metric("Type", uploaded_file.name.split('.')[-1].upper())
        except:
            pass

# Main processing logic
if uploaded_file is not None and "groq_key" in st.session_state:
    # Initialize Groq client
    try:
        client = GroqClient(st.session_state.groq_key)
    except Exception as e:
        st.error(f"Failed to initialize Groq client: {e}")
        st.stop()
    
    # Process the uploaded file
    with st.spinner('🔄 Processing your data...'):
        df = preprocess_and_save(uploaded_file)
    
    if df is not None:
        # Success message
        st.markdown(f"""
        <div class="success-box fade-in">
            <h4>✅ Data Loaded Successfully!</h4>
            <p>{len(df):,} rows • {len(df.columns)} columns • {df.memory_usage(deep=True).sum() / 1024:.1f} KB</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced metrics display
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3>📊 {}</h3>
                <p>Total Rows</p>
            </div>
            """.format(f"{len(df):,}"), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3>📋 {}</h3>
                <p>Columns</p>
            </div>
            """.format(len(df.columns)), unsafe_allow_html=True)
        
        with col3:
            numeric_cols = len(df.select_dtypes(include=['number']).columns)
            st.markdown("""
            <div class="metric-card">
                <h3>🔢 {}</h3>
                <p>Numeric Fields</p>
            </div>
            """.format(numeric_cols), unsafe_allow_html=True)
        
        with col4:
            text_cols = len(df.select_dtypes(include=['object']).columns)
            st.markdown("""
            <div class="metric-card">
                <h3>📝 {}</h3>
                <p>Text Fields</p>
            </div>
            """.format(text_cols), unsafe_allow_html=True)
        
        # Tabs for data exploration
        tab1, tab2, tab3 = st.tabs(["🔍 Data Preview", "📋 Column Info", "📊 Data Profile"])
        
        with tab1:
            st.markdown("#### First 10 rows of your data")
            st.dataframe(df.head(10), use_container_width=True, height=400)
        
        with tab2:
            col_info = pd.DataFrame({
                'Column': df.columns,
                'Type': df.dtypes.astype(str),
                'Non-Null': df.count(),
                'Null Count': df.isnull().sum(),
                'Null %': (df.isnull().sum() / len(df) * 100).round(1)
            })
            st.dataframe(col_info, use_container_width=True, height=400)
        
        with tab3:
            # Basic data profiling
            st.markdown("#### Data Quality Overview")
            
            # Missing data visualization
            missing_data = df.isnull().sum()
            if missing_data.sum() > 0:
                fig = px.bar(
                    x=missing_data.index,
                    y=missing_data.values,
                    title="Missing Values by Column",
                    labels={'x': 'Columns', 'y': 'Missing Count'}
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.success("🎉 No missing values detected!")
        
        # Query interface
        st.markdown("---")
        st.markdown("## 🤔 Ask Questions About Your Data")
        
        # Enhanced query input
        with st.container():
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            
            # Quick action buttons
            st.markdown("**Quick Actions:**")
            quick_cols = st.columns(4)
            
            with quick_cols[0]:
                if st.button("📊 Show Summary"):
                    st.session_state.quick_query = "Show me a summary of all numeric columns"
            
            with quick_cols[1]:
                if st.button("🏆 Top Records"):
                    st.session_state.quick_query = "Show me the top 10 records"
            
            with quick_cols[2]:
                if st.button("🔍 Data Types"):
                    st.session_state.quick_query = "Show me the data types of all columns"
            
            with quick_cols[3]:
                if st.button("📈 Trends"):
                    st.session_state.quick_query = "Show me any trends in the data"
            
            # Main query input
            user_query = st.text_area(
                "Enter your question:",
                value=st.session_state.get('quick_query', ''),
                placeholder="e.g., What are the top 5 products by sales revenue?",
                height=120,
                help="Ask any question about your data in natural language"
            )
            
            # Clear quick query after use
            if 'quick_query' in st.session_state:
                del st.session_state.quick_query
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Analysis button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            analyze_clicked = st.button(
                "🚀 Analyze Data with Groq AI",
                type="primary",
                use_container_width=True
            )
        
        # Process query
        if analyze_clicked:
            if not user_query.strip():
                st.warning("💭 Please enter a question to analyze your data.")
            else:
                # Create results container
                st.markdown('<div class="results-container fade-in">', unsafe_allow_html=True)
                
                # Step 1: Generate SQL
                with st.spinner('🧠 Generating SQL query with Groq AI...'):
                    selected_model = st.session_state.get('selected_model', 'llama-3.1-70b-versatile')
                    sql_query = generate_sql_query(
                        user_query, 
                        df.columns.tolist(), 
                        "data", 
                        client
                    )
                
                if sql_query:
                    # Display generated SQL
                    st.markdown("### 🔧 Generated SQL Query")
                    st.code(sql_query, language="sql")
                    
                    # Step 2: Execute query
                    with st.spinner('⚡ Executing query...'):
                        results = execute_query(df, sql_query)
                    
                    if results is not None and len(results) > 0:
                        # Display results
                        st.markdown("### 📊 Query Results")
                        
                        # Results metrics
                        result_cols = st.columns(3)
                        with result_cols[0]:
                            st.metric("Rows Returned", len(results))
                        with result_cols[1]:
                            st.metric("Columns", len(results.columns))
                        with result_cols[2]:
                            st.metric("Data Size", f"{results.memory_usage(deep=True).sum() / 1024:.1f} KB")
                        
                        # Show results
                        st.dataframe(results, use_container_width=True, height=400)
                        
                        # Download button
                        csv_buffer = io.StringIO()
                        results.to_csv(csv_buffer, index=False)
                        st.download_button(
                            label="📥 Download Results as CSV",
                            data=csv_buffer.getvalue(),
                            file_name=f"analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                        
                        # Step 3: Generate insights
                        with st.spinner('🎯 Generating insights with Groq AI...'):
                            interpretation = interpret_results(
                                user_query, 
                                sql_query, 
                                results, 
                                client
                            )
                        
                        # Display insights
                        st.markdown("### 💡 AI Analysis & Insights")
                        st.markdown(f"""
                        <div class="info-box">
                            {interpretation}
                        </div>
                        """, unsafe_allow_html=True)
                        
                    elif results is not None and len(results) == 0:
                        st.warning("🔍 Query executed successfully but returned no results. Try adjusting your question.")
                    else:
                        st.error("❌ Failed to execute the query. Please try rephrasing your question.")
                else:
                    st.error("❌ Failed to generate SQL query. Please try rephrasing your question.")
                
                st.markdown('</div>', unsafe_allow_html=True)

elif uploaded_file is not None:
    st.markdown("""
    <div class="info-box">
        <h4>⚠️ Free Groq API Key Required</h4>
        <p>Please enter your free Groq API key in the sidebar to start analyzing your data.</p>
        <p><strong>Get yours free at:</strong> <a href="https://console.groq.com" target="_blank">console.groq.com</a></p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Welcome screen
    st.markdown("""
    <div class="info-box fade-in">
        <h3>🚀 Ready to Get Started?</h3>
        <p>Upload your CSV or Excel file above and start asking questions about your data in natural language!</p>
        <p><strong>Now powered by lightning-fast Groq AI - completely FREE!</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature highlights
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="data-card">
            <h4>⚡ Groq AI-Powered</h4>
            <p>Convert natural language questions into SQL queries using lightning-fast Groq AI - completely FREE!</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="data-card">
            <h4>📊 Smart Analysis</h4>
            <p>Get instant insights and interpretations of your data with contextual explanations</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="data-card">
            <h4>🔒 Secure & Free</h4>
            <p>Your data is processed locally and never stored. Complete privacy with free AI processing</p>
        </div>
        """, unsafe_allow_html=True)

# Enhanced footer
st.markdown("""
<div class="footer">
    <h4>🤖 VexaAI Data Analyst ⚡</h4>
    <p>Empowering data-driven decisions with FREE Groq AI technology</p>
    <p><strong>Developed by John Evans Okyere</strong> | VexaAI © 2025</p>
    <p><small>Built with ❤️ using Streamlit, Groq AI, and Modern Web Technologies</small></p>
    <p><small>🆓 Free forever • ⚡ Lightning fast • 🔒 Privacy first</small></p>
</div>
""", unsafe_allow_html=True)