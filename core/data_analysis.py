"""
VexaAI Data Analyst - Data Analysis & Statistics Module
Advanced data analysis and statistical testing
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from scipy import stats
from scipy.stats import chi2_contingency, f_oneway, ttest_ind
import plotly.express as px
import plotly.graph_objects as go
from utils.logger import get_logger

logger = get_logger(__name__)


class DataAnalyzer:
    """Advanced data analysis and statistics"""
    
    def __init__(self, df: pd.DataFrame):
        """Initialize DataAnalyzer"""
        self.df = df.copy()
        logger.info("DataAnalyzer initialized")
    
    def generate_summary_statistics(self) -> Dict:
        """Generate comprehensive summary statistics"""
        try:
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns
            
            summary = {
                "basic_stats": self.df[numeric_cols].describe().to_dict() if len(numeric_cols) > 0 else {},
                "missing_values": self.df.isnull().sum().to_dict(),
                "data_types": self.df.dtypes.astype(str).to_dict(),
                "unique_counts": self.df.nunique().to_dict(),
                "memory_usage": self.df.memory_usage(deep=True).to_dict()
            }
            
            # Categorical summaries
            if len(categorical_cols) > 0:
                summary["categorical_stats"] = {}
                for col in categorical_cols:
                    summary["categorical_stats"][col] = {
                        "unique_values": self.df[col].nunique(),
                        "top_values": self.df[col].value_counts().head(5).to_dict(),
                        "missing": self.df[col].isnull().sum()
                    }
            
            logger.info("Generated summary statistics")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary statistics: {e}")
            raise
    
    def calculate_correlations(
        self,
        method: str = 'pearson',
        min_threshold: float = 0.0
    ) -> pd.DataFrame:
        """Calculate correlation matrix"""
        try:
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) < 2:
                return pd.DataFrame()
            
            corr_matrix = self.df[numeric_cols].corr(method=method)
            
            # Filter by threshold
            if min_threshold > 0:
                mask = np.abs(corr_matrix) >= min_threshold
                corr_matrix = corr_matrix.where(mask)
            
            logger.info(f"Calculated {method} correlations")
            return corr_matrix
            
        except Exception as e:
            logger.error(f"Error calculating correlations: {e}")
            raise
    
    def perform_t_test(
        self,
        column: str,
        group_column: str
    ) -> Dict:
        """Perform independent t-test"""
        try:
            groups = self.df[group_column].unique()
            if len(groups) != 2:
                raise ValueError("T-test requires exactly 2 groups")
            
            group1 = self.df[self.df[group_column] == groups[0]][column].dropna()
            group2 = self.df[self.df[group_column] == groups[1]][column].dropna()
            
            statistic, p_value = ttest_ind(group1, group2)
            
            result = {
                "test": "Independent T-Test",
                "column": column,
                "group_column": group_column,
                "groups": list(groups),
                "statistic": float(statistic),
                "p_value": float(p_value),
                "significant": p_value < 0.05,
                "interpretation": "Significant difference" if p_value < 0.05 else "No significant difference"
            }
            
            logger.info(f"Performed t-test on {column} by {group_column}")
            return result
            
        except Exception as e:
            logger.error(f"Error performing t-test: {e}")
            raise
    
    def perform_anova(
        self,
        column: str,
        group_column: str
    ) -> Dict:
        """Perform one-way ANOVA"""
        try:
            groups = [group[column].dropna() for name, group in self.df.groupby(group_column)]
            
            statistic, p_value = f_oneway(*groups)
            
            result = {
                "test": "One-Way ANOVA",
                "column": column,
                "group_column": group_column,
                "n_groups": len(groups),
                "statistic": float(statistic),
                "p_value": float(p_value),
                "significant": p_value < 0.05,
                "interpretation": "Significant difference between groups" if p_value < 0.05 else "No significant difference"
            }
            
            logger.info(f"Performed ANOVA on {column} by {group_column}")
            return result
            
        except Exception as e:
            logger.error(f"Error performing ANOVA: {e}")
            raise
    
    def perform_chi_square(
        self,
        column1: str,
        column2: str
    ) -> Dict:
        """Perform chi-square test of independence"""
        try:
            contingency_table = pd.crosstab(self.df[column1], self.df[column2])
            chi2, p_value, dof, expected = chi2_contingency(contingency_table)
            
            result = {
                "test": "Chi-Square Test",
                "column1": column1,
                "column2": column2,
                "chi2_statistic": float(chi2),
                "p_value": float(p_value),
                "degrees_of_freedom": int(dof),
                "significant": p_value < 0.05,
                "interpretation": "Variables are dependent" if p_value < 0.05 else "Variables are independent"
            }
            
            logger.info(f"Performed chi-square test between {column1} and {column2}")
            return result
            
        except Exception as e:
            logger.error(f"Error performing chi-square test: {e}")
            raise
    
    def test_normality(
        self,
        columns: List[str]
    ) -> Dict:
        """Test normality using Shapiro-Wilk test"""
        try:
            results = {}
            for col in columns:
                if col in self.df.columns:
                    data = self.df[col].dropna()
                    if len(data) >= 3 and len(data) <= 5000:  # Shapiro-Wilk limitations
                        statistic, p_value = stats.shapiro(data)
                        results[col] = {
                            "statistic": float(statistic),
                            "p_value": float(p_value),
                            "is_normal": p_value > 0.05
                        }
            
            logger.info(f"Performed normality tests on {len(results)} columns")
            return results
            
        except Exception as e:
            logger.error(f"Error testing normality: {e}")
            raise
    
    def detect_multicollinearity(
        self,
        threshold: float = 10.0
    ) -> Dict:
        """Detect multicollinearity using VIF"""
        try:
            from statsmodels.stats.outliers_influence import variance_inflation_factor
            
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
            if len(numeric_cols) < 2:
                return {}
            
            # Calculate VIF
            vif_data = pd.DataFrame()
            vif_data["Feature"] = numeric_cols
            vif_data["VIF"] = [
                variance_inflation_factor(self.df[numeric_cols].values, i)
                for i in range(len(numeric_cols))
            ]
            
            # Identify problematic features
            high_vif = vif_data[vif_data["VIF"] > threshold]
            
            result = {
                "vif_scores": vif_data.to_dict('records'),
                "high_vif_features": high_vif["Feature"].tolist(),
                "threshold": threshold,
                "has_multicollinearity": len(high_vif) > 0
            }
            
            logger.info("Detected multicollinearity")
            return result
            
        except Exception as e:
            logger.error(f"Error detecting multicollinearity: {e}")
            return {"error": str(e)}
