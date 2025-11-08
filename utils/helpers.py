"""
VexaAI Data Analyst - Helper Utilities
Common helper functions
"""

import pandas as pd
import numpy as np
from typing import Any, Dict, List
import io
from datetime import datetime


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def format_number(number: float, decimals: int = 2) -> str:
    """Format number with thousands separator"""
    if pd.isna(number):
        return "N/A"
    return f"{number:,.{decimals}f}"


def get_column_info(df: pd.DataFrame) -> pd.DataFrame:
    """Get comprehensive column information"""
    info = pd.DataFrame({
        'Column': df.columns,
        'Type': df.dtypes.astype(str),
        'Non-Null': df.count(),
        'Null Count': df.isnull().sum(),
        'Null %': (df.isnull().sum() / len(df) * 100).round(2),
        'Unique': df.nunique(),
        'Unique %': (df.nunique() / len(df) * 100).round(2)
    })
    return info


def calculate_data_quality_score(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate overall data quality score"""
    total_cells = df.shape[0] * df.shape[1]
    missing_cells = df.isnull().sum().sum()
    duplicate_rows = df.duplicated().sum()
    
    # Calculate metrics
    completeness = (1 - missing_cells / total_cells) * 100
    uniqueness = (1 - duplicate_rows / len(df)) * 100 if len(df) > 0 else 100
    
    # Overall score (weighted average)
    quality_score = (completeness * 0.6 + uniqueness * 0.4)
    
    return {
        "quality_score": round(quality_score, 2),
        "completeness": round(completeness, 2),
        "uniqueness": round(uniqueness, 2),
        "missing_cells": missing_cells,
        "duplicate_rows": duplicate_rows,
        "total_cells": total_cells
    }


def export_dataframe(
    df: pd.DataFrame,
    format: str = "csv",
    filename: str = None,
    compression: str = None
) -> bytes:
    """Export DataFrame to various formats"""
    if filename is None:
        filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    buffer = io.BytesIO()
    
    if format == "csv":
        df.to_csv(buffer, index=False, compression=compression)
    elif format == "excel":
        df.to_excel(buffer, index=False, engine='openpyxl')
    elif format == "parquet":
        df.to_parquet(buffer, index=False, compression=compression)
    elif format == "json":
        df.to_json(buffer, orient='records', indent=2)
    elif format == "feather":
        df.to_feather(buffer)
    
    buffer.seek(0)
    return buffer.getvalue()


def detect_date_columns(df: pd.DataFrame) -> List[str]:
    """Detect potential date columns"""
    date_cols = []
    for col in df.columns:
        if 'date' in col.lower() or 'time' in col.lower():
            date_cols.append(col)
        elif df[col].dtype == 'object':
            try:
                pd.to_datetime(df[col].dropna().head(100), errors='raise')
                date_cols.append(col)
            except:
                pass
    return date_cols


def suggest_column_types(df: pd.DataFrame) -> Dict[str, str]:
    """Suggest appropriate data types for columns"""
    suggestions = {}
    for col in df.columns:
        current_type = str(df[col].dtype)
        
        if current_type == 'object':
            # Check if it's numeric
            try:
                pd.to_numeric(df[col], errors='raise')
                suggestions[col] = 'numeric'
                continue
            except:
                pass
            
            # Check if it's date
            try:
                pd.to_datetime(df[col].dropna().head(100), errors='raise')
                suggestions[col] = 'datetime'
                continue
            except:
                pass
            
            # Check if it should be category
            unique_ratio = df[col].nunique() / len(df)
            if unique_ratio < 0.05:
                suggestions[col] = 'category'
                continue
            
            suggestions[col] = 'text'
        else:
            suggestions[col] = current_type
    
    return suggestions
