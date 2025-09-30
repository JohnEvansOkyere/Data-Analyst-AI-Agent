import streamlit as st
import pandas as pd
import io
import plotly.express as px
import plotly.graph_objects as go
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
    page_title="VexaAI Data Analyst - Powered by Grok",
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
            
    /* Metric cards styling */
.metric-card {
    background: white;
    padding: 1.5rem;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    border-left: 4px solid #667eea;
    margin: 0.5rem 0;
}

.metric-card h3 {
    color: #667eea;
    font-size: 2rem;
    margin: 0;
    font-weight: 700;
}

.metric-card p {
    color: #4a5568;
    font-size: 0.9rem;
    margin: 0.5rem 0 0 0;
    font-weight: 500;
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
    
    .grok-box {
        background: linear-gradient(135deg, #1DA1F2 0%, #14171A 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(29, 161, 242, 0.3);
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

def create_visualizations(df):
    """Create automatic visualizations based on data types"""
    visualizations = []
    
    # Get numeric and categorical columns
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    # 1. Distribution of numeric columns (first 3)
    for col in numeric_cols[:3]:
        fig = px.histogram(
            df, 
            x=col, 
            title=f'Distribution of {col}',
            color_discrete_sequence=['#667eea']
        )
        fig.update_layout(
            template='plotly_white',
            height=400
        )
        visualizations.append(('histogram', col, fig))
    
    # 2. Count plots for categorical columns (first 3)
    for col in categorical_cols[:3]:
        value_counts = df[col].value_counts().head(10)
        fig = px.bar(
            x=value_counts.index,
            y=value_counts.values,
            title=f'Top 10 {col}',
            labels={'x': col, 'y': 'Count'},
            color_discrete_sequence=['#764ba2']
        )
        fig.update_layout(
            template='plotly_white',
            height=400
        )
        visualizations.append(('bar', col, fig))
    
    # 3. Correlation heatmap if multiple numeric columns
    if len(numeric_cols) > 1:
        corr_matrix = df[numeric_cols].corr()
        fig = px.imshow(
            corr_matrix,
            title='Correlation Heatmap',
            color_continuous_scale='RdBu_r',
            aspect='auto'
        )
        fig.update_layout(
            template='plotly_white',
            height=500
        )
        visualizations.append(('heatmap', 'correlation', fig))
    
    # 4. Scatter plot for first two numeric columns
    if len(numeric_cols) >= 2:
        fig = px.scatter(
            df,
            x=numeric_cols[0],
            y=numeric_cols[1],
            title=f'{numeric_cols[0]} vs {numeric_cols[1]}',
            color_discrete_sequence=['#f093fb'],
            opacity=0.6
        )
        fig.update_layout(
            template='plotly_white',
            height=400
        )
        visualizations.append(('scatter', f'{numeric_cols[0]}_vs_{numeric_cols[1]}', fig))
    
    # 5. Box plot for numeric columns
    if len(numeric_cols) > 0:
        fig = go.Figure()
        for col in numeric_cols[:5]:
            fig.add_trace(go.Box(y=df[col], name=col))
        fig.update_layout(
            title='Box Plot - Numeric Columns',
            template='plotly_white',
            height=400
        )
        visualizations.append(('box', 'numeric_distributions', fig))
    
    return visualizations

def show_query_insights_page(df, client):
    """Page for natural language queries and insights"""
    st.markdown("## 🤔 Ask Questions About Your Data")
    
    # Enhanced query input
    with st.container():
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        
        # Quick action buttons
        st.markdown("**Quick Actions:**")
        quick_cols = st.columns(4)
        
        with quick_cols[0]:
            if st.button("📊 Show Summary", key="summary_btn"):
                st.session_state.quick_query = "Show me a summary of all numeric columns"
        
        with quick_cols[1]:
            if st.button("🏆 Top Records", key="top_btn"):
                st.session_state.quick_query = "Show me the top 10 records"
        
        with quick_cols[2]:
            if st.button("🔍 Data Types", key="types_btn"):
                st.session_state.quick_query = "Show me the data types of all columns"
        
        with quick_cols[3]:
            if st.button("📈 Trends", key="trends_btn"):
                st.session_state.quick_query = "Show me any trends in the data"
        
        # Main query input
        user_query = st.text_area(
            "Enter your question:",
            value=st.session_state.get('quick_query', ''),
            placeholder="e.g., What are the top 5 products by sales revenue?",
            height=120,
            help="Ask any question about your data in natural language",
            key="user_query_input"
        )
        
        # Clear quick query after use
        if 'quick_query' in st.session_state:
            del st.session_state.quick_query
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Analysis button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_clicked = st.button(
            "🚀 Analyze Data with Grok AI",
            type="primary",
            use_container_width=True,
            key="analyze_btn"
        )
    
    # Process query
    if analyze_clicked:
        if not user_query.strip():
            st.warning("💭 Please enter a question to analyze your data.")
        else:
            # Create results container
            st.markdown('<div class="results-container fade-in">', unsafe_allow_html=True)
            
            # Step 1: Generate SQL
            with st.spinner('🧠 Generating SQL query with Grok AI...'):
                selected_model = st.session_state.get('selected_model', 'grok-4-fast-reasoning')
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
                        use_container_width=True,
                        key="download_results_btn"
                    )
                    
                    # Step 3: Generate insights
                    with st.spinner('🎯 Generating insights with Grok AI...'):
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

def show_dashboard_page(df):
    """Page for data visualizations dashboard"""
    st.markdown("## 📊 Interactive Data Dashboard")
    
    st.info("🎨 Auto-generated visualizations based on your data structure")
    
    # Create visualizations
    with st.spinner('🎨 Creating visualizations...'):
        visualizations = create_visualizations(df)
    
    if not visualizations:
        st.warning("No suitable columns found for visualization. Please upload data with numeric or categorical columns.")
        return
    
    # Display visualizations in a grid
    st.markdown("### 📈 Data Visualizations")
    
    for i in range(0, len(visualizations), 2):
        col1, col2 = st.columns(2)
        
        with col1:
            if i < len(visualizations):
                viz_type, viz_name, fig = visualizations[i]
                st.plotly_chart(fig, use_container_width=True, key=f"viz_{i}")
        
        with col2:
            if i + 1 < len(visualizations):
                viz_type, viz_name, fig = visualizations[i + 1]
                st.plotly_chart(fig, use_container_width=True, key=f"viz_{i+1}")
    
    # Summary statistics
    st.markdown("---")
    st.markdown("### 📋 Summary Statistics")
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    if numeric_cols:
        st.dataframe(df[numeric_cols].describe(), use_container_width=True)
    else:
        st.info("No numeric columns available for summary statistics.")

def main():
    # Check authentication first
    if not check_authentication():
        return
    
    # Main header
    st.markdown("""
    <div class="main-header fade-in">
        <h1>🤖 VexaAI Data Analyst</h1>
        <p>Transform your data into insights with AI-powered natural language queries</p>
        <div class="company-info">Developed by John Evans Okyere | VexaAI | Powered by Grok AI ⚡</div>
    </div>
    """, unsafe_allow_html=True)
    
    # User info in header
    col1, col2, col3 = st.columns([2, 1, 1])
    with col2:
        st.markdown(f"**👤 Welcome, {st.session_state.username}**")
    with col3:
        if st.button("🚪 Logout", key="logout_btn"):
            st.session_state.authenticated = False
            st.session_state.clear()
            st.rerun()
    
    # Sidebar with enhanced styling
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        # Admin panel access
        if st.session_state.get('is_admin', False):
            if st.button("👨‍💼 Admin Panel", key="admin_btn"):
                st.session_state.show_admin = True
                st.rerun()
        
        # Grok info box
        st.markdown("""
        <div class="grok-box">
            <h4>⚡ Powered by Grok AI</h4>
            <p><strong>ULTRA-FAST REASONING</strong><br>
            • Lightning-fast inference<br>
            • Advanced reasoning capabilities<br>
            • From xAI</p>
        </div>
        """, unsafe_allow_html=True)
        
        # API Key input with enhanced styling
        with st.container():
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            st.markdown("**🔑 xAI API Key**")
            
            # Instructions for getting xAI API key
            with st.expander("📝 Get xAI API Key", expanded=False):
                st.markdown("""
                **How to get your xAI API Key:**
                
                1. Visit [x.ai](https://x.ai) or [console.x.ai](https://console.x.ai)
                2. Sign up for an account
                3. Navigate to API Keys section
                4. Click "Create API Key"
                5. Copy and paste it below
                
                **Grok Models Available:**
                • grok-4-fast-reasoning (Ultra-fast)
                • grok-2-1212 (Latest stable)
                • grok-beta (Newest features)
                • grok-vision-beta (With vision)
                """)
            
            xai_key = st.text_input(
                "Enter your xAI API key",
                type="password", 
                placeholder="xai-...",
                label_visibility="collapsed",
                help="Get your API key from x.ai",
                key="xai_key_input"
            )
            
            if xai_key:
                st.session_state.groq_key = xai_key
                st.markdown('<p class="status-success">✅ xAI API key configured!</p>', unsafe_allow_html=True)
            else:
                st.markdown('<p class="status-warning">⚠️ xAI API key required</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Model selection
        if "groq_key" in st.session_state:
            st.markdown("**🧠 AI Model Selection**")
            model_choice = st.selectbox(
                "Choose AI Model:",
                [
                    "grok-4-fast-reasoning",
                    "grok-2-1212",
                    "grok-beta",
                    "grok-vision-beta"
                ],
                help="Different models offer various capabilities and speeds",
                key="model_select"
            )
            st.session_state.selected_model = model_choice
            
            # Model info
            model_info = {
                "grok-4-fast-reasoning": "⚡ Ultra-fast reasoning (Recommended)",
                "grok-2-1212": "🚀 Latest Grok 2 - Most stable",
                "grok-beta": "🧪 Beta with newest features",
                "grok-vision-beta": "👁️ Vision-enabled model"
            }
            
            st.info(model_info.get(model_choice, "Great choice!"))
        
        st.markdown("---")
        
        # How to use section
        with st.expander("📖 How to Use", expanded=True):
            st.markdown("""
            **Step-by-step guide:**
            
            1. 🔑 **Get API Key**
               - Visit x.ai or console.x.ai
               - Sign up for an account
               - Create API key
            
            2. 📂 **Upload Data**
               - Support for CSV & Excel files
               - Auto-detects data types
            
            3. 💬 **Query Insights Tab**
               - Use natural language
               - Get SQL queries automatically
               - View AI-generated insights
            
            4. 📊 **Dashboard Tab**
               - Auto-generated visualizations
               - Interactive charts
               - Summary statistics
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
            st.success("🟢 Ready to analyze with Grok AI")
        else:
            st.error("🔴 Waiting for xAI API key")
    
    # Show admin panel if requested
    if st.session_state.get('show_admin', False):
        show_admin_panel()
        if st.button("← Back to Main App", key="back_to_main"):
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
            help="Upload CSV or Excel files up to 200MB",
            key="file_uploader"
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
        # Initialize xAI client
        try:
            client = GroqClient(st.session_state.groq_key)
        except Exception as e:
            st.error(f"Failed to initialize xAI client: {e}")
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
            
            # Main Navigation Tabs
            st.markdown("---")
            tab1, tab2, tab3 = st.tabs(["🔍 Data Preview", "💬 Query Insights", "📊 Dashboard"])
            
            with tab1:
                st.markdown("### First 10 rows of your data")
                st.dataframe(df.head(10), use_container_width=True, height=400)
                
                st.markdown("### Column Information")
                col_info = pd.DataFrame({
                    'Column': df.columns,
                    'Type': df.dtypes.astype(str),
                    'Non-Null': df.count(),
                    'Null Count': df.isnull().sum(),
                    'Null %': (df.isnull().sum() / len(df) * 100).round(1)
                })
                st.dataframe(col_info, use_container_width=True, height=300)
            
            with tab2:
                show_query_insights_page(df, client)
            
            with tab3:
                show_dashboard_page(df)
    
    elif uploaded_file is not None:
        st.markdown("""
        <div class="info-box">
            <h4>⚠️ xAI API Key Required</h4>
            <p>Please enter your xAI API key in the sidebar to start analyzing your data.</p>
            <p><strong>Get yours at:</strong> <a href="https://x.ai" target="_blank" style="color: white; text-decoration: underline;">x.ai</a></p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Welcome screen
        st.markdown("""
        <div class="info-box fade-in">
            <h3>🚀 Ready to Get Started?</h3>
            <p>Upload your CSV or Excel file above and start analyzing your data!</p>
            <p><strong>Now powered by lightning-fast Grok AI!</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature highlights
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="data-card">
                <h4>⚡ Grok AI-Powered</h4>
                <p>Convert natural language questions into SQL queries using ultra-fast Grok reasoning models from xAI</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="data-card">
                <h4>📊 Interactive Dashboard</h4>
                <p>Auto-generated visualizations and charts to understand your data at a glance</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="data-card">
                <h4>🔒 Secure</h4>
                <p>Your data is processed locally and never stored. Complete privacy guaranteed</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Enhanced footer
    st.markdown("""
    <div class="footer">
        <h4>🤖 VexaAI Data Analyst ⚡</h4>
        <p>Empowering data-driven decisions with Grok AI technology</p>
        <p><strong>Developed by John Evans Okyere</strong> | VexaAI © 2025</p>
        <p><small>Built with ❤️ using Streamlit, Grok AI (xAI), and Modern Web Technologies</small></p>
        <p><small>⚡ Lightning fast • 🔒 Privacy first • 🧠 Advanced reasoning</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()