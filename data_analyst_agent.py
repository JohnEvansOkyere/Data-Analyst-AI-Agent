import json
import tempfile
import csv
import streamlit as st
import pandas as pd
import sqlite3
import io
from openai import OpenAI
import re

# Function to preprocess and save the uploaded file
def preprocess_and_save(file):
    try:
        # Read the uploaded file into a DataFrame
        if file.name.endswith('.csv'):
            df = pd.read_csv(file, encoding='utf-8', na_values=['NA', 'N/A', 'missing'])
        elif file.name.endswith('.xlsx'):
            df = pd.read_excel(file, na_values=['NA', 'N/A', 'missing'])
        else:
            st.error("Unsupported file format. Please upload a CSV or Excel file.")
            return None, None, None
        
        # Clean column names
        df.columns = df.columns.str.strip().str.replace(' ', '_').str.replace('[^A-Za-z0-9_]', '', regex=True)
        
        # Parse dates and numeric columns
        for col in df.columns:
            if 'date' in col.lower():
                df[col] = pd.to_datetime(df[col], errors='coerce')
            elif df[col].dtype == 'object':
                try:
                    df[col] = pd.to_numeric(df[col], errors='ignore')
                except (ValueError, TypeError):
                    pass
        
        return df
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return None

def generate_sql_query(user_query, columns, table_name="data", client=None):
    """Generate SQL query using OpenAI"""
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
    
    SQL Query:
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.1
        )
        
        sql_query = response.choices[0].message.content.strip()
        
        # Clean the SQL query
        sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
        if sql_query.startswith('SELECT') or sql_query.startswith('select'):
            return sql_query
        else:
            # Extract SQL from response if it's wrapped in text
            lines = sql_query.split('\n')
            for line in lines:
                line = line.strip()
                if line.upper().startswith('SELECT'):
                    return line
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
    """Generate interpretation of results using OpenAI"""
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
    
    Keep the response clear and business-friendly.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Results retrieved successfully, but couldn't generate interpretation: {e}"

# Streamlit app
st.title("📊 Data Analyst Agent")
st.markdown("Upload your data and ask questions in natural language!")

# Sidebar for API keys
with st.sidebar:
    st.header("Configuration")
    openai_key = st.text_input("OpenAI API Key", type="password", placeholder="Enter your OpenAI API key")
    if openai_key:
        st.session_state.openai_key = openai_key
        st.success("✅ API key saved!")
    else:
        st.warning("⚠️ Please enter your OpenAI API key to proceed.")
    
    st.markdown("---")
    st.markdown("### How to use:")
    st.markdown("""
    1. Enter your OpenAI API key
    2. Upload a CSV or Excel file
    3. Ask questions about your data
    4. Get SQL queries and insights automatically
    """)

# File upload widget
uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None and "openai_key" in st.session_state:
    # Initialize OpenAI client
    try:
        client = OpenAI(api_key=st.session_state.openai_key)
    except Exception as e:
        st.error(f"Failed to initialize OpenAI client: {e}")
        st.stop()
    
    # Preprocess the uploaded file
    df = preprocess_and_save(uploaded_file)
    
    if df is not None:
        st.success(f"✅ File uploaded successfully! ({len(df)} rows, {len(df.columns)} columns)")
        
        # Display basic info about the dataset
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rows", len(df))
        with col2:
            st.metric("Columns", len(df.columns))
        with col3:
            st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
        
        # Show data preview
        with st.expander("📋 Data Preview", expanded=True):
            st.dataframe(df.head(10), use_container_width=True)
        
        # Show column information
        with st.expander("📊 Column Information"):
            col_info = pd.DataFrame({
                'Column': df.columns,
                'Type': df.dtypes.astype(str),
                'Non-Null Count': df.count(),
                'Null Count': df.isnull().sum()
            })
            st.dataframe(col_info, use_container_width=True)
        
        st.markdown("---")
        
        # Query input
        st.subheader("🤔 Ask a Question About Your Data")
        
        # Sample questions
        with st.expander("💡 Example Questions"):
            st.markdown("""
            - What are the top 10 values by [column name]?
            - Show me the average of [column name] by [another column]
            - How many unique values are in [column name]?
            - What's the distribution of [column name]?
            - Show me records where [column name] is greater than [value]
            """)
        
        user_query = st.text_area(
            "Enter your question:", 
            placeholder="e.g., What are the top 5 products by sales?",
            height=100
        )
        
        if st.button("🔍 Analyze", type="primary", use_container_width=True):
            if not user_query.strip():
                st.warning("Please enter a question.")
            else:
                with st.spinner('🧠 Generating SQL query...'):
                    # Generate SQL query
                    sql_query = generate_sql_query(
                        user_query, 
                        df.columns.tolist(), 
                        "data", 
                        client
                    )
                
                if sql_query:
                    st.markdown("### 🔧 Generated SQL Query")
                    st.code(sql_query, language="sql")
                    
                    with st.spinner('⚡ Executing query...'):
                        # Execute query
                        results = execute_query(df, sql_query)
                    
                    if results is not None and len(results) > 0:
                        st.markdown("### 📊 Query Results")
                        st.dataframe(results, use_container_width=True)
                        
                        # Download results
                        csv_buffer = io.StringIO()
                        results.to_csv(csv_buffer, index=False)
                        st.download_button(
                            label="📥 Download Results as CSV",
                            data=csv_buffer.getvalue(),
                            file_name="query_results.csv",
                            mime="text/csv"
                        )
                        
                        # Generate interpretation
                        with st.spinner('🎯 Generating insights...'):
                            interpretation = interpret_results(
                                user_query, 
                                sql_query, 
                                results, 
                                client
                            )
                        
                        st.markdown("### 💡 Analysis & Insights")
                        st.markdown(interpretation)
                        
                    elif results is not None and len(results) == 0:
                        st.warning("Query executed successfully but returned no results.")
                    else:
                        st.error("Failed to execute the query. Please try rephrasing your question.")
                else:
                    st.error("Failed to generate SQL query. Please try rephrasing your question.")

elif uploaded_file is not None:
    st.warning("⚠️ Please enter your OpenAI API key in the sidebar to continue.")
else:
    st.info("👆 Please upload a CSV or Excel file to get started.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Built with ❤️ using Streamlit, OpenAI, and Pandas"
    "</div>", 
    unsafe_allow_html=True
)