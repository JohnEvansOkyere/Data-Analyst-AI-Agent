"""
Feature Selection Module
Provides comprehensive feature selection methods for machine learning.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
import warnings
warnings.filterwarnings('ignore')

from sklearn.feature_selection import (
    # Univariate selection
    SelectKBest, SelectPercentile, GenericUnivariateSelect,
    f_classif, f_regression, chi2, mutual_info_classif, mutual_info_regression,
    # Model-based selection
    SelectFromModel, RFE, RFECV,
    # Variance-based
    VarianceThreshold
)

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.linear_model import Lasso, Ridge, LogisticRegression
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder


class FeatureSelector:
    """
    Comprehensive feature selection using multiple methods.
    """

    def __init__(self):
        self.selector = None
        self.selected_features = None
        self.feature_scores = None
        self.method_used = None

    def variance_threshold_selection(
        self,
        df: pd.DataFrame,
        threshold: float = 0.0,
        exclude_columns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Select features based on variance threshold.

        Args:
            df: Input DataFrame
            threshold: Minimum variance threshold
            exclude_columns: Columns to exclude from selection

        Returns:
            Selection results with feature variances
        """
        if exclude_columns is None:
            exclude_columns = []

        # Select numeric columns only
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        feature_cols = [col for col in numeric_cols if col not in exclude_columns]

        X = df[feature_cols].fillna(0)

        # Apply variance threshold
        selector = VarianceThreshold(threshold=threshold)
        selector.fit(X)

        # Get selected features
        selected_mask = selector.get_support()
        selected_features = [feature_cols[i] for i, selected in enumerate(selected_mask) if selected]
        removed_features = [feature_cols[i] for i, selected in enumerate(selected_mask) if not selected]

        # Calculate variances
        variances = pd.DataFrame({
            'feature': feature_cols,
            'variance': selector.variances_,
            'selected': selected_mask
        }).sort_values('variance', ascending=False)

        self.selector = selector
        self.selected_features = selected_features
        self.method_used = 'variance_threshold'

        return {
            'method': 'variance_threshold',
            'threshold': threshold,
            'n_features_original': len(feature_cols),
            'n_features_selected': len(selected_features),
            'selected_features': selected_features,
            'removed_features': removed_features,
            'feature_variances': variances.to_dict('records')
        }

    def correlation_based_selection(
        self,
        df: pd.DataFrame,
        target_column: str,
        threshold: float = 0.1,
        method: str = 'pearson'
    ) -> Dict[str, Any]:
        """
        Select features based on correlation with target.

        Args:
            df: Input DataFrame
            target_column: Target column name
            threshold: Minimum absolute correlation threshold
            method: 'pearson', 'spearman', or 'kendall'

        Returns:
            Selection results with correlations
        """
        # Get numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        feature_cols = [col for col in numeric_cols if col != target_column]

        # Calculate correlations
        correlations = df[feature_cols + [target_column]].corr(method=method)[target_column]
        correlations = correlations.drop(target_column)

        # Select features above threshold
        abs_correlations = correlations.abs()
        selected_features = abs_correlations[abs_correlations >= threshold].index.tolist()
        removed_features = abs_correlations[abs_correlations < threshold].index.tolist()

        # Create results DataFrame
        correlation_df = pd.DataFrame({
            'feature': correlations.index,
            'correlation': correlations.values,
            'abs_correlation': abs_correlations.values,
            'selected': abs_correlations.values >= threshold
        }).sort_values('abs_correlation', ascending=False)

        self.selected_features = selected_features
        self.feature_scores = correlations.to_dict()
        self.method_used = f'correlation_{method}'

        return {
            'method': f'correlation_{method}',
            'threshold': threshold,
            'n_features_original': len(feature_cols),
            'n_features_selected': len(selected_features),
            'selected_features': selected_features,
            'removed_features': removed_features,
            'correlations': correlation_df.to_dict('records')
        }

    def mutual_information_selection(
        self,
        df: pd.DataFrame,
        target_column: str,
        k: int = 10,
        task_type: str = 'classification'
    ) -> Dict[str, Any]:
        """
        Select features using mutual information.

        Args:
            df: Input DataFrame
            target_column: Target column name
            k: Number of top features to select
            task_type: 'classification' or 'regression'

        Returns:
            Selection results with MI scores
        """
        # Prepare data
        feature_cols = [col for col in df.columns if col != target_column]
        X = df[feature_cols].copy()
        y = df[target_column].copy()

        # Handle categorical features
        categorical_cols = X.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            X = pd.get_dummies(X, columns=categorical_cols, drop_first=True)

        X = X.fillna(0)

        # Encode target if needed
        if task_type == 'classification' and (y.dtype == 'object' or y.dtype.name == 'category'):
            le = LabelEncoder()
            y = le.fit_transform(y)

        # Calculate mutual information
        if task_type == 'classification':
            mi_scores = mutual_info_classif(X, y, random_state=42)
        else:
            mi_scores = mutual_info_regression(X, y, random_state=42)

        # Create scores DataFrame
        mi_df = pd.DataFrame({
            'feature': X.columns,
            'mi_score': mi_scores
        }).sort_values('mi_score', ascending=False)

        # Select top k features
        k = min(k, len(X.columns))
        selected_features = mi_df.head(k)['feature'].tolist()
        removed_features = mi_df.tail(len(X.columns) - k)['feature'].tolist()

        self.selected_features = selected_features
        self.feature_scores = dict(zip(mi_df['feature'], mi_df['mi_score']))
        self.method_used = f'mutual_information_{task_type}'

        return {
            'method': f'mutual_information_{task_type}',
            'k': k,
            'n_features_original': len(feature_cols),
            'n_features_selected': len(selected_features),
            'selected_features': selected_features,
            'removed_features': removed_features,
            'mi_scores': mi_df.to_dict('records')
        }

    def statistical_test_selection(
        self,
        df: pd.DataFrame,
        target_column: str,
        k: int = 10,
        task_type: str = 'classification',
        score_func: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Select features using statistical tests (ANOVA F-test, Chi-squared).

        Args:
            df: Input DataFrame
            target_column: Target column name
            k: Number of top features to select
            task_type: 'classification' or 'regression'
            score_func: 'f_test', 'chi2' (auto-selected based on task_type if None)

        Returns:
            Selection results with test scores
        """
        # Prepare data
        feature_cols = [col for col in df.columns if col != target_column]
        X = df[feature_cols].copy()
        y = df[target_column].copy()

        # Handle categorical features
        categorical_cols = X.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            X = pd.get_dummies(X, columns=categorical_cols, drop_first=True)

        X = X.fillna(0)

        # Encode target if needed
        if task_type == 'classification' and (y.dtype == 'object' or y.dtype.name == 'category'):
            le = LabelEncoder()
            y = le.fit_transform(y)

        # Select score function
        if score_func is None:
            score_func = 'f_test'

        if score_func == 'f_test':
            if task_type == 'classification':
                score_function = f_classif
            else:
                score_function = f_regression
        elif score_func == 'chi2':
            score_function = chi2
            # Chi2 requires non-negative values
            X = X - X.min() + 1e-10
        else:
            raise ValueError(f"Unknown score function: {score_func}")

        # Apply SelectKBest
        k = min(k, len(X.columns))
        selector = SelectKBest(score_func=score_function, k=k)
        selector.fit(X, y)

        # Get scores and selected features
        scores = selector.scores_
        selected_mask = selector.get_support()

        scores_df = pd.DataFrame({
            'feature': X.columns,
            'score': scores,
            'selected': selected_mask
        }).sort_values('score', ascending=False)

        selected_features = scores_df[scores_df['selected']]['feature'].tolist()
        removed_features = scores_df[~scores_df['selected']]['feature'].tolist()

        self.selector = selector
        self.selected_features = selected_features
        self.feature_scores = dict(zip(scores_df['feature'], scores_df['score']))
        self.method_used = f'{score_func}_{task_type}'

        return {
            'method': f'{score_func}_{task_type}',
            'k': k,
            'n_features_original': len(feature_cols),
            'n_features_selected': len(selected_features),
            'selected_features': selected_features,
            'removed_features': removed_features,
            'scores': scores_df.to_dict('records')
        }

    def model_based_selection(
        self,
        df: pd.DataFrame,
        target_column: str,
        model_type: str = 'random_forest',
        task_type: str = 'classification',
        threshold: str = 'mean',
        max_features: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Select features using model-based feature importance.

        Args:
            df: Input DataFrame
            target_column: Target column name
            model_type: 'random_forest', 'gradient_boosting', 'lasso', 'ridge'
            task_type: 'classification' or 'regression'
            threshold: Importance threshold ('mean', 'median', or numeric value)
            max_features: Maximum number of features to select

        Returns:
            Selection results with feature importances
        """
        # Prepare data
        feature_cols = [col for col in df.columns if col != target_column]
        X = df[feature_cols].copy()
        y = df[target_column].copy()

        # Handle categorical features
        categorical_cols = X.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            X = pd.get_dummies(X, columns=categorical_cols, drop_first=True)

        X = X.fillna(0)

        # Encode target if needed
        if task_type == 'classification' and (y.dtype == 'object' or y.dtype.name == 'category'):
            le = LabelEncoder()
            y = le.fit_transform(y)

        # Select model
        if task_type == 'classification':
            if model_type == 'random_forest':
                model = RandomForestClassifier(n_estimators=100, random_state=42)
            elif model_type == 'gradient_boosting':
                model = GradientBoostingClassifier(n_estimators=100, random_state=42)
            elif model_type == 'lasso':
                model = LogisticRegression(penalty='l1', solver='liblinear', random_state=42)
            else:
                model = RandomForestClassifier(n_estimators=100, random_state=42)
        else:
            if model_type == 'random_forest':
                model = RandomForestRegressor(n_estimators=100, random_state=42)
            elif model_type == 'gradient_boosting':
                model = GradientBoostingRegressor(n_estimators=100, random_state=42)
            elif model_type == 'lasso':
                model = Lasso(alpha=0.1, random_state=42)
            else:
                model = RandomForestRegressor(n_estimators=100, random_state=42)

        # Fit model and select features
        selector = SelectFromModel(model, threshold=threshold, max_features=max_features)
        selector.fit(X, y)

        # Get feature importances
        if hasattr(selector.estimator_, 'feature_importances_'):
            importances = selector.estimator_.feature_importances_
        elif hasattr(selector.estimator_, 'coef_'):
            importances = np.abs(selector.estimator_.coef_)
            if len(importances.shape) > 1:
                importances = importances[0]
        else:
            importances = np.zeros(X.shape[1])

        selected_mask = selector.get_support()

        importance_df = pd.DataFrame({
            'feature': X.columns,
            'importance': importances,
            'selected': selected_mask
        }).sort_values('importance', ascending=False)

        selected_features = importance_df[importance_df['selected']]['feature'].tolist()
        removed_features = importance_df[~importance_df['selected']]['feature'].tolist()

        self.selector = selector
        self.selected_features = selected_features
        self.feature_scores = dict(zip(importance_df['feature'], importance_df['importance']))
        self.method_used = f'{model_type}_{task_type}'

        return {
            'method': f'{model_type}_{task_type}',
            'threshold': str(threshold),
            'n_features_original': len(feature_cols),
            'n_features_selected': len(selected_features),
            'selected_features': selected_features,
            'removed_features': removed_features,
            'importances': importance_df.to_dict('records')
        }

    def recursive_feature_elimination(
        self,
        df: pd.DataFrame,
        target_column: str,
        n_features_to_select: Optional[int] = None,
        task_type: str = 'classification',
        step: int = 1,
        cv: int = 5
    ) -> Dict[str, Any]:
        """
        Recursive Feature Elimination with cross-validation.

        Args:
            df: Input DataFrame
            target_column: Target column name
            n_features_to_select: Number of features to select (None = auto with CV)
            task_type: 'classification' or 'regression'
            step: Number of features to remove at each iteration
            cv: Number of cross-validation folds

        Returns:
            Selection results with feature rankings
        """
        # Prepare data
        feature_cols = [col for col in df.columns if col != target_column]
        X = df[feature_cols].copy()
        y = df[target_column].copy()

        # Handle categorical features
        categorical_cols = X.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            X = pd.get_dummies(X, columns=categorical_cols, drop_first=True)

        X = X.fillna(0)

        # Encode target if needed
        if task_type == 'classification' and (y.dtype == 'object' or y.dtype.name == 'category'):
            le = LabelEncoder()
            y = le.fit_transform(y)

        # Select estimator
        if task_type == 'classification':
            estimator = RandomForestClassifier(n_estimators=50, random_state=42)
        else:
            estimator = RandomForestRegressor(n_estimators=50, random_state=42)

        # Apply RFE or RFECV
        if n_features_to_select is None:
            # Use RFECV for automatic selection
            selector = RFECV(estimator, step=step, cv=cv, scoring=None)
        else:
            # Use RFE with fixed number
            selector = RFE(estimator, n_features_to_select=n_features_to_select, step=step)

        selector.fit(X, y)

        # Get rankings and selected features
        selected_mask = selector.support_
        rankings = selector.ranking_

        ranking_df = pd.DataFrame({
            'feature': X.columns,
            'ranking': rankings,
            'selected': selected_mask
        }).sort_values('ranking')

        selected_features = ranking_df[ranking_df['selected']]['feature'].tolist()
        removed_features = ranking_df[~ranking_df['selected']]['feature'].tolist()

        self.selector = selector
        self.selected_features = selected_features
        self.method_used = f'rfe{"cv" if n_features_to_select is None else ""}_{task_type}'

        results = {
            'method': f'rfe{"cv" if n_features_to_select is None else ""}_{task_type}',
            'n_features_original': len(feature_cols),
            'n_features_selected': len(selected_features),
            'selected_features': selected_features,
            'removed_features': removed_features,
            'rankings': ranking_df.to_dict('records')
        }

        # Add CV scores if RFECV was used
        if hasattr(selector, 'cv_results_'):
            results['cv_scores'] = selector.cv_results_['mean_test_score'].tolist()
            results['optimal_n_features'] = int(selector.n_features_)

        return results

    def remove_multicollinear_features(
        self,
        df: pd.DataFrame,
        threshold: float = 0.9,
        method: str = 'pearson'
    ) -> Dict[str, Any]:
        """
        Remove highly correlated (multicollinear) features.

        Args:
            df: Input DataFrame
            threshold: Correlation threshold above which to remove features
            method: 'pearson', 'spearman', or 'kendall'

        Returns:
            Selection results with correlation pairs
        """
        # Get numeric columns only
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        X = df[numeric_cols].fillna(0)

        # Calculate correlation matrix
        corr_matrix = X.corr(method=method).abs()

        # Find pairs of highly correlated features
        upper_triangle = corr_matrix.where(
            np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
        )

        # Identify features to remove
        to_remove = set()
        correlated_pairs = []

        for column in upper_triangle.columns:
            high_corr = upper_triangle[column][upper_triangle[column] > threshold]
            for corr_feature, corr_value in high_corr.items():
                if column not in to_remove:
                    to_remove.add(corr_feature)
                    correlated_pairs.append({
                        'feature_1': column,
                        'feature_2': corr_feature,
                        'correlation': float(corr_value)
                    })

        removed_features = list(to_remove)
        selected_features = [col for col in numeric_cols if col not in to_remove]

        self.selected_features = selected_features
        self.method_used = f'multicollinearity_{method}'

        return {
            'method': f'multicollinearity_{method}',
            'threshold': threshold,
            'n_features_original': len(numeric_cols),
            'n_features_selected': len(selected_features),
            'n_features_removed': len(removed_features),
            'selected_features': selected_features,
            'removed_features': removed_features,
            'correlated_pairs': correlated_pairs
        }

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply feature selection to a DataFrame.

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with only selected features
        """
        if self.selected_features is None:
            raise ValueError("No features selected. Run a selection method first.")

        # Return only selected features
        available_features = [f for f in self.selected_features if f in df.columns]

        if len(available_features) != len(self.selected_features):
            missing = set(self.selected_features) - set(available_features)
            print(f"Warning: {len(missing)} selected features not found in DataFrame: {missing}")

        return df[available_features]


def compare_feature_selection_methods(
    df: pd.DataFrame,
    target_column: str,
    task_type: str = 'classification',
    methods: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Compare multiple feature selection methods.

    Args:
        df: Input DataFrame
        target_column: Target column name
        task_type: 'classification' or 'regression'
        methods: List of methods to compare (None = all)

    Returns:
        Comparison DataFrame
    """
    if methods is None:
        methods = ['variance', 'correlation', 'mutual_info', 'f_test', 'random_forest']

    results = []
    selector = FeatureSelector()

    for method in methods:
        try:
            if method == 'variance':
                result = selector.variance_threshold_selection(df, threshold=0.01)
            elif method == 'correlation':
                result = selector.correlation_based_selection(df, target_column, threshold=0.1)
            elif method == 'mutual_info':
                result = selector.mutual_information_selection(df, target_column, k=10, task_type=task_type)
            elif method == 'f_test':
                result = selector.statistical_test_selection(df, target_column, k=10, task_type=task_type)
            elif method == 'random_forest':
                result = selector.model_based_selection(df, target_column, task_type=task_type)
            else:
                continue

            results.append({
                'method': result['method'],
                'n_features_selected': result['n_features_selected'],
                'reduction_pct': (1 - result['n_features_selected'] / result['n_features_original']) * 100
            })

        except Exception as e:
            results.append({
                'method': method,
                'error': str(e)
            })

    return pd.DataFrame(results)
