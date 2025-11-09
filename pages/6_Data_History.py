"""
Data History Page - Track uploaded datasets
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.auth import check_authentication
from utils.logger import get_logger

logger = get_logger(__name__)

st.set_page_config(page_title="Data History", page_icon="📁", layout="wide")

def main():
    if not check_authentication():
        return
    
    st.title("📁 Data History")
    st.markdown("View your uploaded datasets and analysis history")
    
    # Initialize history in session state if not exists
    if 'data_history' not in st.session_state:
        st.session_state.data_history = []
    
    # ==================== CURRENT DATASET ====================
    if 'df' in st.session_state:
        st.markdown("### 📊 Current Dataset")
        
        current_dataset = {
            'name': st.session_state.get('dataset_name', 'Current Dataset'),
            'rows': len(st.session_state.df),
            'columns': len(st.session_state.df.columns),
            'size_mb': st.session_state.df.memory_usage(deep=True).sum() / 1024 / 1024,
            'loaded_at': datetime.now()
        }
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📋 Rows", f"{current_dataset['rows']:,}")
        with col2:
            st.metric("📊 Columns", current_dataset['columns'])
        with col3:
            st.metric("💾 Size", f"{current_dataset['size_mb']:.2f} MB")
        with col4:
            st.metric("📅 Loaded", "Just now")
        
        # Dataset preview
        with st.expander("👀 Preview Current Dataset"):
            st.dataframe(st.session_state.df.head(20), use_container_width=True)
        
        # Save to history button
        if st.button("💾 Save to History"):
            # Check if already in history
            if not any(d['name'] == current_dataset['name'] for d in st.session_state.data_history):
                st.session_state.data_history.append(current_dataset)
                st.success(f"✅ Saved '{current_dataset['name']}' to history!")
                st.rerun()
            else:
                st.info("ℹ️ This dataset is already in history")
    
    else:
        st.info("ℹ️ No dataset currently loaded. Upload data to get started!")
    
    # ==================== HISTORY ====================
    st.markdown("---")
    st.markdown("### 📚 Dataset History")
    
    if len(st.session_state.data_history) > 0:
        st.markdown(f"**Total datasets tracked: {len(st.session_state.data_history)}**")
        
        # Display history
        for idx, dataset in enumerate(reversed(st.session_state.data_history)):
            with st.expander(f"📊 {dataset['name']} - {dataset['loaded_at'].strftime('%Y-%m-%d %H:%M')}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write("**Dimensions:**")
                    st.write(f"Rows: {dataset['rows']:,}")
                    st.write(f"Columns: {dataset['columns']}")
                
                with col2:
                    st.write("**Size:**")
                    st.write(f"{dataset['size_mb']:.2f} MB")
                
                with col3:
                    st.write("**Loaded:**")
                    st.write(dataset['loaded_at'].strftime('%Y-%m-%d %H:%M:%S'))
                
                # Delete button
                if st.button(f"🗑️ Remove from History", key=f"del_{idx}"):
                    st.session_state.data_history.remove(dataset)
                    st.success("Removed from history!")
                    st.rerun()
        
        # Clear all history
        st.markdown("---")
        if st.button("🗑️ Clear All History", type="secondary"):
            st.session_state.data_history = []
            st.success("History cleared!")
            st.rerun()
    
    else:
        st.info("📭 No datasets in history yet. Upload and save datasets to track them here!")
    
    # ==================== STATISTICS ====================
    if len(st.session_state.data_history) > 0:
        st.markdown("---")
        st.markdown("### 📊 History Statistics")
        
        total_rows = sum(d['rows'] for d in st.session_state.data_history)
        total_size = sum(d['size_mb'] for d in st.session_state.data_history)
        avg_columns = sum(d['columns'] for d in st.session_state.data_history) / len(st.session_state.data_history)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Rows Processed", f"{total_rows:,}")
        with col2:
            st.metric("Total Data Size", f"{total_size:.2f} MB")
        with col3:
            st.metric("Avg Columns", f"{avg_columns:.0f}")

if __name__ == "__main__":
    main()