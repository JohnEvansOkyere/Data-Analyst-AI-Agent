import json
import tempfile
import csv
import pandas as pd
import sqlite3
import io
import requests
import re
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)

# xAI Grok API client class
class GroqClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.x.ai/v1"
        
    def chat_completion(self, messages, model="grok-4-fast-reasoning", max_tokens=500, temperature=0.1):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"API Response Status: {response.status_code}")
                logger.error(f"API Response: {response.text}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"xAI API error: {str(e)}")
            raise Exception(f"xAI API error: {str(e)}")

def preprocess_and_save(file):
    try:
        if file.name.endswith('.csv'):
            file.seek(0)
            df = pd.read_csv(file, encoding='utf-8', na_values=['NA', 'N/A', 'missing'])
        elif file.name.endswith('.xlsx'):
            file.seek(0)
            df = pd.read_excel(file, na_values=['NA', 'N/A', 'missing'])
        else:
            raise ValueError("Unsupported file format. Please upload a CSV or Excel file.")
        
        if df.empty or len(df.columns) == 0:
            raise ValueError("Uploaded file has no data or no valid columns.")

        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
            .str.replace(' ', '_')
            .str.replace('[^A-Za-z0-9_]', '', regex=True)
        )
        
        for col in df.columns:
            if 'date' in col.lower():
                df[col] = pd.to_datetime(df[col], errors='coerce')
            elif df[col].dtype == 'object':
                try:
                    df[col] = pd.to_numeric(df[col])
                except (ValueError, TypeError):
                    pass
        
        logger.info(f"Data preprocessed: {len(df)} rows, {len(df.columns)} columns")
        return df

    except Exception as e:
        logger.error(f"Error processing file: {e}")
        raise Exception(f"Error processing file: {e}")

