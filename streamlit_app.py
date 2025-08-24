import streamlit as st
import pandas as pd
import io
import plotly.express as px
from datetime import datetime

# Import our modules
from ml_engine import (
    GroqClient, 
    preprocess_and_save, 
    generate_sql_query, 
    execute_query, 
    interpret_results,
    get_data_profile,
    get_quick_stats
)
from auth import check_authentication, show_admin_panel

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

def main():
    # Check authentication first
    if not check_authentication():
        return
    
    # Main header
    st.markdown("""
    <div class="main-header fade-in">
        <h1>🤖 VexaAI Data Analyst</h1>
        <p>Transform your data into insights with AI-powered natural language queries</p>
        <div class="company-info">Developed by John Evans Okyere | VexaAI | Powered by Groq AI ⚡</div>
    </div>
    """, unsafe_allow_html=True)
    
    # User info in header
    col1, col2, col3 = st.columns([2, 1, 1])
    with col2:
        st.markdown(f"**👤 Welcome, {st.session_state.username}**")
    with col3:
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.clear()
            st.rerun()
    
    # Sidebar with enhanced styling
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        # Admin panel access
        if st.session_state.get('is_admin', False):
            if st.button("👨‍💼 Admin Panel"):
                st.session_state.show_admin = True
                st.rerun()
        
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
    
    # Show admin panel if requested
    if st.session_state.get('show_admin', False):
        show_admin_panel()
        if st.button("← Back to Main App"):
            st.session_state.show_admin = False
            st.rerun()
        return
    
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
                stats = get_quick_stats(uploaded_file)
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Rows", f"{stats['rows']:,}")
                    st.metric("Columns", stats['columns'])
                with col_b:
                    st.metric("Size", f"{stats['size_kb']:.1f} KB")
                    st.metric("Type", stats['file_type'])
            except Exception as e:
                st.error(f"Error getting stats: {e}")
    
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
            try:
                df = preprocess_and_save(uploaded_file)
            except Exception as e:
                st.error(f"Error processing file: {e}")
                st.stop()
        
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
                        try:
                            sql_query = generate_sql_query(
                                user_query, 
                                df.columns.tolist(), 
                                "data", 
                                client
                            )
                        except Exception as e:
                            st.error(f"Error generating SQL: {e}")
                            st.stop()
                    
                    if sql_query:
                        # Display generated SQL
                        st.markdown("### 🔧 Generated SQL Query")
                        st.code(sql_query, language="sql")
                        
                        # Step 2: Execute query
                        with st.spinner('⚡ Executing query...'):
                            try:
                                results = execute_query(df, sql_query)
                            except Exception as e:
                                st.error(f"Error executing query: {e}")
                                st.stop()
                        
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
                                try:
                                    interpretation = interpret_results(
                                        user_query, 
                                        sql_query, 
                                        results, 
                                        client
                                    )
                                except Exception as e:
                                    interpretation = f"Results retrieved successfully, but couldn't generate interpretation: {e}"
                            
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

if __name__ == "__main__":
    main()
