"""
Visualizations Page - Interactive Charts
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.auth import check_authentication
from utils.logger import get_logger

logger = get_logger(__name__)

st.set_page_config(page_title="Visualizations", page_icon="📊", layout="wide")

def create_chart(df, chart_type, x_col, y_col=None, color_col=None, title=""):
    """Create different types of charts"""
    try:
        if chart_type == "Histogram":
            fig = px.histogram(df, x=x_col, color=color_col, title=title)
        
        elif chart_type == "Scatter":
            fig = px.scatter(df, x=x_col, y=y_col, color=color_col, title=title)
        
        elif chart_type == "Line":
            fig = px.line(df, x=x_col, y=y_col, color=color_col, title=title)
        
        elif chart_type == "Bar":
            if y_col:
                fig = px.bar(df, x=x_col, y=y_col, color=color_col, title=title)
            else:
                value_counts = df[x_col].value_counts().head(20)
                fig = px.bar(x=value_counts.index, y=value_counts.values, 
                           title=title or f"Distribution of {x_col}")
                fig.update_layout(xaxis_title=x_col, yaxis_title="Count")
        
        elif chart_type == "Box":
            fig = px.box(df, y=y_col or x_col, color=color_col, title=title)
        
        elif chart_type == "Violin":
            fig = px.violin(df, y=y_col or x_col, color=color_col, title=title)
        
        elif chart_type == "Pie":
            value_counts = df[x_col].value_counts().head(10)
            fig = px.pie(values=value_counts.values, names=value_counts.index, title=title)
        
        fig.update_layout(template='plotly_white', height=500)
        return fig
    
    except Exception as e:
        logger.error(f"Chart creation error: {e}")
        return None

def main():
    if not check_authentication():
        return
    
    st.title("📊 Interactive Visualizations")
    st.markdown("Create custom charts and explore your data visually")
    
    if 'df' not in st.session_state:
        st.warning("⚠️ Please upload data first!")
        st.info("Go to '📂 Data Upload' page to upload your dataset")
        return
    
    df = st.session_state.df
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["🎨 Custom Charts", "📈 Quick Insights", "🗺️ Advanced"])
    
    # ==================== CUSTOM CHARTS TAB ====================
    with tab1:
        st.markdown("### 🎨 Create Custom Chart")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("**Chart Settings**")
            
            chart_type = st.selectbox(
                "Chart Type",
                ["Histogram", "Scatter", "Line", "Bar", "Box", "Violin", "Pie"]
            )
            
            # Get column types
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
            all_cols = df.columns.tolist()
            
            # Column selection based on chart type
            if chart_type in ["Histogram", "Box", "Violin"]:
                x_col = st.selectbox("Column", numeric_cols if chart_type == "Histogram" else all_cols)
                y_col = None
            
            elif chart_type == "Scatter":
                x_col = st.selectbox("X-Axis", numeric_cols)
                y_col = st.selectbox("Y-Axis", [c for c in numeric_cols if c != x_col])
            
            elif chart_type == "Line":
                x_col = st.selectbox("X-Axis", all_cols)
                y_col = st.selectbox("Y-Axis", numeric_cols)
            
            elif chart_type == "Bar":
                x_col = st.selectbox("X-Axis", all_cols)
                y_col = st.selectbox("Y-Axis (optional)", [None] + numeric_cols)
            
            elif chart_type == "Pie":
                x_col = st.selectbox("Category Column", categorical_cols if categorical_cols else all_cols)
                y_col = None
            
            # Color option
            color_col = st.selectbox("Color By (optional)", [None] + categorical_cols)
            
            # Title
            chart_title = st.text_input("Chart Title", f"{chart_type} of {x_col}")
            
            create_button = st.button("📊 Create Chart", type="primary", use_container_width=True)
        
        with col2:
            if create_button:
                with st.spinner("Creating chart..."):
                    fig = create_chart(df, chart_type, x_col, y_col, color_col, chart_title)
                    
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Download button
                        st.download_button(
                            "📥 Download Chart HTML",
                            fig.to_html(),
                            f"{chart_type.lower()}_chart.html",
                            "text/html"
                        )
                    else:
                        st.error("Could not create chart. Check your column selections.")
            else:
                st.info("👈 Configure your chart settings and click 'Create Chart'")
    
    # ==================== QUICK INSIGHTS TAB ====================
    with tab2:
        st.markdown("### 📈 Quick Visual Insights")
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        if numeric_cols:
            st.markdown("#### 📊 Numeric Distributions")
            
            for i in range(0, min(6, len(numeric_cols)), 2):
                col1, col2 = st.columns(2)
                
                with col1:
                    if i < len(numeric_cols):
                        col_name = numeric_cols[i]
                        fig = px.histogram(df, x=col_name, title=f"Distribution of {col_name}")
                        fig.update_layout(template='plotly_white', height=300)
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    if i + 1 < len(numeric_cols):
                        col_name = numeric_cols[i + 1]
                        fig = px.box(df, y=col_name, title=f"Box Plot of {col_name}")
                        fig.update_layout(template='plotly_white', height=300)
                        st.plotly_chart(fig, use_container_width=True)
        
        if categorical_cols:
            st.markdown("#### 📋 Categorical Distributions")
            
            for col_name in categorical_cols[:4]:
                value_counts = df[col_name].value_counts().head(10)
                fig = px.bar(x=value_counts.index, y=value_counts.values, 
                           title=f"Top 10 {col_name}")
                fig.update_layout(template='plotly_white', height=300, 
                                xaxis_title=col_name, yaxis_title="Count")
                st.plotly_chart(fig, use_container_width=True)
        
        # Correlation heatmap
        if len(numeric_cols) > 1:
            st.markdown("#### 🔥 Correlation Heatmap")
            corr_matrix = df[numeric_cols].corr()
            fig = px.imshow(corr_matrix, 
                          title="Correlation Matrix",
                          color_continuous_scale='RdBu_r',
                          aspect='auto')
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
    
    # ==================== ADVANCED TAB ====================
    with tab3:
        st.markdown("### 🗺️ Advanced Visualizations")
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        if len(numeric_cols) >= 2:
            st.markdown("#### 🎯 Scatter Matrix")
            
            selected_cols = st.multiselect(
                "Select columns for scatter matrix",
                numeric_cols,
                default=numeric_cols[:min(4, len(numeric_cols))]
            )
            
            if len(selected_cols) >= 2:
                fig = px.scatter_matrix(df[selected_cols])
                fig.update_layout(height=800)
                st.plotly_chart(fig, use_container_width=True)
        
        # Parallel coordinates
        if len(numeric_cols) >= 3:
            st.markdown("#### 📊 Parallel Coordinates")
            
            selected_cols = st.multiselect(
                "Select columns for parallel coordinates",
                numeric_cols,
                default=numeric_cols[:min(5, len(numeric_cols))],
                key="parallel"
            )
            
            if len(selected_cols) >= 2:
                fig = px.parallel_coordinates(df, dimensions=selected_cols)
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()