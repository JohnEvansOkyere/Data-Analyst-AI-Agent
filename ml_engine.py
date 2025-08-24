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

# Groq API client class
class GroqClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.groq.com/openai/v1"
        
    def chat_completion(self, messages, model="llama-3.3-70b-versatile", max_tokens=500, temperature=0.1):
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
            
            # Debug information
            if response.status_code != 200:
                print(f"API Response Status: {response.status_code}")
                print(f"API Response: {response.text}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Groq API error: {str(e)}")

# Function to preprocess and save the uploaded file
def preprocess_and_save(file):
    try:
        # Read the uploaded file into a DataFrame
        if file.name.endswith('.csv'):
            # Reset file pointer in case it was read earlier
            file.seek(0)
            df = pd.read_csv(file, encoding='utf-8', na_values=['NA', 'N/A', 'missing'])
        elif file.name.endswith('.xlsx'):
            file.seek(0)
            df = pd.read_excel(file, na_values=['NA', 'N/A', 'missing'])
        else:
            raise ValueError("Unsupported file format. Please upload a CSV or Excel file.")
        
        # Check if DataFrame has columns
        if df.empty or len(df.columns) == 0:
            raise ValueError("Uploaded file has no data or no valid columns. Please check the file.")

        # Clean column names
        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
            .str.replace(' ', '_')
            .str.replace('[^A-Za-z0-9_]', '', regex=True)
        )
        
        # Parse dates and numeric columns
        for col in df.columns:
            if 'date' in col.lower():
                df[col] = pd.to_datetime(df[col], errors='coerce')
            elif df[col].dtype == 'object':
                try:
                    df[col] = pd.to_numeric(df[col], errors='ignore')
                except Exception:
                    pass
        
        return df

    except Exception as e:
        raise Exception(f"Error processing file: {e}")

def generate_sql_query(user_query, columns, table_name="data", client=None):
    """Generate SQL query using Groq"""
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
    7. Do not include markdown formatting or code blocks
    
    SQL Query:
    """
    
    try:
        messages = [{"role": "user", "content": prompt}]
        response = client.chat_completion(
            messages=messages,
            max_tokens=300,
            temperature=0.1
        )
        
        sql_query = response['choices'][0]['message']['content'].strip()
        
        # Clean the SQL query
        sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
        
        # Extract SQL if it's wrapped in text
        lines = sql_query.split('\n')
        for line in lines:
            line = line.strip()
            if line.upper().startswith('SELECT'):
                return line
        
        if sql_query.startswith('SELECT') or sql_query.startswith('select'):
            return sql_query
        else:
            return sql_query
            
    except Exception as e:
        raise Exception(f"Error generating SQL query: {e}")

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
        raise Exception(f"Error executing query: {e}")

def interpret_results(query, sql_query, results, client):
    """Generate interpretation of results using Groq"""
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
        return f"Results retrieved successfully, but couldn't generate interpretation: {e}"

def get_data_profile(df):
    """Get basic data profiling information"""
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
    """Get quick statistics from uploaded file"""
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
        raise Exception(f"Error getting quick stats: {e}")
