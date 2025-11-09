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
from utils.ui_components import apply_modern_css, render_page_header, render_section_header

logger = get_logger(__name__)

st.set_page_config(page_title="Data Upload", page_icon="📂", layout="wide")

def main():
    if not check_authentication():
        return
    
    # Apply modern CSS
    apply_modern_css()
    
    # Modern page header
    render_page_header(
        title="Data Upload & Preview",
        subtitle="Upload your CSV or Excel file to get started",
        icon="📂"
    )
    
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
            st.warning("⚠️ API key required for AI features")
        
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
        
        # Supabase status indicator
        st.markdown("---")
        st.markdown("**💾 Database Status**")
        db = get_supabase_manager()
        if db.is_connected():
            st.success("✅ Supabase Connected")
        else:
            st.warning("⚠️ Supabase not configured")
            st.info("Add credentials to .env file")
    
    # Main content
    render_section_header("📤 Upload Your Dataset")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel file",
            type=["csv", "xlsx", "xls"],
            help="Maximum file size: 200MB"
        )
        
        if uploaded_file:
            st.success(f"✅ **{uploaded_file.name}** - {format_file_size(uploaded_file.size)}")
    
    with col2:
        if uploaded_file:
            st.markdown("### 📊 Quick Stats")
            try:
                stats = get_quick_stats(uploaded_file)
                st.metric("Rows", f"{stats['rows']:,}")
                st.metric("Columns", stats['columns'])
                st.metric("File Type", stats['file_type'])
            except Exception as e:
                st.error(f"Error: {e}")
    
    # Process uploaded file
    if uploaded_file:
        with st.spinner('🔄 Processing your data...'):
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
                st.error(f"❌ Error processing file: {e}")
                logger.error(f"File processing error: {e}")
                return
        
        st.success("✅ Data loaded successfully!")
        
        # Metrics row
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
        render_section_header("📊 Data Quality Assessment")
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
        render_section_header("👀 Data Preview")
        
        tab1, tab2, tab3 = st.tabs(["📋 Data Sample", "📊 Column Info", "📈 Statistics"])
        
        with tab1:
            st.dataframe(df.head(20), use_container_width=True, height=400)
            
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
        
        # Save to Supabase - FIXED: Check connection instead of session state
        render_section_header("💾 Save to Database")
        
        db = get_supabase_manager()
        
        if not db.is_connected():
            st.warning("⚠️ Supabase not configured")
            st.info("💡 Add SUPABASE_URL and SUPABASE_ANON_KEY to your .env file to enable cloud storage")
        else:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("""
                Save your dataset to Supabase for:
                - 📊 Version control
                - 📈 Analysis history tracking
                - 👥 Team collaboration
                - 📝 Audit logging
                """)
            
            with col2:
                if st.button("💾 Save to Supabase", use_container_width=True, type="primary"):
                    with st.spinner("Saving to database..."):
                        try:
                            # Prepare column info
                            column_info_dict = df.dtypes.astype(str).to_dict()
                            
                            logger.info(f"Attempting to save dataset: {uploaded_file.name}")
                            
                            # Save dataset
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
                                    "completeness": quality['completeness'],
                                    "uniqueness": quality['uniqueness'],
                                    "upload_date": pd.Timestamp.now().isoformat(),
                                    "file_type": uploaded_file.type
                                }
                            )
                            
                            if dataset_id:
                                st.success("✅ Dataset saved successfully!")
                                st.info(f"📊 Dataset ID: `{dataset_id}`")
                                st.session_state.current_dataset_id = dataset_id
                                
                                # Log the activity
                                db.log_user_activity(
                                    user_id=st.session_state.username,
                                    activity_type="dataset_upload",
                                    description=f"Uploaded dataset: {uploaded_file.name}",
                                    metadata={
                                        "dataset_id": dataset_id,
                                        "rows": len(df),
                                        "columns": len(df.columns),
                                        "file_size": uploaded_file.size,
                                        "quality_score": quality['quality_score']
                                    }
                                )
                                
                                logger.info(f"✅ Dataset saved: {dataset_id} by {st.session_state.username}")
                            else:
                                st.error("❌ Failed to save dataset to Supabase")
                                logger.error("Dataset save returned None")
                                
                        except Exception as e:
                            st.error(f"❌ Error saving to Supabase: {str(e)}")
                            logger.error(f"Supabase save error: {e}", exc_info=True)

            

if __name__ == "__main__":
    main()