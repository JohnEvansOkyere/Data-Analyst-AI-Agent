"""
VexaAI Data Analyst - Feature Engineering Module
Advanced feature engineering capabilities
"""

import pandas as pd
import numpy as np
from typing import List, Optional, Dict
from sklearn.preprocessing import PolynomialFeatures
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)


class FeatureEngineer:
    """Feature engineering operations"""
    
    def __init__(self, df: pd.DataFrame):
        """Initialize FeatureEngineer"""
        self.df = df.copy()
        self.feature_history = []
        logger.info("FeatureEngineer initialized")
    
    # ==================== POLYNOMIAL FEATURES ====================
    
    def create_polynomial_features(
        self,
        columns: List[str],
        degree: int = 2,
        include_bias: bool = False
    ) -> pd.DataFrame:
        """
        Create polynomial features
        
        Args:
            columns: Columns to create polynomial features from
            degree: Polynomial degree
            include_bias: Include bias column
        
        Returns:
            DataFrame with polynomial features
        """
        try:
            poly = PolynomialFeatures(degree=degree, include_bias=include_bias)
            numeric_data = self.df[columns].values
            poly_features = poly.fit_transform(numeric_data)
            
            # Create column names
            feature_names = poly.get_feature_names_out(columns)
            poly_df = pd.DataFrame(
                poly_features,
                columns=feature_names,
                index=self.df.index
            )
            
            # Add to original DataFrame
            self.df = pd.concat([self.df, poly_df], axis=1)
            
            self.feature_history.append({
                "operation": "polynomial_features",
                "columns": columns,
                "degree": degree,
                "features_created": len(feature_names),
                "description": f"Created {len(feature_names)} polynomial features"
            })
            
            logger.info(f"Created {len(feature_names)} polynomial features")
            return self.df
            
        except Exception as e:
            logger.error(f"Error creating polynomial features: {e}")
            raise
    
    # ==================== INTERACTION FEATURES ====================
    
    def create_interaction_features(
        self,
        column_pairs: List[tuple]
    ) -> pd.DataFrame:
        """
        Create interaction features between column pairs
        
        Args:
            column_pairs: List of column pairs to create interactions
        
        Returns:
            DataFrame with interaction features
        """
        try:
            for col1, col2 in column_pairs:
                if col1 in self.df.columns and col2 in self.df.columns:
                    # Multiplication interaction
                    self.df[f"{col1}_x_{col2}"] = self.df[col1] * self.df[col2]
                    
                    # Division interaction (avoid division by zero)
                    self.df[f"{col1}_div_{col2}"] = self.df[col1] / (self.df[col2] + 1e-10)
                    
                    # Addition interaction
                    self.df[f"{col1}_plus_{col2}"] = self.df[col1] + self.df[col2]
                    
                    # Subtraction interaction
                    self.df[f"{col1}_minus_{col2}"] = self.df[col1] - self.df[col2]
            
            self.feature_history.append({
                "operation": "interaction_features",
                "column_pairs": column_pairs,
                "features_created": len(column_pairs) * 4,
                "description": f"Created {len(column_pairs) * 4} interaction features"
            })
            
            logger.info(f"Created interaction features for {len(column_pairs)} column pairs")
            return self.df
            
        except Exception as e:
            logger.error(f"Error creating interaction features: {e}")
            raise
    
    # ==================== MATHEMATICAL TRANSFORMATIONS ====================
    
    def apply_log_transform(
        self,
        columns: List[str],
        base: str = 'natural'
    ) -> pd.DataFrame:
        """
        Apply logarithmic transformation
        
        Args:
            columns: Columns to transform
            base: Log base ('natural', '10', '2')
        
        Returns:
            DataFrame with log-transformed features
        """
        try:
            for col in columns:
                if col in self.df.columns:
                    # Add small constant to avoid log(0)
                    data = self.df[col] + 1
                    
                    if base == 'natural':
                        self.df[f"{col}_log"] = np.log(data)
                    elif base == '10':
                        self.df[f"{col}_log10"] = np.log10(data)
                    elif base == '2':
                        self.df[f"{col}_log2"] = np.log2(data)
            
            self.feature_history.append({
                "operation": "log_transform",
                "columns": columns,
                "base": base,
                "description": f"Applied {base} log transform to {len(columns)} columns"
            })
            
            logger.info(f"Applied log transform to {len(columns)} columns")
            return self.df
            
        except Exception as e:
            logger.error(f"Error applying log transform: {e}")
            raise
    
    def apply_sqrt_transform(
        self,
        columns: List[str]
    ) -> pd.DataFrame:
        """
        Apply square root transformation
        
        Args:
            columns: Columns to transform
        
        Returns:
            DataFrame with sqrt-transformed features
        """
        try:
            for col in columns:
                if col in self.df.columns:
                    self.df[f"{col}_sqrt"] = np.sqrt(np.abs(self.df[col]))
            
            self.feature_history.append({
                "operation": "sqrt_transform",
                "columns": columns,
                "description": f"Applied sqrt transform to {len(columns)} columns"
            })
            
            logger.info(f"Applied sqrt transform to {len(columns)} columns")
            return self.df
            
        except Exception as e:
            logger.error(f"Error applying sqrt transform: {e}")
            raise
    
    def apply_power_transform(
        self,
        columns: List[str],
        power: float = 2
    ) -> pd.DataFrame:
        """
        Apply power transformation
        
        Args:
            columns: Columns to transform
            power: Power to raise values to
        
        Returns:
            DataFrame with power-transformed features
        """
        try:
            for col in columns:
                if col in self.df.columns:
                    self.df[f"{col}_pow{power}"] = np.power(self.df[col], power)
            
            self.feature_history.append({
                "operation": "power_transform",
                "columns": columns,
                "power": power,
                "description": f"Applied power^{power} transform to {len(columns)} columns"
            })
            
            logger.info(f"Applied power transform to {len(columns)} columns")
            return self.df
            
        except Exception as e:
            logger.error(f"Error applying power transform: {e}")
            raise
    
    # ==================== BINNING ====================
    
    def create_bins(
        self,
        column: str,
        n_bins: int = 5,
        strategy: str = 'quantile',
        labels: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Create bins from continuous variable
        
        Args:
            column: Column to bin
            n_bins: Number of bins
            strategy: Binning strategy ('quantile', 'uniform', 'kmeans')
            labels: Custom bin labels
        
        Returns:
            DataFrame with binned feature
        """
        try:
            if column not in self.df.columns:
                raise ValueError(f"Column '{column}' not found")
            
            if strategy == 'quantile':
                self.df[f"{column}_binned"] = pd.qcut(
                    self.df[column],
                    q=n_bins,
                    labels=labels,
                    duplicates='drop'
                )
            elif strategy == 'uniform':
                self.df[f"{column}_binned"] = pd.cut(
                    self.df[column],
                    bins=n_bins,
                    labels=labels
                )
            
            self.feature_history.append({
                "operation": "create_bins",
                "column": column,
                "n_bins": n_bins,
                "strategy": strategy,
                "description": f"Created {n_bins} bins for {column}"
            })
            
            logger.info(f"Created bins for column {column}")
            return self.df
            
        except Exception as e:
            logger.error(f"Error creating bins: {e}")
            raise
    
    # ==================== DATE FEATURES ====================
    
    def extract_date_features(
        self,
        date_columns: List[str]
    ) -> pd.DataFrame:
        """
        Extract features from date columns
        
        Args:
            date_columns: Date columns to extract features from
        
        Returns:
            DataFrame with date features
        """
        try:
            for col in date_columns:
                if col not in self.df.columns:
                    continue
                
                # Convert to datetime if not already
                if not pd.api.types.is_datetime64_any_dtype(self.df[col]):
                    self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                
                # Extract date components
                self.df[f"{col}_year"] = self.df[col].dt.year
                self.df[f"{col}_month"] = self.df[col].dt.month
                self.df[f"{col}_day"] = self.df[col].dt.day
                self.df[f"{col}_dayofweek"] = self.df[col].dt.dayofweek
                self.df[f"{col}_quarter"] = self.df[col].dt.quarter
                self.df[f"{col}_is_weekend"] = self.df[col].dt.dayofweek.isin([5, 6]).astype(int)
                self.df[f"{col}_is_month_start"] = self.df[col].dt.is_month_start.astype(int)
                self.df[f"{col}_is_month_end"] = self.df[col].dt.is_month_end.astype(int)
            
            self.feature_history.append({
                "operation": "extract_date_features",
                "columns": date_columns,
                "features_created": len(date_columns) * 8,
                "description": f"Extracted date features from {len(date_columns)} columns"
            })
            
            logger.info(f"Extracted date features from {len(date_columns)} columns")
            return self.df
            
        except Exception as e:
            logger.error(f"Error extracting date features: {e}")
            raise
    
    # ==================== AGGREGATION FEATURES ====================
    
    def create_aggregation_features(
        self,
        group_by: str,
        target_columns: List[str],
        aggregations: List[str] = ['mean', 'std', 'min', 'max', 'count']
    ) -> pd.DataFrame:
        """
        Create aggregation features by group
        
        Args:
            group_by: Column to group by
            target_columns: Columns to aggregate
            aggregations: Aggregation functions
        
        Returns:
            DataFrame with aggregation features
        """
        try:
            for col in target_columns:
                if col in self.df.columns:
                    for agg in aggregations:
                        agg_values = self.df.groupby(group_by)[col].transform(agg)
                        self.df[f"{col}_{agg}_by_{group_by}"] = agg_values
            
            self.feature_history.append({
                "operation": "aggregation_features",
                "group_by": group_by,
                "target_columns": target_columns,
                "aggregations": aggregations,
                "description": f"Created aggregation features grouped by {group_by}"
            })
            
            logger.info(f"Created aggregation features grouped by {group_by}")
            return self.df
            
        except Exception as e:
            logger.error(f"Error creating aggregation features: {e}")
            raise
    
    # ==================== ROLLING FEATURES ====================
    
    def create_rolling_features(
        self,
        columns: List[str],
        window: int = 7,
        aggregations: List[str] = ['mean', 'std', 'min', 'max']
    ) -> pd.DataFrame:
        """
        Create rolling window features
        
        Args:
            columns: Columns to create rolling features
            window: Window size
            aggregations: Aggregation functions
        
        Returns:
            DataFrame with rolling features
        """
        try:
            for col in columns:
                if col in self.df.columns:
                    for agg in aggregations:
                        rolling_values = self.df[col].rolling(window=window).agg(agg)
                        self.df[f"{col}_rolling{window}_{agg}"] = rolling_values
            
            self.feature_history.append({
                "operation": "rolling_features",
                "columns": columns,
                "window": window,
                "aggregations": aggregations,
                "description": f"Created rolling features with window={window}"
            })
            
            logger.info(f"Created rolling features with window={window}")
            return self.df
            
        except Exception as e:
            logger.error(f"Error creating rolling features: {e}")
            raise
    
    def get_feature_summary(self) -> Dict:
        """Get summary of feature engineering operations"""
        return {
            "total_operations": len(self.feature_history),
            "operations": self.feature_history,
            "original_columns": len(self.df.columns) - sum(
                op.get('features_created', 0) for op in self.feature_history
            ),
            "engineered_columns": sum(
                op.get('features_created', 0) for op in self.feature_history
            ),
            "final_columns": len(self.df.columns)
        }
    
    def get_result(self) -> pd.DataFrame:
        """Get the DataFrame with engineered features"""
        return self.df
