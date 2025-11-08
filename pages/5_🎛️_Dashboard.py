"""
Dashboard Page - Overview of all metrics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.auth import check_authentication
from utils.helpers import calculate_data_quality_score, get_column_info
from utils.logger import get_logger

logger = get_logger(__name__)

st.set_page_config(page_title="Dashboard", page_icon="🎛️", layout="wide")

def main():
    if not check_authentication():
        return
    
    st.title("🎛️ Data Analysis Dashboard")
    st.markdown("Comprehensive overview of your data")
    
    if 'df' not in st.session_state:
        st.warning("⚠️ Please upload data first!")
        st.info("Go to '📂 Data Upload' page to upload your dataset")
        return
    
    df = st.session_state.df
    
    # ==================== KEY METRICS ====================
    st.markdown("### 📊 Key Metrics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📋 Total Rows", f"{len(df):,}")
    
    with col2:
        st.metric("📊 Total Columns", len(df.columns))
    
    with col3:
        numeric_cols = len(df.select_dtypes(include=['number']).columns)
        st.metric("🔢 Numeric Columns", numeric_cols)
    
    with col4:
        text_cols = len(df.select_dtypes(include=['object']).columns)
        st.metric("📝 Text Columns", text_cols)
    
    with col5:
        memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
        st.metric("💾 Memory", f"{memory_mb:.1f} MB")
    
    # ==================== DATA QUALITY ====================
    st.markdown("---")
    st.markdown("### 🎯 Data Quality Overview")
    
    quality = calculate_data_quality_score(df)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Quality Score",
            f"{quality['quality_score']}%",
            delta="Good" if quality['quality_score'] > 80 else "Needs Work"
        )
    
    with col2:
        st.metric("Completeness", f"{quality['completeness']}%")
    
    with col3:
        st.metric("Uniqueness", f"{quality['uniqueness']}%")
    
    with col4:
        st.metric("Missing Cells", f"{quality['missing_cells']:,}")
    
    # Quality gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=quality['quality_score'],
        title={'text': "Overall Data Quality"},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 80], 'color': "gray"},
                {'range': [80, 100], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)
    
    # ==================== COLUMN DETAILS ====================
    st.markdown("---")
    st.markdown("### 📋 Column Details")
    
    column_info = get_column_info(df)
    
    # Color code null percentages
    def color_null_pct(val):
        if val > 50:
            color = 'background-color: #ffcccc'
        elif val > 20:
            color = 'background-color: #fff4cc'
        else:
            color = 'background-color: #ccffcc'
        return color
    
    styled_df = column_info.style.applymap(color_null_pct, subset=['Null %'])
    st.dataframe(styled_df, use_container_width=True, height=400)
    
    # ==================== MISSING DATA VISUALIZATION ====================
    st.markdown("---")
    st.markdown("### 🔍 Missing Data Analysis")
    
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    missing_df = pd.DataFrame({
        'Column': missing.index,
        'Missing Count': missing.values,
        'Missing %': missing_pct.values
    }).sort_values('Missing Count', ascending=False)
    
    missing_df = missing_df[missing_df['Missing Count'] > 0]
    
    if len(missing_df) > 0:
        fig = px.bar(missing_df, x='Column', y='Missing %', 
                    title="Missing Data by Column",
                    color='Missing %',
                    color_continuous_scale='Reds')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("✅ No missing data found!")
    
    # ==================== NUMERIC DISTRIBUTIONS ====================
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if numeric_cols:
        st.markdown("---")
        st.markdown("### 📊 Numeric Column Distributions")
        
        # Select columns to display
        display_cols = st.multiselect(
            "Select columns to display",
            numeric_cols,
            default=numeric_cols[:min(4, len(numeric_cols))]
        )
        
        if display_cols:
            for i in range(0, len(display_cols), 2):
                col1, col2 = st.columns(2)
                
                with col1:
                    if i < len(display_cols):
                        col_name = display_cols[i]
                        fig = px.histogram(df, x=col_name, title=f"{col_name} Distribution")
                        fig.update_layout(height=300, template='plotly_white')
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    if i + 1 < len(display_cols):
                        col_name = display_cols[i + 1]
                        fig = px.box(df, y=col_name, title=f"{col_name} Box Plot")
                        fig.update_layout(height=300, template='plotly_white')
                        st.plotly_chart(fig, use_container_width=True)
    
    # ==================== CATEGORICAL OVERVIEW ====================
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    if categorical_cols:
        st.markdown("---")
        st.markdown("### 📋 Categorical Columns Overview")
        
        for col in categorical_cols[:3]:
            with st.expander(f"📊 {col}"):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    unique_count = df[col].nunique()
                    most_common = df[col].mode()[0] if len(df[col].mode()) > 0 else "N/A"
                    
                    st.metric("Unique Values", unique_count)
                    st.metric("Most Common", most_common)
                    st.metric("Missing", df[col].isnull().sum())
                
                with col2:
                    value_counts = df[col].value_counts().head(10)
                    fig = px.pie(values=value_counts.values, names=value_counts.index,
                               title=f"Top 10 {col}")
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
    
    # ==================== SUMMARY STATISTICS ====================
    if numeric_cols:
        st.markdown("---")
        st.markdown("### 📈 Summary Statistics")
        
        summary = df[numeric_cols].describe().T
        st.dataframe(summary, use_container_width=True)

if __name__ == "__main__":
    main()