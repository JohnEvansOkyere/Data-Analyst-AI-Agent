"""
VexaAI Data Analyst - Data Analysis & Statistics Module
Advanced data analysis and statistical testing
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from scipy import stats
from scipy.stats import chi2_contingency, f_oneway, ttest_ind
import plotly.express as px
import plotly.graph_objects as go
from utils.logger import get_logger

logger = get_logger(__name__)


class DataAnalyzer:
    """Advanced data analysis and statistics"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize DataAnalyzer
        
        Args:
            df: pandas DataFrame to analyze
        """
        self.df = df.copy()
        self.numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns.tolist()
        logger.info(f"DataAnalyzer initialized: {len(self.df)} rows, {len(self.df.columns)} columns")
    
    def generate_summary_statistics(self) -> Dict:
        """
        Generate comprehensive summary statistics
        
        Returns:
            Dict containing basic stats, missing values, data types, etc.
        """
        try:
            summary = {
                "basic_stats": {},
                "missing_values": self.df.isnull().sum().to_dict(),
                "data_types": self.df.dtypes.astype(str).to_dict(),
                "unique_counts": self.df.nunique().to_dict(),
                "memory_usage": self.df.memory_usage(deep=True).sum() / 1024  # KB
            }
            
            # Numeric statistics
            if len(self.numeric_cols) > 0:
                summary["basic_stats"] = self.df[self.numeric_cols].describe().to_dict()
            
            # Categorical summaries
            if len(self.categorical_cols) > 0:
                summary["categorical_stats"] = {}
                for col in self.categorical_cols:
                    try:
                        value_counts = self.df[col].value_counts().head(10)
                        summary["categorical_stats"][col] = {
                            "unique_values": int(self.df[col].nunique()),
                            "top_values": value_counts.to_dict(),
                            "missing": int(self.df[col].isnull().sum()),
                            "missing_pct": float(self.df[col].isnull().sum() / len(self.df) * 100)
                        }
                    except Exception as e:
                        logger.warning(f"Error processing categorical column {col}: {e}")
                        continue
            
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
        """
        Calculate correlation matrix
        
        Args:
            method: Correlation method ('pearson', 'spearman', 'kendall')
            min_threshold: Minimum absolute correlation to show
        
        Returns:
            Correlation matrix DataFrame
        """
        try:
            if len(self.numeric_cols) < 2:
                logger.warning("Need at least 2 numeric columns for correlation")
                return pd.DataFrame()
            
            # Calculate correlation
            corr_matrix = self.df[self.numeric_cols].corr(method=method)
            
            # Filter by threshold
            if min_threshold > 0:
                # Keep only correlations above threshold
                mask = np.abs(corr_matrix) >= min_threshold
                corr_matrix = corr_matrix.where(mask)
            
            logger.info(f"Calculated {method} correlations with threshold {min_threshold}")
            return corr_matrix
            
        except Exception as e:
            logger.error(f"Error calculating correlations: {e}")
            raise
    
    def perform_t_test(
        self,
        column: str,
        group_column: str,
        alternative: str = 'two-sided'
    ) -> Dict:
        """
        Perform independent t-test
        
        Args:
            column: Numeric column to test
            group_column: Categorical column with 2 groups
            alternative: Type of test ('two-sided', 'less', 'greater')
        
        Returns:
            Dict with test results
        """
        try:
            # Validate inputs
            if column not in self.numeric_cols:
                raise ValueError(f"{column} is not a numeric column")
            
            if group_column not in self.df.columns:
                raise ValueError(f"{group_column} not found in dataframe")
            
            groups = self.df[group_column].unique()
            groups = [g for g in groups if pd.notna(g)]  # Remove NaN groups
            
            if len(groups) != 2:
                raise ValueError(f"T-test requires exactly 2 groups, found {len(groups)}")
            
            # Extract data for each group
            group1_data = self.df[self.df[group_column] == groups[0]][column].dropna()
            group2_data = self.df[self.df[group_column] == groups[1]][column].dropna()
            
            if len(group1_data) < 2 or len(group2_data) < 2:
                raise ValueError("Each group needs at least 2 observations")
            
            # Perform t-test
            statistic, p_value = ttest_ind(group1_data, group2_data, alternative=alternative)
            
            # Calculate effect size (Cohen's d)
            mean_diff = group1_data.mean() - group2_data.mean()
            pooled_std = np.sqrt(((len(group1_data)-1)*group1_data.std()**2 + 
                                 (len(group2_data)-1)*group2_data.std()**2) / 
                                (len(group1_data) + len(group2_data) - 2))
            cohens_d = mean_diff / pooled_std if pooled_std > 0 else 0
            
            result = {
                "test": "Independent T-Test",
                "column": column,
                "group_column": group_column,
                "groups": {
                    str(groups[0]): {
                        "n": int(len(group1_data)),
                        "mean": float(group1_data.mean()),
                        "std": float(group1_data.std())
                    },
                    str(groups[1]): {
                        "n": int(len(group2_data)),
                        "mean": float(group2_data.mean()),
                        "std": float(group2_data.std())
                    }
                },
                "statistic": float(statistic),
                "p_value": float(p_value),
                "cohens_d": float(cohens_d),
                "significant": p_value < 0.05,
                "interpretation": self._interpret_t_test(p_value, cohens_d, alternative)
            }
            
            logger.info(f"Performed t-test on {column} by {group_column}")
            return result
            
        except Exception as e:
            logger.error(f"Error performing t-test: {e}")
            raise
    
    def _interpret_t_test(self, p_value: float, cohens_d: float, alternative: str) -> str:
        """Generate interpretation for t-test results"""
        if p_value >= 0.05:
            return "No significant difference between groups (p ≥ 0.05)"
        
        effect_size = "small" if abs(cohens_d) < 0.5 else "medium" if abs(cohens_d) < 0.8 else "large"
        direction = "higher" if cohens_d > 0 else "lower"
        
        return f"Significant difference found (p < 0.05) with {effect_size} effect size (d = {cohens_d:.3f})"
    
    def perform_anova(
        self,
        column: str,
        group_column: str
    ) -> Dict:
        """
        Perform one-way ANOVA
        
        Args:
            column: Numeric column to test
            group_column: Categorical column with groups
        
        Returns:
            Dict with ANOVA results
        """
        try:
            # Validate inputs
            if column not in self.numeric_cols:
                raise ValueError(f"{column} is not a numeric column")
            
            # Group data
            groups = []
            group_names = []
            for name, group in self.df.groupby(group_column):
                if pd.notna(name):
                    data = group[column].dropna()
                    if len(data) > 0:
                        groups.append(data)
                        group_names.append(name)
            
            if len(groups) < 2:
                raise ValueError("ANOVA requires at least 2 groups")
            
            # Perform ANOVA
            statistic, p_value = f_oneway(*groups)
            
            # Calculate group statistics
            group_stats = {}
            for name, data in zip(group_names, groups):
                group_stats[str(name)] = {
                    "n": int(len(data)),
                    "mean": float(data.mean()),
                    "std": float(data.std())
                }
            
            result = {
                "test": "One-Way ANOVA",
                "column": column,
                "group_column": group_column,
                "n_groups": len(groups),
                "group_stats": group_stats,
                "f_statistic": float(statistic),
                "p_value": float(p_value),
                "significant": p_value < 0.05,
                "interpretation": "Significant difference between groups" if p_value < 0.05 
                                else "No significant difference between groups"
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
        """
        Perform chi-square test of independence
        
        Args:
            column1: First categorical column
            column2: Second categorical column
        
        Returns:
            Dict with chi-square test results
        """
        try:
            # Create contingency table
            contingency_table = pd.crosstab(self.df[column1], self.df[column2])
            
            # Perform chi-square test
            chi2, p_value, dof, expected = chi2_contingency(contingency_table)
            
            result = {
                "test": "Chi-Square Test of Independence",
                "column1": column1,
                "column2": column2,
                "chi2_statistic": float(chi2),
                "p_value": float(p_value),
                "degrees_of_freedom": int(dof),
                "contingency_table": contingency_table.to_dict(),
                "significant": p_value < 0.05,
                "interpretation": f"Variables are {'dependent' if p_value < 0.05 else 'independent'} (p = {p_value:.4f})"
            }
            
            logger.info(f"Performed chi-square test between {column1} and {column2}")
            return result
            
        except Exception as e:
            logger.error(f"Error performing chi-square test: {e}")
            raise
    
    def test_normality(
        self,
        columns: Optional[List[str]] = None
    ) -> Dict:
        """
        Test normality using Shapiro-Wilk test
        
        Args:
            columns: List of columns to test (if None, tests all numeric columns)
        
        Returns:
            Dict with normality test results for each column
        """
        try:
            if columns is None:
                columns = self.numeric_cols
            
            results = {}
            for col in columns:
                if col not in self.df.columns:
                    logger.warning(f"Column {col} not found")
                    continue
                
                data = self.df[col].dropna()
                
                # Check sample size constraints
                if len(data) < 3:
                    results[col] = {
                        "error": "Sample size too small (n < 3)"
                    }
                elif len(data) > 5000:
                    # Use alternative test for large samples
                    results[col] = {
                        "warning": "Sample size > 5000, using Kolmogorov-Smirnov test",
                        "test": "Kolmogorov-Smirnov"
                    }
                    statistic, p_value = stats.kstest(data, 'norm', args=(data.mean(), data.std()))
                    results[col].update({
                        "statistic": float(statistic),
                        "p_value": float(p_value),
                        "is_normal": p_value > 0.05
                    })
                else:
                    # Use Shapiro-Wilk for appropriate sample sizes
                    statistic, p_value = stats.shapiro(data)
                    results[col] = {
                        "test": "Shapiro-Wilk",
                        "statistic": float(statistic),
                        "p_value": float(p_value),
                        "is_normal": p_value > 0.05,
                        "n": int(len(data))
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
        """
        Detect multicollinearity using Variance Inflation Factor (VIF)
        
        Args:
            threshold: VIF threshold (values > 10 indicate high multicollinearity)
        
        Returns:
            Dict with VIF scores and problematic features
        """
        try:
            # Check if statsmodels is available
            try:
                from statsmodels.stats.outliers_influence import variance_inflation_factor
            except ImportError:
                logger.error("statsmodels not installed. Install with: pip install statsmodels")
                return {
                    "error": "statsmodels package required. Install with: pip install statsmodels --break-system-packages"
                }
            
            if len(self.numeric_cols) < 2:
                return {"error": "Need at least 2 numeric columns"}
            
            # Prepare data (remove NaN)
            df_clean = self.df[self.numeric_cols].dropna()
            
            if len(df_clean) == 0:
                return {"error": "No complete cases after removing NaN"}
            
            # Calculate VIF for each feature
            vif_data = []
            for i, col in enumerate(self.numeric_cols):
                try:
                    vif = variance_inflation_factor(df_clean.values, i)
                    vif_data.append({
                        "Feature": col,
                        "VIF": float(vif)
                    })
                except Exception as e:
                    logger.warning(f"Error calculating VIF for {col}: {e}")
                    vif_data.append({
                        "Feature": col,
                        "VIF": None
                    })
            
            # Identify problematic features
            high_vif_features = [item["Feature"] for item in vif_data 
                                if item["VIF"] is not None and item["VIF"] > threshold]
            
            result = {
                "vif_scores": vif_data,
                "high_vif_features": high_vif_features,
                "threshold": threshold,
                "has_multicollinearity": len(high_vif_features) > 0,
                "interpretation": self._interpret_vif(high_vif_features, threshold)
            }
            
            logger.info("Detected multicollinearity")
            return result
            
        except Exception as e:
            logger.error(f"Error detecting multicollinearity: {e}")
            return {"error": str(e)}
    
    def _interpret_vif(self, high_vif_features: List[str], threshold: float) -> str:
        """Generate interpretation for VIF analysis"""
        if not high_vif_features:
            return f"No multicollinearity detected (all VIF < {threshold})"
        
        return f"Multicollinearity detected in {len(high_vif_features)} feature(s): {', '.join(high_vif_features)}"
    
    def detect_outliers(
        self,
        column: str,
        method: str = 'iqr'
    ) -> Dict:
        """
        Detect outliers using IQR or Z-score method
        
        Args:
            column: Numeric column to check
            method: Detection method ('iqr' or 'zscore')
        
        Returns:
            Dict with outlier information
        """
        try:
            if column not in self.numeric_cols:
                raise ValueError(f"{column} is not a numeric column")
            
            data = self.df[column].dropna()
            
            if method == 'iqr':
                Q1 = data.quantile(0.25)
                Q3 = data.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outliers = data[(data < lower_bound) | (data > upper_bound)]
                
            elif method == 'zscore':
                z_scores = np.abs(stats.zscore(data))
                outliers = data[z_scores > 3]
                lower_bound = data.mean() - 3 * data.std()
                upper_bound = data.mean() + 3 * data.std()
                
            else:
                raise ValueError(f"Unknown method: {method}")
            
            result = {
                "column": column,
                "method": method,
                "n_outliers": int(len(outliers)),
                "outlier_percentage": float(len(outliers) / len(data) * 100),
                "lower_bound": float(lower_bound),
                "upper_bound": float(upper_bound),
                "outlier_values": outliers.tolist()[:20],  # First 20 outliers
                "interpretation": f"Found {len(outliers)} outliers ({len(outliers)/len(data)*100:.2f}%) using {method.upper()} method"
            }
            
            logger.info(f"Detected outliers in {column} using {method} method")
            return result
            
        except Exception as e:
            logger.error(f"Error detecting outliers: {e}")
            raise