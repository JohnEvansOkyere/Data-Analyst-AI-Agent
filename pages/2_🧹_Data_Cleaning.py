"""
Data Cleaning and Preprocessing Page
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.auth import check_authentication
from core.data_cleaning import DataCleaner, DataScaler, DataEncoder
from core.feature_engineering import FeatureEngineer
from utils.helpers import export_dataframe
from utils.logger import get_logger
from utils.ui_components import apply_modern_css, render_page_header, render_section_header  # NEW!

logger = get_logger(__name__)

st.set_page_config(page_title="Data Cleaning", page_icon="🧹", layout="wide")

def main():
    if not check_authentication():
        return
    
       # Apply modern CSS
    apply_modern_css()
    
    # Modern page header
    render_page_header(
        title="Data Cleaning & Preprocessing",
        subtitle="Transform your data with advanced preprocessing techniques",
        icon="🧹"
    )
    

    st.title("🧹 Data Cleaning & Preprocessing")
    
    if 'df' not in st.session_state:
        st.warning("⚠️ Please upload data first!")
        st.info("Go to '📂 Data Upload' page to upload your dataset")
        return
    
    df = st.session_state.df.copy()
    
    # Sidebar - Operations
    with st.sidebar:
        st.markdown("### 🛠️ Cleaning Operations")
        operation = st.selectbox(
            "Choose Operation",
            [
                "Handle Missing Data",
                "Remove Duplicates",
                "Remove Outliers",
                "Scale Features",
                "Encode Categories",
                "Engineer Features",
                "Clean Text",
                "Convert Data Types"
            ]
        )
    
    # Main content tabs
    tab1, tab2 = st.tabs(["⚙️ Operations", "📊 Preview"])
    
    with tab1:
        if operation == "Handle Missing Data":
            st.markdown("### 📉 Handle Missing Data")
            
            missing_info = df.isnull().sum()
            missing_cols = missing_info[missing_info > 0]
            
            if len(missing_cols) == 0:
                st.success("✅ No missing data found!")
            else:
                st.warning(f"Found missing data in {len(missing_cols)} columns")
                st.dataframe(missing_cols, use_container_width=True)
                
                strategy = st.selectbox(
                    "Strategy",
                    [
                        "drop_rows",
                        "drop_columns",
                        "fill_mean",
                        "fill_median",
                        "fill_mode",
                        "fill_constant",
                        "forward_fill",
                        "backward_fill",
                        "interpolate"
                    ]
                )
                
                columns = st.multiselect(
                    "Select columns",
                    missing_cols.index.tolist(),
                    default=missing_cols.index.tolist()
                )
                
                fill_value = None
                if strategy == "fill_constant":
                    fill_value = st.text_input("Fill value", "0")
                
                if st.button("Apply"):
                    cleaner = DataCleaner(df)
                    df = cleaner.handle_missing_data(
                        strategy=strategy,
                        columns=columns,
                        fill_value=fill_value
                    )
                    st.session_state.df = df
                    st.success("✅ Missing data handled!")
                    st.rerun()
        
        elif operation == "Remove Duplicates":
            st.markdown("### 🔄 Remove Duplicates")
            
            duplicates = df.duplicated().sum()
            st.metric("Duplicate Rows", duplicates)
            
            if duplicates > 0:
                subset = st.multiselect(
                    "Consider these columns",
                    df.columns.tolist(),
                    default=[]
                )
                
                keep = st.selectbox("Keep", ["first", "last", False])
                
                if st.button("Remove Duplicates"):
                    cleaner = DataCleaner(df)
                    df = cleaner.remove_duplicates(
                        subset=subset if subset else None,
                        keep=keep
                    )
                    st.session_state.df = df
                    st.success("✅ Duplicates removed!")
                    st.rerun()
            else:
                st.success("✅ No duplicates found!")
        
        elif operation == "Remove Outliers":
            st.markdown("### 📊 Remove Outliers")
            
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            
            if not numeric_cols:
                st.warning("No numeric columns found!")
            else:
                method = st.selectbox("Method", ["iqr", "z_score", "isolation_forest"])
                columns = st.multiselect("Select columns", numeric_cols, default=numeric_cols[:3])
                
                if method == "iqr":
                    multiplier = st.slider("IQR Multiplier", 1.0, 3.0, 1.5, 0.1)
                    kwargs = {"multiplier": multiplier}
                elif method == "z_score":
                    threshold = st.slider("Z-Score Threshold", 2.0, 4.0, 3.0, 0.1)
                    kwargs = {"threshold": threshold}
                else:
                    contamination = st.slider("Contamination", 0.01, 0.3, 0.1, 0.01)
                    kwargs = {"contamination": contamination}
                
                if st.button("Remove Outliers"):
                    cleaner = DataCleaner(df)
                    df = cleaner.remove_outliers(method=method, columns=columns, **kwargs)
                    st.session_state.df = df
                    st.success("✅ Outliers removed!")
                    st.rerun()
        
        elif operation == "Scale Features":
            st.markdown("### ⚖️ Scale Features")
            
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            
            if not numeric_cols:
                st.warning("No numeric columns found!")
            else:
                method = st.selectbox(
                    "Scaling Method",
                    ["standard_scaler", "min_max_scaler", "robust_scaler", "max_abs_scaler"]
                )
                columns = st.multiselect("Select columns", numeric_cols)
                
                if columns and st.button("Scale"):
                    scaler = DataScaler(df)
                    df, scalers = scaler.scale_columns(columns, method)
                    st.session_state.df = df
                    st.success("✅ Features scaled!")
                    st.rerun()
        
        elif operation == "Encode Categories":
            st.markdown("### 🔤 Encode Categories")
            
            cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            
            if not cat_cols:
                st.warning("No categorical columns found!")
            else:
                method = st.selectbox(
                    "Encoding Method",
                    ["label_encoding", "one_hot_encoding", "frequency_encoding"]
                )
                columns = st.multiselect("Select columns", cat_cols)
                
                if columns and st.button("Encode"):
                    encoder = DataEncoder(df)
                    df, encoders = encoder.encode_columns(columns, method)
                    st.session_state.df = df
                    st.success("✅ Categories encoded!")
                    st.rerun()
        
        elif operation == "Engineer Features":
            st.markdown("### ⚙️ Engineer Features")
            
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            
            feature_type = st.selectbox(
                "Feature Type",
                [
                    "Polynomial Features",
                    "Interaction Features",
                    "Log Transform",
                    "Power Transform",
                    "Date Features"
                ]
            )
            
            engineer = FeatureEngineer(df)
            
            if feature_type == "Polynomial Features":
                columns = st.multiselect("Select columns", numeric_cols)
                degree = st.slider("Degree", 2, 4, 2)
                
                if columns and st.button("Create"):
                    df = engineer.create_polynomial_features(columns, degree)
                    st.session_state.df = df
                    st.success("✅ Features created!")
                    st.rerun()
            
            elif feature_type == "Log Transform":
                columns = st.multiselect("Select columns", numeric_cols)
                base = st.selectbox("Base", ["natural", "10", "2"])
                
                if columns and st.button("Transform"):
                    df = engineer.apply_log_transform(columns, base)
                    st.session_state.df = df
                    st.success("✅ Transform applied!")
                    st.rerun()
    
    with tab2:
        st.markdown("### 📊 Current Data Preview")
        st.dataframe(st.session_state.df.head(20), use_container_width=True, height=400)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rows", len(st.session_state.df))
        with col2:
            st.metric("Columns", len(st.session_state.df.columns))
        with col3:
            quality_pct = (1 - st.session_state.df.isnull().sum().sum() / (len(st.session_state.df) * len(st.session_state.df.columns))) * 100
            st.metric("Quality", f"{quality_pct:.1f}%")
        
        # Export cleaned data
        st.markdown("---")
        st.markdown("### 📥 Export Cleaned Data")
        
        col1, col2 = st.columns(2)
        with col1:
            export_format = st.selectbox("Format", ["csv", "excel", "parquet", "json"])
        with col2:
            compression = st.selectbox("Compression", ["none", "gzip", "bz2"])
        
        if st.button("📥 Download Cleaned Data"):
            try:
                data = export_dataframe(
                    st.session_state.df,
                    format=export_format,
                    compression=None if compression == "none" else compression
                )
                st.download_button(
                    label=f"Download {export_format.upper()}",
                    data=data,
                    file_name=f"cleaned_data.{export_format}",
                    mime="application/octet-stream"
                )
            except Exception as e:
                st.error(f"Error exporting: {e}")

if __name__ == "__main__":
    main()