def generate_sql_query(user_query, columns, table_name="data", client=None):
    """
    Generate SQL query from natural language using xAI Grok
    
    Args:
        user_query: Natural language question
        columns: List of column names
        table_name: Name of the table (default: "data")
        client: GroqClient instance
    
    Returns:
        str: SQL query
    """
    column_info = ", ".join(columns)
    
    # Enhanced prompt with specific examples
    prompt = f"""You are an expert SQL query generator. Convert the user's question into a valid, complete, executable SQL query.

        DATABASE SCHEMA:
        Table name: {table_name}
        Columns: {column_info}

        CRITICAL INSTRUCTIONS:
        1. ALWAYS write a COMPLETE SQL query with SELECT, FROM, and any necessary clauses
        2. Column names are CASE-SENSITIVE - use them EXACTLY as shown above
        3. ALWAYS include "FROM {table_name}" in your query
        4. Use standard SQLite syntax

        QUERY PATTERNS:

        For "most/common/popular [column]":
        Example: "What is the most used PreferredLoginDevice?"
        SQL: SELECT PreferredLoginDevice, COUNT(*) as count FROM {table_name} GROUP BY PreferredLoginDevice ORDER BY count DESC LIMIT 1

        For "most [column] by [another column]":
        Example: "What is the most PreferredLoginDevice by Gender?"
        SQL: SELECT Gender, PreferredLoginDevice, COUNT(*) as count FROM {table_name} GROUP BY Gender, PreferredLoginDevice ORDER BY Gender, count DESC

        For "breakdown/distribution by [column]":
        Example: "Distribution by Gender"
        SQL: SELECT Gender, COUNT(*) as count FROM {table_name} GROUP BY Gender

        For "average/mean":
        Example: "Average Tenure"
        SQL: SELECT AVG(Tenure) as average FROM {table_name}

        For "top N":
        Example: "Top 5 by OrderCount"
        SQL: SELECT * FROM {table_name} ORDER BY OrderCount DESC LIMIT 5

        For "comparison":
        Example: "Compare satisfaction by MaritalStatus"
        SQL: SELECT MaritalStatus, AVG(SatisfactionScore) as avg_score FROM {table_name} GROUP BY MaritalStatus

        For "total/count with filter":
        Example: "How many churned?"
        SQL: SELECT COUNT(*) as total FROM {table_name} WHERE Churn = 1

        USER QUESTION: {user_query}

        IMPORTANT: Return ONLY the complete SQL query. No explanations, no markdown, no code blocks, just the raw SQL query."""
            
    try:
        messages = [{"role": "user", "content": prompt}]
        
        # Increase max_tokens for complex queries
        response = client.chat_completion(
            messages=messages,
            max_tokens=500,  # Increased from 300
            temperature=0.1
        )
        
        # Get the raw response
        raw_sql = response['choices'][0]['message']['content'].strip()
        logger.info(f"Raw AI Response: {raw_sql}")
        
        # Clean up the response
        sql_query = raw_sql
        
        # Remove markdown code blocks
        sql_query = sql_query.replace('```sql', '').replace('```SQL', '').replace('```', '').strip()
        
        # Remove any "SQL:" prefix
        if sql_query.upper().startswith('SQL:'):
            sql_query = sql_query[4:].strip()
        
        # Remove any explanatory text before SELECT
        if 'SELECT' in sql_query.upper():
            select_index = sql_query.upper().index('SELECT')
            sql_query = sql_query[select_index:]
        
        # If multiple lines, combine them intelligently
        lines = [line.strip() for line in sql_query.split('\n') if line.strip()]
        if len(lines) > 1:
            # Check if first line is complete
            first_line_upper = lines[0].upper()
            if 'SELECT' in first_line_upper and 'FROM' in first_line_upper:
                # First line is complete, use it
                sql_query = lines[0]
            else:
                # Combine all lines
                sql_query = ' '.join(lines)
        
        # Remove trailing semicolon
        sql_query = sql_query.rstrip(';').strip()
        
        # CRITICAL: Validate and fix missing FROM clause
        sql_upper = sql_query.upper()
        if 'SELECT' in sql_upper and 'FROM' not in sql_upper:
            logger.warning(f"Missing FROM clause in: {sql_query}")
            
            # Try to intelligently insert FROM clause
            # Find insertion point (before WHERE, GROUP BY, ORDER BY, or at end)
            insert_keywords = ['WHERE', 'GROUP BY', 'HAVING', 'ORDER BY', 'LIMIT']
            insert_pos = len(sql_query)
            
            for keyword in insert_keywords:
                if keyword in sql_upper:
                    pos = sql_upper.index(keyword)
                    if pos < insert_pos:
                        insert_pos = pos
            
            # Insert FROM clause
            before = sql_query[:insert_pos].strip()
            after = sql_query[insert_pos:].strip()
            sql_query = f"{before} FROM {table_name} {after}".strip()
            
            logger.info(f"Fixed SQL with FROM clause: {sql_query}")
        
        # Final validation
        if not sql_query.upper().startswith('SELECT'):
            logger.error(f"Invalid SQL - doesn't start with SELECT: {sql_query}")
            raise Exception(f"Generated invalid SQL query: {sql_query}")
        
        if 'FROM' not in sql_query.upper():
            logger.error(f"Invalid SQL - missing FROM: {sql_query}")
            raise Exception(f"Generated SQL missing FROM clause: {sql_query}")
        
        logger.info(f"Final SQL Query: {sql_query}")
        return sql_query
            
    except Exception as e:
        logger.error(f"Error generating SQL query: {e}")
        raise Exception(f"Error generating SQL query: {e}")

def execute_query(df, sql_query):
    try:
        conn = sqlite3.connect(':memory:')
        df.to_sql('data', conn, index=False, if_exists='replace')
        result = pd.read_sql_query(sql_query, conn)
        conn.close()
        logger.info(f"Query executed successfully: {len(result)} rows returned")
        return result
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        raise Exception(f"Error executing query: {e}")

def interpret_results(query, sql_query, results, client):
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
    
    Keep the response clear and business-friendly. Do not use markdown formatting.
    """
    
    try:
        messages = [{"role": "user", "content": prompt}]
        response = client.chat_completion(
            messages=messages,
            max_tokens=400,
            temperature=0.3
        )
        
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        logger.warning(f"Error generating interpretation: {e}")
        return f"Results retrieved successfully, but couldn't generate interpretation: {e}"

def get_data_profile(df):
    profile = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'numeric_columns': len(df.select_dtypes(include=['number']).columns),
        'text_columns': len(df.select_dtypes(include=['object']).columns),
        'memory_usage_kb': df.memory_usage(deep=True).sum() / 1024,
        'missing_data': df.isnull().sum().to_dict(),
        'column_types': df.dtypes.astype(str).to_dict()
    }
    return profile

def get_quick_stats(file):
    try:
        if file.name.endswith('.csv'):
            temp_df = pd.read_csv(file)
        else:
            temp_df = pd.read_excel(file)
        
        return {
            'rows': len(temp_df),
            'columns': len(temp_df.columns),
            'size_kb': file.size / 1024,
            'file_type': file.name.split('.')[-1].upper()
        }
    except Exception as e:
        logger.error(f"Error getting quick stats: {e}")
        raise Exception(f"Error getting quick stats: {e}")
