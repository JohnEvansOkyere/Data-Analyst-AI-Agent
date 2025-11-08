"""
VexaAI Data Analyst - Data Cleaning & Preprocessing Module
Comprehensive data cleaning and preprocessing techniques
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from sklearn.preprocessing import (
    StandardScaler, MinMaxScaler, RobustScaler, 
    MaxAbsScaler, Normalizer, LabelEncoder, OneHotEncoder
)
from sklearn.ensemble import IsolationForest
from scipy import stats
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)


class DataCleaner:
    """Comprehensive data cleaning and preprocessing"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize DataCleaner
        
        Args:
            df: Input DataFrame
        """
        self.df = df.copy()
        self.original_df = df.copy()
        self.cleaning_history = []
        logger.info(f"DataCleaner initialized with {len(df)} rows, {len(df.columns)} columns")
    
    def get_cleaning_summary(self) -> Dict:
        """Get summary of cleaning operations performed"""
        return {
            "original_shape": self.original_df.shape,
            "current_shape": self.df.shape,
            "rows_removed": len(self.original_df) - len(self.df),
            "columns_removed": len(self.original_df.columns) - len(self.df.columns),
            "operations": self.cleaning_history
        }
    
    # ==================== MISSING DATA HANDLING ====================
    
    def handle_missing_data(
        self,
        strategy: str = "drop_rows",
        columns: Optional[List[str]] = None,
        fill_value: Any = None,
        threshold: float = 0.5
    ) -> pd.DataFrame:
        """
        Handle missing data with various strategies
        
        Args:
            strategy: Strategy to handle missing data
            columns: Specific columns to apply strategy (None for all)
            fill_value: Value to fill if strategy is 'fill_constant'
            threshold: Threshold for dropping columns (percentage of missing)
        
        Returns:
            Cleaned DataFrame
        """
        try:
            cols = columns if columns else self.df.columns.tolist()
            rows_before = len(self.df)
            
            if strategy == "drop_rows":
                self.df = self.df.dropna(subset=cols)
                operation = f"Dropped rows with missing values in {len(cols)} columns"
            
            elif strategy == "drop_columns":
                missing_pct = self.df[cols].isnull().sum() / len(self.df)
                cols_to_drop = missing_pct[missing_pct > threshold].index.tolist()
                self.df = self.df.drop(columns=cols_to_drop)
                operation = f"Dropped {len(cols_to_drop)} columns with >{threshold*100}% missing"
            
            elif strategy == "fill_mean":
                numeric_cols = self.df[cols].select_dtypes(include=[np.number]).columns
                self.df[numeric_cols] = self.df[numeric_cols].fillna(self.df[numeric_cols].mean())
                operation = f"Filled missing values with mean in {len(numeric_cols)} columns"
            
            elif strategy == "fill_median":
                numeric_cols = self.df[cols].select_dtypes(include=[np.number]).columns
                self.df[numeric_cols] = self.df[numeric_cols].fillna(self.df[numeric_cols].median())
                operation = f"Filled missing values with median in {len(numeric_cols)} columns"
            
            elif strategy == "fill_mode":
                for col in cols:
                    if col in self.df.columns:
                        mode_value = self.df[col].mode()[0] if len(self.df[col].mode()) > 0 else None
                        if mode_value is not None:
                            self.df[col] = self.df[col].fillna(mode_value)
                operation = f"Filled missing values with mode in {len(cols)} columns"
            
            elif strategy == "fill_constant":
                self.df[cols] = self.df[cols].fillna(fill_value)
                operation = f"Filled missing values with constant '{fill_value}' in {len(cols)} columns"
            
            elif strategy == "forward_fill":
                self.df[cols] = self.df[cols].fillna(method='ffill')
                operation = f"Forward filled missing values in {len(cols)} columns"
            
            elif strategy == "backward_fill":
                self.df[cols] = self.df[cols].fillna(method='bfill')
                operation = f"Backward filled missing values in {len(cols)} columns"
            
            elif strategy == "interpolate":
                numeric_cols = self.df[cols].select_dtypes(include=[np.number]).columns
                self.df[numeric_cols] = self.df[numeric_cols].interpolate(method='linear')
                operation = f"Interpolated missing values in {len(numeric_cols)} columns"
            
            rows_after = len(self.df)
            self.cleaning_history.append({
                "operation": "handle_missing_data",
                "strategy": strategy,
                "rows_before": rows_before,
                "rows_after": rows_after,
                "description": operation
            })
            
            logger.info(f"Missing data handled: {operation}")
            return self.df
            
        except Exception as e:
            logger.error(f"Error handling missing data: {e}")
            raise
    
    # ==================== DUPLICATE HANDLING ====================
    
    def remove_duplicates(
        self,
        subset: Optional[List[str]] = None,
        keep: str = "first"
    ) -> pd.DataFrame:
        """
        Remove duplicate rows
        
        Args:
            subset: Columns to consider for identifying duplicates
            keep: Which duplicates to keep ('first', 'last', False)
        
        Returns:
            DataFrame without duplicates
        """
        try:
            rows_before = len(self.df)
            self.df = self.df.drop_duplicates(subset=subset, keep=keep)
            rows_after = len(self.df)
            duplicates_removed = rows_before - rows_after
            
            self.cleaning_history.append({
                "operation": "remove_duplicates",
                "rows_before": rows_before,
                "rows_after": rows_after,
                "duplicates_removed": duplicates_removed,
                "description": f"Removed {duplicates_removed} duplicate rows"
            })
            
            logger.info(f"Removed {duplicates_removed} duplicate rows")
            return self.df
            
        except Exception as e:
            logger.error(f"Error removing duplicates: {e}")
            raise
    
    # ==================== OUTLIER DETECTION & REMOVAL ====================
    
    def detect_outliers_iqr(
        self,
        column: str,
        multiplier: float = 1.5
    ) -> pd.Series:
        """Detect outliers using IQR method"""
        Q1 = self.df[column].quantile(0.25)
        Q3 = self.df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR
        return (self.df[column] < lower_bound) | (self.df[column] > upper_bound)
    
    def detect_outliers_zscore(
        self,
        column: str,
        threshold: float = 3.0
    ) -> pd.Series:
        """Detect outliers using Z-score method"""
        z_scores = np.abs(stats.zscore(self.df[column].dropna()))
        outliers = pd.Series(False, index=self.df.index)
        outliers.loc[self.df[column].dropna().index] = z_scores > threshold
        return outliers
    
    def detect_outliers_isolation_forest(
        self,
        columns: List[str],
        contamination: float = 0.1
    ) -> pd.Series:
        """Detect outliers using Isolation Forest"""
        clf = IsolationForest(contamination=contamination, random_state=42)
        data = self.df[columns].dropna()
        predictions = clf.fit_predict(data)
        outliers = pd.Series(False, index=self.df.index)
        outliers.loc[data.index] = predictions == -1
        return outliers
    
    def remove_outliers(
        self,
        method: str = "iqr",
        columns: Optional[List[str]] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        Remove outliers from specified columns
        
        Args:
            method: Method to detect outliers ('iqr', 'z_score', 'isolation_forest')
            columns: Columns to check for outliers
            **kwargs: Additional parameters for outlier detection
        
        Returns:
            DataFrame without outliers
        """
        try:
            if columns is None:
                columns = self.df.select_dtypes(include=[np.number]).columns.tolist()
            
            rows_before = len(self.df)
            outlier_mask = pd.Series(False, index=self.df.index)
            
            if method == "iqr":
                for col in columns:
                    if col in self.df.columns:
                        outlier_mask |= self.detect_outliers_iqr(col, kwargs.get('multiplier', 1.5))
            
            elif method == "z_score":
                for col in columns:
                    if col in self.df.columns:
                        outlier_mask |= self.detect_outliers_zscore(col, kwargs.get('threshold', 3.0))
            
            elif method == "isolation_forest":
                outlier_mask = self.detect_outliers_isolation_forest(
                    columns,
                    kwargs.get('contamination', 0.1)
                )
            
            self.df = self.df[~outlier_mask]
            rows_after = len(self.df)
            outliers_removed = rows_before - rows_after
            
            self.cleaning_history.append({
                "operation": "remove_outliers",
                "method": method,
                "columns": columns,
                "rows_before": rows_before,
                "rows_after": rows_after,
                "outliers_removed": outliers_removed,
                "description": f"Removed {outliers_removed} outliers using {method} method"
            })
            
            logger.info(f"Removed {outliers_removed} outliers using {method} method")
            return self.df
            
        except Exception as e:
            logger.error(f"Error removing outliers: {e}")
            raise
    
    # ==================== DATA TYPE CONVERSION ====================
    
    def convert_data_types(
        self,
        conversions: Dict[str, str]
    ) -> pd.DataFrame:
        """
        Convert column data types
        
        Args:
            conversions: Dictionary mapping column names to target data types
        
        Returns:
            DataFrame with converted types
        """
        try:
            for column, dtype in conversions.items():
                if column in self.df.columns:
                    if dtype == 'datetime':
                        self.df[column] = pd.to_datetime(self.df[column], errors='coerce')
                    elif dtype == 'category':
                        self.df[column] = self.df[column].astype('category')
                    else:
                        self.df[column] = self.df[column].astype(dtype)
            
            self.cleaning_history.append({
                "operation": "convert_data_types",
                "conversions": conversions,
                "description": f"Converted data types for {len(conversions)} columns"
            })
            
            logger.info(f"Converted data types for {len(conversions)} columns")
            return self.df
            
        except Exception as e:
            logger.error(f"Error converting data types: {e}")
            raise
    
    # ==================== COLUMN OPERATIONS ====================
    
    def rename_columns(
        self,
        rename_map: Dict[str, str]
    ) -> pd.DataFrame:
        """Rename columns"""
        try:
            self.df = self.df.rename(columns=rename_map)
            self.cleaning_history.append({
                "operation": "rename_columns",
                "renames": rename_map,
                "description": f"Renamed {len(rename_map)} columns"
            })
            logger.info(f"Renamed {len(rename_map)} columns")
            return self.df
        except Exception as e:
            logger.error(f"Error renaming columns: {e}")
            raise
    
    def drop_columns(
        self,
        columns: List[str]
    ) -> pd.DataFrame:
        """Drop specified columns"""
        try:
            existing_cols = [col for col in columns if col in self.df.columns]
            self.df = self.df.drop(columns=existing_cols)
            self.cleaning_history.append({
                "operation": "drop_columns",
                "columns": existing_cols,
                "description": f"Dropped {len(existing_cols)} columns"
            })
            logger.info(f"Dropped {len(existing_cols)} columns")
            return self.df
        except Exception as e:
            logger.error(f"Error dropping columns: {e}")
            raise
    
    def reorder_columns(
        self,
        column_order: List[str]
    ) -> pd.DataFrame:
        """Reorder columns"""
        try:
            # Include columns not in the specified order at the end
            remaining_cols = [col for col in self.df.columns if col not in column_order]
            new_order = column_order + remaining_cols
            self.df = self.df[new_order]
            self.cleaning_history.append({
                "operation": "reorder_columns",
                "description": "Reordered columns"
            })
            logger.info("Reordered columns")
            return self.df
        except Exception as e:
            logger.error(f"Error reordering columns: {e}")
            raise
    
    # ==================== TEXT CLEANING ====================
    
    def clean_text_columns(
        self,
        columns: Optional[List[str]] = None,
        lowercase: bool = True,
        remove_whitespace: bool = True,
        remove_special_chars: bool = False
    ) -> pd.DataFrame:
        """
        Clean text data in specified columns
        
        Args:
            columns: Columns to clean (None for all object columns)
            lowercase: Convert to lowercase
            remove_whitespace: Remove extra whitespace
            remove_special_chars: Remove special characters
        
        Returns:
            DataFrame with cleaned text
        """
        try:
            if columns is None:
                columns = self.df.select_dtypes(include=['object']).columns.tolist()
            
            for col in columns:
                if col in self.df.columns:
                    if lowercase:
                        self.df[col] = self.df[col].str.lower()
                    if remove_whitespace:
                        self.df[col] = self.df[col].str.strip()
                        self.df[col] = self.df[col].str.replace(r'\s+', ' ', regex=True)
                    if remove_special_chars:
                        self.df[col] = self.df[col].str.replace(r'[^a-zA-Z0-9\s]', '', regex=True)
            
            self.cleaning_history.append({
                "operation": "clean_text_columns",
                "columns": columns,
                "description": f"Cleaned text in {len(columns)} columns"
            })
            
            logger.info(f"Cleaned text in {len(columns)} columns")
            return self.df
            
        except Exception as e:
            logger.error(f"Error cleaning text columns: {e}")
            raise
    
    def get_result(self) -> pd.DataFrame:
        """Get the cleaned DataFrame"""
        return self.df


