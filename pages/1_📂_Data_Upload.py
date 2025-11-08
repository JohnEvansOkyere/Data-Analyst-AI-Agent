"""
Data Upload and Preview Page
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.auth import check_authentication
from core.ml_engine import preprocess_and_save, get_quick_stats
from database.supabase_manager import get_supabase_manager
from utils.helpers import get_column_info, calculate_data_quality_score, format_file_size
from utils.logger import get_logger, audit_logger

logger = get_logger(__name__)

st.set_page_config(page_title="Data Upload", page_icon="📂", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .upload-box {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: #f8f9ff;
    }
    .success-box {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    if not check_authentication():
        return
    
    st.title("📂 Data Upload & Preview")
    st.markdown("Upload your CSV or Excel file to get started")
    
    # Sidebar - API Configuration
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        st.markdown("**🔑 xAI API Key**")
        with st.expander("📝 Get xAI API Key"):
            st.markdown("""
            1. Visit [console.x.ai](https://console.x.ai)
            2. Sign up/Login
            3. Create API Key
            4. Copy and paste below
            """)
        
        xai_key = st.text_input(
            "Enter your xAI API key",
            type="password",
            placeholder="xai-...",
            key="xai_key_input"
        )
        
        if xai_key:
            st.session_state.groq_key = xai_key
            st.success("✅ API key configured!")
        else:
            st.warning("⚠️ API key required")
        
        if "groq_key" in st.session_state:
            st.markdown("**🧠 AI Model**")
            model_choice = st.selectbox(
                "Choose Model:",
                [
                    "grok-4-fast-reasoning",
                    "grok-2-1212",
                    "grok-beta",
                    "grok-vision-beta"
                ]
            )
            st.session_state.selected_model = model_choice
        
        # Supabase configuration
        st.markdown("---")
        st.markdown("**💾 Supabase Configuration**")
        with st.expander("🔧 Configure Supabase"):
            supabase_url = st.text_input("Supabase URL", type="password")
            supabase_key = st.text_input("Supabase Key", type="password")
            if supabase_url and supabase_key:
                st.session_state.supabase_url = supabase_url
                st.session_state.supabase_key = supabase_key
                st.success("Supabase configured!")
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Upload Your Data")
        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel file",
            type=["csv", "xlsx", "xls"],
            help="Maximum file size: 200MB"
        )
        
        if uploaded_file:
            st.markdown(f"""
            <div class="success-box">
                <strong>📄 {uploaded_file.name}</strong><br>
                <small>{format_file_size(uploaded_file.size)} • {uploaded_file.type}</small>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        if uploaded_file:
            st.markdown("### Quick Stats")
            try:
                stats = get_quick_stats(uploaded_file)
                st.metric("Rows", f"{stats['rows']:,}")
                st.metric("Columns", stats['columns'])
                st.metric("File Type", stats['file_type'])
            except Exception as e:
                st.error(f"Error: {e}")
    
    # Process uploaded file
    if uploaded_file:
        with st.spinner('Processing your data...'):
            try:
                df = preprocess_and_save(uploaded_file)
                st.session_state.df = df
                st.session_state.original_df = df.copy()
                st.session_state.dataset_name = uploaded_file.name
                
                audit_logger.log_data_access(
                    st.session_state.username,
                    uploaded_file.name,
                    "upload"
                )
                
            except Exception as e:
                st.error(f"Error processing file: {e}")
                logger.error(f"File processing error: {e}")
                return
        
        # Display success
        st.success("✅ Data loaded successfully!")
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total Rows", f"{len(df):,}")
        with col2:
            st.metric("📋 Columns", len(df.columns))
        with col3:
            numeric_cols = len(df.select_dtypes(include=['number']).columns)
            st.metric("🔢 Numeric", numeric_cols)
        with col4:
            text_cols = len(df.select_dtypes(include=['object']).columns)
            st.metric("📝 Text", text_cols)
        
        # Data Quality Score
        st.markdown("---")
        st.markdown("### 📊 Data Quality Assessment")
        quality = calculate_data_quality_score(df)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Quality Score",
                f"{quality['quality_score']}%",
                delta="Good" if quality['quality_score'] > 80 else "Needs Improvement"
            )
        with col2:
            st.metric("Completeness", f"{quality['completeness']}%")
        with col3:
            st.metric("Uniqueness", f"{quality['uniqueness']}%")
        
        # Data Preview
        st.markdown("---")
        st.markdown("### 👀 Data Preview")
        
        tab1, tab2, tab3 = st.tabs(["📋 Data Sample", "📊 Column Info", "📈 Statistics"])
        
        with tab1:
            st.dataframe(df.head(20), use_container_width=True, height=400)
            
            # Download button
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Preview CSV",
                data=csv,
                file_name="data_preview.csv",
                mime="text/csv"
            )
        
        with tab2:
            column_info = get_column_info(df)
            st.dataframe(column_info, use_container_width=True, height=400)
        
        with tab3:
            numeric_df = df.select_dtypes(include=['number'])
            if not numeric_df.empty:
                st.dataframe(numeric_df.describe(), use_container_width=True)
            else:
                st.info("No numeric columns to display statistics")
        
        # Save to Supabase option
        if 'supabase_url' in st.session_state and 'supabase_key' in st.session_state:
            st.markdown("---")
            if st.button("💾 Save Dataset to Supabase"):
                try:
                    db = get_supabase_manager()
                    column_info_dict = df.dtypes.astype(str).to_dict()
                    
                    dataset_id = db.save_dataset(
                        user_id=st.session_state.username,
                        dataset_name=uploaded_file.name,
                        file_name=uploaded_file.name,
                        file_size=uploaded_file.size,
                        rows=len(df),
                        columns=len(df.columns),
                        column_info=column_info_dict,
                        metadata={
                            "quality_score": quality['quality_score'],
                            "upload_date": pd.Timestamp.now().isoformat()
                        }
                    )
                    
                    if dataset_id:
                        st.success(f"✅ Dataset saved! ID: {dataset_id}")
                        st.session_state.current_dataset_id = dataset_id
                    else:
                        st.warning("Could not save to Supabase")
                        
                except Exception as e:
                    st.error(f"Error saving to Supabase: {e}")
                    logger.error(f"Supabase save error: {e}")

if __name__ == "__main__":
    main()
