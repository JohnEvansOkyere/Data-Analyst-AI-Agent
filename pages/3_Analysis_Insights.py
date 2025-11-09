"""
Analysis & Insights Page - AI Queries and Statistical Tests
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
import time
import io
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.auth import check_authentication
from core.ml_engine import GroqClient, generate_sql_query, execute_query, interpret_results
from core.data_analysis import DataAnalyzer
from utils.logger import get_logger, audit_logger

logger = get_logger(__name__)

st.set_page_config(page_title="Analysis & Insights", page_icon="📈", layout="wide")

def main():
    if not check_authentication():
        return
    
    st.title("📈 Analysis & Insights")
    st.markdown("Ask questions in natural language or run statistical tests")
    
    if 'df' not in st.session_state:
        st.warning("⚠️ Please upload data first!")
        st.info("Go to '📂 Data Upload' page to upload your dataset")
        return
    
    df = st.session_state.df
    
    # Check for API key
    if 'groq_key' not in st.session_state:
        st.error("🔑 Please enter your xAI API key in the sidebar first!")
        with st.sidebar:
            st.markdown("### 🔑 xAI API Key")
            xai_key = st.text_input("Enter API key", type="password", placeholder="xai-...")
            if xai_key:
                st.session_state.groq_key = xai_key
                st.success("✅ API key set!")
                st.rerun()
        return
    
    # Tabs for different analysis types
    tab1, tab2, tab3 = st.tabs(["🤖 AI Queries", "📊 Statistical Tests", "🔗 Correlations"])
    
    # ==================== AI QUERIES TAB ====================
    with tab1:
        st.markdown("### 🤖 Ask Questions About Your Data")
        
        # Quick action buttons
        st.markdown("**Quick Actions:**")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📊 Summary", key="summary"):
                st.session_state.quick_query = "Show me summary statistics"
        with col2:
            if st.button("🏆 Top 10", key="top10"):
                st.session_state.quick_query = "Show me the top 10 records"
        with col3:
            if st.button("🔍 Data Info", key="info"):
                st.session_state.quick_query = "What columns do I have?"
        with col4:
            if st.button("📈 Trends", key="trends"):
                st.session_state.quick_query = "Show me any interesting trends"
        
        # Query input
        user_query = st.text_area(
            "Enter your question:",
            value=st.session_state.get('quick_query', ''),
            placeholder="e.g., What are the top 5 products by sales?",
            height=100,
            key="query_input"
        )
        
        if 'quick_query' in st.session_state:
            del st.session_state.quick_query
        
        # Analyze button
        if st.button("🚀 Analyze with Grok AI", type="primary", use_container_width=True):
            if not user_query.strip():
                st.warning("Please enter a question!")
            else:
                start_time = time.time()
                
                with st.spinner("🧠 Generating SQL query..."):
                    try:
                        client = GroqClient(st.session_state.groq_key)
                        sql_query = generate_sql_query(
                            user_query,
                            df.columns.tolist(),
                            "data",
                            client
                        )
                    except Exception as e:
                        st.error(f"Error: {e}")
                        return
                
                if sql_query:
                    st.markdown("### 🔧 Generated SQL")
                    st.code(sql_query, language="sql")
                    
                    with st.spinner("⚡ Executing query..."):
                        try:
                            results = execute_query(df, sql_query)
                        except Exception as e:
                            st.error(f"Query error: {e}")
                            return
                    
                    if results is not None and len(results) > 0:
                        st.markdown("### 📊 Results")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Rows", len(results))
                        with col2:
                            st.metric("Columns", len(results.columns))
                        with col3:
                            duration = time.time() - start_time
                            st.metric("Time", f"{duration:.2f}s")
                        
                        st.dataframe(results, use_container_width=True, height=400)
                        
                        # Download button
                        csv = results.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            "📥 Download Results",
                            csv,
                            f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            "text/csv"
                        )
                        
                        # AI Interpretation
                        with st.spinner("🎯 Generating insights..."):
                            try:
                                interpretation = interpret_results(
                                    user_query, sql_query, results, client
                                )
                                st.markdown("### 💡 AI Insights")
                                st.info(interpretation)
                            except Exception as e:
                                st.warning(f"Could not generate insights: {e}")
                        
                        # Log the analysis
                        audit_logger.log_user_action(
                            st.session_state.username,
                            "ai_query",
                            f"Query: {user_query[:50]}..."
                        )
                    else:
                        st.warning("No results returned")
    
    # ==================== STATISTICAL TESTS TAB ====================
    with tab2:
        st.markdown("### 📊 Statistical Tests")
        
        analyzer = DataAnalyzer(df)
        
        test_type = st.selectbox(
            "Select Test",
            [
                "T-Test (Compare 2 Groups)",
                "ANOVA (Compare Multiple Groups)",
                "Chi-Square (Independence)",
                "Normality Test",
                "Summary Statistics"
            ]
        )
        
        if test_type == "T-Test (Compare 2 Groups)":
            st.markdown("**Independent T-Test**")
            
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
            
            if not numeric_cols or not categorical_cols:
                st.warning("Need both numeric and categorical columns for T-test")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    numeric_col = st.selectbox("Numeric Column", numeric_cols)
                with col2:
                    group_col = st.selectbox("Group Column", categorical_cols)
                
                if st.button("Run T-Test"):
                    try:
                        result = analyzer.perform_t_test(numeric_col, group_col)
                        
                        st.markdown("#### Results:")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("T-Statistic", f"{result['statistic']:.4f}")
                        with col2:
                            st.metric("P-Value", f"{result['p_value']:.4f}")
                        with col3:
                            status = "✅ Significant" if result['significant'] else "❌ Not Significant"
                            st.metric("Significance", status)
                        
                        st.info(f"**Interpretation:** {result['interpretation']}")
                    except Exception as e:
                        st.error(f"Error: {e}")
        
        elif test_type == "ANOVA (Compare Multiple Groups)":
            st.markdown("**One-Way ANOVA**")
            
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
            
            if not numeric_cols or not categorical_cols:
                st.warning("Need both numeric and categorical columns for ANOVA")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    numeric_col = st.selectbox("Numeric Column", numeric_cols)
                with col2:
                    group_col = st.selectbox("Group Column", categorical_cols)
                
                if st.button("Run ANOVA"):
                    try:
                        result = analyzer.perform_anova(numeric_col, group_col)
                        
                        st.markdown("#### Results:")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("F-Statistic", f"{result['statistic']:.4f}")
                        with col2:
                            st.metric("P-Value", f"{result['p_value']:.4f}")
                        with col3:
                            st.metric("Groups", result['n_groups'])
                        
                        st.info(f"**Interpretation:** {result['interpretation']}")
                    except Exception as e:
                        st.error(f"Error: {e}")
        
        elif test_type == "Chi-Square (Independence)":
            st.markdown("**Chi-Square Test of Independence**")
            
            categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
            
            if len(categorical_cols) < 2:
                st.warning("Need at least 2 categorical columns")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    cat_col1 = st.selectbox("First Column", categorical_cols)
                with col2:
                    cat_col2 = st.selectbox("Second Column", [c for c in categorical_cols if c != cat_col1])
                
                if st.button("Run Chi-Square Test"):
                    try:
                        result = analyzer.perform_chi_square(cat_col1, cat_col2)
                        
                        st.markdown("#### Results:")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Chi-Square", f"{result['chi2_statistic']:.4f}")
                        with col2:
                            st.metric("P-Value", f"{result['p_value']:.4f}")
                        with col3:
                            st.metric("DOF", result['degrees_of_freedom'])
                        
                        st.info(f"**Interpretation:** {result['interpretation']}")
                    except Exception as e:
                        st.error(f"Error: {e}")
        
        elif test_type == "Normality Test":
            st.markdown("**Shapiro-Wilk Normality Test**")
            
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            
            if not numeric_cols:
                st.warning("No numeric columns found")
            else:
                selected_cols = st.multiselect("Select Columns", numeric_cols, default=numeric_cols[:3])
                
                if st.button("Run Normality Test"):
                    if selected_cols:
                        try:
                            results = analyzer.test_normality(selected_cols)
                            
                            st.markdown("#### Results:")
                            result_df = pd.DataFrame(results).T
                            result_df['is_normal'] = result_df['is_normal'].map({True: '✅ Normal', False: '❌ Not Normal'})
                            st.dataframe(result_df, use_container_width=True)
                        except Exception as e:
                            st.error(f"Error: {e}")
        
        elif test_type == "Summary Statistics":
            st.markdown("**Comprehensive Summary Statistics**")
            
            summary = analyzer.generate_summary_statistics()
            
            if summary['basic_stats']:
                st.markdown("#### Numeric Columns")
                st.dataframe(pd.DataFrame(summary['basic_stats']), use_container_width=True)
            
            if summary.get('categorical_stats'):
                st.markdown("#### Categorical Columns")
                for col, stats in summary['categorical_stats'].items():
                    with st.expander(f"📊 {col}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Unique Values", stats['unique_values'])
                            st.metric("Missing", stats['missing'])
                        with col2:
                            st.write("**Top Values:**")
                            st.write(pd.DataFrame(stats['top_values'].items(), columns=['Value', 'Count']))
    
    # ==================== CORRELATIONS TAB ====================
    with tab3:
        st.markdown("### 🔗 Correlation Analysis")
        
        analyzer = DataAnalyzer(df)
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        if len(numeric_cols) < 2:
            st.warning("Need at least 2 numeric columns for correlation analysis")
        else:
            col1, col2 = st.columns(2)
            with col1:
                method = st.selectbox("Method", ["pearson", "spearman", "kendall"])
            with col2:
                threshold = st.slider("Show correlations above", 0.0, 1.0, 0.0, 0.05)
            
            if st.button("Calculate Correlations"):
                try:
                    corr_matrix = analyzer.calculate_correlations(method, threshold)
                    
                    if not corr_matrix.empty:
                        st.markdown("#### Correlation Matrix")
                        st.dataframe(corr_matrix.style.background_gradient(cmap='RdBu_r', vmin=-1, vmax=1), 
                                   use_container_width=True)
                        
                        # Find strong correlations
                        st.markdown("#### Strong Correlations")
                        strong_corr = []
                        for i in range(len(corr_matrix.columns)):
                            for j in range(i+1, len(corr_matrix.columns)):
                                corr_val = corr_matrix.iloc[i, j]
                                if abs(corr_val) > 0.5:
                                    strong_corr.append({
                                        'Variable 1': corr_matrix.columns[i],
                                        'Variable 2': corr_matrix.columns[j],
                                        'Correlation': f"{corr_val:.3f}"
                                    })
                        
                        if strong_corr:
                            st.dataframe(pd.DataFrame(strong_corr), use_container_width=True)
                        else:
                            st.info("No strong correlations found (|r| > 0.5)")
                    else:
                        st.info("No correlations to display")
                        
                except Exception as e:
                    st.error(f"Error: {e}")

if __name__ == "__main__":
    main()