class DataScaler:
    """Data scaling and normalization"""
    
    def __init__(self, df: pd.DataFrame):
        """Initialize DataScaler"""
        self.df = df.copy()
        self.scalers = {}
        logger.info("DataScaler initialized")
    
    def scale_columns(
        self,
        columns: List[str],
        method: str = "standard_scaler"
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        Scale specified columns
        
        Args:
            columns: Columns to scale
            method: Scaling method
        
        Returns:
            Tuple of (scaled DataFrame, scaler objects)
        """
        try:
            for col in columns:
                if col not in self.df.columns:
                    continue
                
                data = self.df[[col]].values
                
                if method == "standard_scaler":
                    scaler = StandardScaler()
                elif method == "min_max_scaler":
                    scaler = MinMaxScaler()
                elif method == "robust_scaler":
                    scaler = RobustScaler()
                elif method == "max_abs_scaler":
                    scaler = MaxAbsScaler()
                elif method == "normalizer":
                    scaler = Normalizer()
                else:
                    raise ValueError(f"Unknown scaling method: {method}")
                
                scaled_data = scaler.fit_transform(data)
                self.df[col] = scaled_data
                self.scalers[col] = scaler
            
            logger.info(f"Scaled {len(columns)} columns using {method}")
            return self.df, self.scalers
            
        except Exception as e:
            logger.error(f"Error scaling columns: {e}")
            raise
    
    def get_result(self) -> pd.DataFrame:
        """Get the scaled DataFrame"""
        return self.df


class DataEncoder:
    """Data encoding for categorical variables"""
    
    def __init__(self, df: pd.DataFrame):
        """Initialize DataEncoder"""
        self.df = df.copy()
        self.encoders = {}
        logger.info("DataEncoder initialized")
    
    def encode_columns(
        self,
        columns: List[str],
        method: str = "label_encoding"
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        Encode categorical columns
        
        Args:
            columns: Columns to encode
            method: Encoding method
        
        Returns:
            Tuple of (encoded DataFrame, encoder objects)
        """
        try:
            for col in columns:
                if col not in self.df.columns:
                    continue
                
                if method == "label_encoding":
                    encoder = LabelEncoder()
                    self.df[col] = encoder.fit_transform(self.df[col].astype(str))
                    self.encoders[col] = encoder
                
                elif method == "one_hot_encoding":
                    dummies = pd.get_dummies(self.df[col], prefix=col, drop_first=True)
                    self.df = pd.concat([self.df.drop(columns=[col]), dummies], axis=1)
                    self.encoders[col] = list(dummies.columns)
                
                elif method == "frequency_encoding":
                    freq = self.df[col].value_counts(normalize=True).to_dict()
                    self.df[f"{col}_freq"] = self.df[col].map(freq)
                    self.encoders[col] = freq
            
            logger.info(f"Encoded {len(columns)} columns using {method}")
            return self.df, self.encoders
            
        except Exception as e:
            logger.error(f"Error encoding columns: {e}")
            raise
    
    def get_result(self) -> pd.DataFrame:
        """Get the encoded DataFrame"""
        return self.df
