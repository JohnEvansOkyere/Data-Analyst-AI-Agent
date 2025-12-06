"""
Machine Learning Models Module
Provides comprehensive ML capabilities including regression, classification, and clustering.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
import json
from datetime import datetime

# Sklearn imports
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, KFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    # Regression metrics
    mean_squared_error, mean_absolute_error, r2_score, mean_absolute_percentage_error,
    # Classification metrics
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    classification_report, confusion_matrix, roc_curve, precision_recall_curve,
    # Clustering metrics
    silhouette_score, davies_bouldin_score, calinski_harabasz_score
)

# Regression models
from sklearn.linear_model import (
    LinearRegression, Ridge, Lasso, ElasticNet,
    LogisticRegression, SGDRegressor
)
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestRegressor, RandomForestClassifier,
    GradientBoostingRegressor, GradientBoostingClassifier,
    AdaBoostRegressor, AdaBoostClassifier,
    ExtraTreesRegressor, ExtraTreesClassifier
)
from sklearn.svm import SVR, SVC
from sklearn.neighbors import KNeighborsRegressor, KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.neural_network import MLPRegressor, MLPClassifier

# Clustering
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering, MeanShift, SpectralClustering

import warnings
warnings.filterwarnings('ignore')


class MLModelTrainer:
    """
    Comprehensive Machine Learning model training and evaluation.
    """

    # Available models registry
    REGRESSION_MODELS = {
        'linear_regression': LinearRegression,
        'ridge': Ridge,
        'lasso': Lasso,
        'elastic_net': ElasticNet,
        'decision_tree': DecisionTreeRegressor,
        'random_forest': RandomForestRegressor,
        'gradient_boosting': GradientBoostingRegressor,
        'adaboost': AdaBoostRegressor,
        'svr': SVR,
        'knn': KNeighborsRegressor,
        'mlp': MLPRegressor,
        'sgd': SGDRegressor,
        'extra_trees': ExtraTreesRegressor
    }

    CLASSIFICATION_MODELS = {
        'logistic_regression': LogisticRegression,
        'decision_tree': DecisionTreeClassifier,
        'random_forest': RandomForestClassifier,
        'gradient_boosting': GradientBoostingClassifier,
        'adaboost': AdaBoostClassifier,
        'svc': SVC,
        'knn': KNeighborsClassifier,
        'naive_bayes': GaussianNB,
        'mlp': MLPClassifier,
        'extra_trees': ExtraTreesClassifier
    }

    CLUSTERING_MODELS = {
        'kmeans': KMeans,
        'dbscan': DBSCAN,
        'hierarchical': AgglomerativeClustering,
        'meanshift': MeanShift,
        'spectral': SpectralClustering
    }

    def __init__(self):
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_names = None
        self.target_name = None
        self.model_type = None
        self.training_history = []

    def prepare_data(
        self,
        df: pd.DataFrame,
        target_column: str,
        feature_columns: Optional[List[str]] = None,
        test_size: float = 0.2,
        random_state: int = 42,
        scale_features: bool = True
    ) -> Dict[str, Any]:
        """
        Prepare data for ML training.

        Args:
            df: Input DataFrame
            target_column: Name of target column
            feature_columns: List of feature columns (None = all except target)
            test_size: Proportion of test set
            random_state: Random seed
            scale_features: Whether to scale features

        Returns:
            Dictionary with train/test splits and metadata
        """
        # Select features
        if feature_columns is None:
            feature_columns = [col for col in df.columns if col != target_column]

        X = df[feature_columns].copy()
        y = df[target_column].copy()

        # Handle categorical features
        categorical_cols = X.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            # One-hot encode categorical variables
            X = pd.get_dummies(X, columns=categorical_cols, drop_first=True)

        # Handle missing values
        X = X.fillna(X.mean())

        # Encode target if categorical
        if y.dtype == 'object' or y.dtype.name == 'category':
            self.label_encoder = LabelEncoder()
            y = self.label_encoder.fit_transform(y)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

        # Scale features
        if scale_features:
            self.scaler = StandardScaler()
            X_train = self.scaler.fit_transform(X_train)
            X_test = self.scaler.transform(X_test)

            # Convert back to DataFrame for consistency
            X_train = pd.DataFrame(X_train, columns=X.columns)
            X_test = pd.DataFrame(X_test, columns=X.columns)

        self.feature_names = list(X.columns)
        self.target_name = target_column

        return {
            'X_train': X_train,
            'X_test': X_test,
            'y_train': y_train,
            'y_test': y_test,
            'feature_names': self.feature_names,
            'n_samples': len(df),
            'n_features': X.shape[1],
            'n_train': len(X_train),
            'n_test': len(X_test)
        }

    def train_model(
        self,
        model_name: str,
        X_train: Union[pd.DataFrame, np.ndarray],
        y_train: Union[pd.Series, np.ndarray],
        model_type: str = 'regression',
        params: Optional[Dict[str, Any]] = None,
        cv_folds: int = 5
    ) -> Dict[str, Any]:
        """
        Train a machine learning model.

        Args:
            model_name: Name of the model
            X_train: Training features
            y_train: Training target
            model_type: 'regression', 'classification', or 'clustering'
            params: Model hyperparameters
            cv_folds: Number of cross-validation folds

        Returns:
            Training results and metrics
        """
        self.model_type = model_type

        # Get model class
        if model_type == 'regression':
            model_class = self.REGRESSION_MODELS.get(model_name)
        elif model_type == 'classification':
            model_class = self.CLASSIFICATION_MODELS.get(model_name)
        elif model_type == 'clustering':
            model_class = self.CLUSTERING_MODELS.get(model_name)
        else:
            raise ValueError(f"Unknown model type: {model_type}")

        if model_class is None:
            raise ValueError(f"Unknown model: {model_name} for type {model_type}")

        # Initialize model with parameters
        if params is None:
            params = {}

        # Add default parameters for some models
        if model_name in ['random_forest', 'extra_trees']:
            params.setdefault('n_estimators', 100)
            params.setdefault('random_state', 42)
        elif model_name == 'gradient_boosting':
            params.setdefault('n_estimators', 100)
            params.setdefault('learning_rate', 0.1)
            params.setdefault('random_state', 42)
        elif model_name == 'mlp':
            params.setdefault('hidden_layer_sizes', (100,))
            params.setdefault('max_iter', 500)
            params.setdefault('random_state', 42)
        elif model_name == 'kmeans':
            params.setdefault('n_clusters', 3)
            params.setdefault('random_state', 42)

        self.model = model_class(**params)

        # Train model
        start_time = datetime.now()

        if model_type == 'clustering':
            # Clustering doesn't use y
            self.model.fit(X_train)
            labels = self.model.labels_ if hasattr(self.model, 'labels_') else self.model.predict(X_train)
            training_time = (datetime.now() - start_time).total_seconds()

            results = {
                'model_name': model_name,
                'model_type': model_type,
                'training_time': training_time,
                'n_clusters': len(np.unique(labels)),
                'labels': labels,
                'params': params
            }
        else:
            # Supervised learning
            self.model.fit(X_train, y_train)
            training_time = (datetime.now() - start_time).total_seconds()

            # Cross-validation
            cv_scores = cross_val_score(
                self.model, X_train, y_train,
                cv=cv_folds,
                scoring='r2' if model_type == 'regression' else 'accuracy'
            )

            results = {
                'model_name': model_name,
                'model_type': model_type,
                'training_time': training_time,
                'cv_scores': cv_scores.tolist(),
                'cv_mean': float(cv_scores.mean()),
                'cv_std': float(cv_scores.std()),
                'params': params
            }

            # Feature importance (if available)
            if hasattr(self.model, 'feature_importances_'):
                importances = self.model.feature_importances_
                feature_importance = pd.DataFrame({
                    'feature': self.feature_names,
                    'importance': importances
                }).sort_values('importance', ascending=False)
                results['feature_importance'] = feature_importance.to_dict('records')

            # Coefficients (for linear models)
            if hasattr(self.model, 'coef_'):
                coef = self.model.coef_
                if len(coef.shape) == 1:
                    coefficients = pd.DataFrame({
                        'feature': self.feature_names,
                        'coefficient': coef
                    }).sort_values('coefficient', ascending=False, key=abs)
                    results['coefficients'] = coefficients.to_dict('records')

        self.training_history.append(results)
        return results

    def evaluate_model(
        self,
        X_test: Union[pd.DataFrame, np.ndarray],
        y_test: Union[pd.Series, np.ndarray]
    ) -> Dict[str, Any]:
        """
        Evaluate trained model on test set.

        Args:
            X_test: Test features
            y_test: Test target

        Returns:
            Evaluation metrics
        """
        if self.model is None:
            raise ValueError("No model trained. Call train_model() first.")

        if self.model_type == 'clustering':
            # Clustering evaluation
            labels = self.model.predict(X_test) if hasattr(self.model, 'predict') else self.model.labels_

            metrics = {
                'silhouette_score': float(silhouette_score(X_test, labels)),
                'davies_bouldin_score': float(davies_bouldin_score(X_test, labels)),
                'calinski_harabasz_score': float(calinski_harabasz_score(X_test, labels))
            }

            return {
                'model_type': 'clustering',
                'metrics': metrics,
                'n_clusters': len(np.unique(labels)),
                'cluster_sizes': pd.Series(labels).value_counts().to_dict()
            }

        # Make predictions
        y_pred = self.model.predict(X_test)

        if self.model_type == 'regression':
            # Regression metrics
            metrics = {
                'mse': float(mean_squared_error(y_test, y_pred)),
                'rmse': float(np.sqrt(mean_squared_error(y_test, y_pred))),
                'mae': float(mean_absolute_error(y_test, y_pred)),
                'r2': float(r2_score(y_test, y_pred)),
                'mape': float(mean_absolute_percentage_error(y_test, y_pred)) if (y_test != 0).all() else None
            }

            # Prediction analysis
            residuals = y_test - y_pred

            return {
                'model_type': 'regression',
                'metrics': metrics,
                'predictions': y_pred.tolist() if hasattr(y_pred, 'tolist') else y_pred,
                'residuals': residuals.tolist() if hasattr(residuals, 'tolist') else residuals,
                'residual_stats': {
                    'mean': float(np.mean(residuals)),
                    'std': float(np.std(residuals)),
                    'min': float(np.min(residuals)),
                    'max': float(np.max(residuals))
                }
            }

        elif self.model_type == 'classification':
            # Classification metrics
            y_pred_proba = None
            if hasattr(self.model, 'predict_proba'):
                y_pred_proba = self.model.predict_proba(X_test)

            # Handle binary vs multiclass
            n_classes = len(np.unique(y_test))

            metrics = {
                'accuracy': float(accuracy_score(y_test, y_pred)),
                'precision': float(precision_score(y_test, y_pred, average='weighted', zero_division=0)),
                'recall': float(recall_score(y_test, y_pred, average='weighted', zero_division=0)),
                'f1': float(f1_score(y_test, y_pred, average='weighted', zero_division=0))
            }

            # ROC AUC for binary classification
            if n_classes == 2 and y_pred_proba is not None:
                metrics['roc_auc'] = float(roc_auc_score(y_test, y_pred_proba[:, 1]))

            # Confusion matrix
            cm = confusion_matrix(y_test, y_pred)

            # Classification report
            report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)

            results = {
                'model_type': 'classification',
                'metrics': metrics,
                'confusion_matrix': cm.tolist(),
                'classification_report': report,
                'predictions': y_pred.tolist() if hasattr(y_pred, 'tolist') else y_pred,
                'n_classes': n_classes
            }

            # Add probabilities if available
            if y_pred_proba is not None:
                results['prediction_probabilities'] = y_pred_proba.tolist()

            # Decode labels if encoded
            if self.label_encoder is not None:
                results['class_labels'] = self.label_encoder.classes_.tolist()

            return results

        return {}

    def predict(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        return_proba: bool = False
    ) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
        """
        Make predictions on new data.

        Args:
            X: Features to predict on
            return_proba: Return probabilities (classification only)

        Returns:
            Predictions (and probabilities if requested)
        """
        if self.model is None:
            raise ValueError("No model trained. Call train_model() first.")

        # Scale if scaler was used
        if self.scaler is not None:
            X = self.scaler.transform(X)

        predictions = self.model.predict(X)

        # Decode labels if encoded
        if self.label_encoder is not None and self.model_type == 'classification':
            predictions = self.label_encoder.inverse_transform(predictions)

        if return_proba and self.model_type == 'classification' and hasattr(self.model, 'predict_proba'):
            probabilities = self.model.predict_proba(X if self.scaler is None else X)
            return predictions, probabilities

        return predictions

    def hyperparameter_tuning(
        self,
        model_name: str,
        X_train: Union[pd.DataFrame, np.ndarray],
        y_train: Union[pd.Series, np.ndarray],
        param_grid: Dict[str, List[Any]],
        model_type: str = 'regression',
        cv_folds: int = 5,
        scoring: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform hyperparameter tuning using GridSearchCV.

        Args:
            model_name: Name of the model
            X_train: Training features
            y_train: Training target
            param_grid: Parameter grid for tuning
            model_type: 'regression' or 'classification'
            cv_folds: Number of CV folds
            scoring: Scoring metric

        Returns:
            Best parameters and results
        """
        # Get base model
        if model_type == 'regression':
            model_class = self.REGRESSION_MODELS.get(model_name)
            if scoring is None:
                scoring = 'r2'
        elif model_type == 'classification':
            model_class = self.CLASSIFICATION_MODELS.get(model_name)
            if scoring is None:
                scoring = 'accuracy'
        else:
            raise ValueError(f"Tuning not supported for {model_type}")

        if model_class is None:
            raise ValueError(f"Unknown model: {model_name}")

        base_model = model_class()

        # Grid search
        grid_search = GridSearchCV(
            base_model,
            param_grid,
            cv=cv_folds,
            scoring=scoring,
            n_jobs=-1,
            verbose=0
        )

        grid_search.fit(X_train, y_train)

        # Store best model
        self.model = grid_search.best_estimator_
        self.model_type = model_type

        return {
            'best_params': grid_search.best_params_,
            'best_score': float(grid_search.best_score_),
            'cv_results': {
                'mean_test_score': grid_search.cv_results_['mean_test_score'].tolist(),
                'std_test_score': grid_search.cv_results_['std_test_score'].tolist(),
                'params': grid_search.cv_results_['params']
            }
        }

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the trained model."""
        if self.model is None:
            return {'error': 'No model trained'}

        info = {
            'model_type': self.model_type,
            'model_class': type(self.model).__name__,
            'feature_names': self.feature_names,
            'target_name': self.target_name,
            'n_features': len(self.feature_names) if self.feature_names else None
        }

        # Add model-specific info
        if hasattr(self.model, 'get_params'):
            info['parameters'] = self.model.get_params()

        return info


def compare_models(
    df: pd.DataFrame,
    target_column: str,
    model_names: List[str],
    model_type: str = 'regression',
    feature_columns: Optional[List[str]] = None,
    test_size: float = 0.2,
    cv_folds: int = 5
) -> pd.DataFrame:
    """
    Compare multiple models on the same dataset.

    Args:
        df: Input DataFrame
        target_column: Target column name
        model_names: List of model names to compare
        model_type: 'regression' or 'classification'
        feature_columns: Feature columns (None = all except target)
        test_size: Test set proportion
        cv_folds: Cross-validation folds

    Returns:
        DataFrame with comparison results
    """
    results = []

    for model_name in model_names:
        try:
            trainer = MLModelTrainer()

            # Prepare data
            data = trainer.prepare_data(
                df, target_column, feature_columns, test_size
            )

            # Train model
            train_results = trainer.train_model(
                model_name,
                data['X_train'],
                data['y_train'],
                model_type=model_type,
                cv_folds=cv_folds
            )

            # Evaluate model
            eval_results = trainer.evaluate_model(
                data['X_test'],
                data['y_test']
            )

            # Combine results
            result = {
                'model': model_name,
                'training_time': train_results['training_time'],
                'cv_mean': train_results.get('cv_mean', None),
                'cv_std': train_results.get('cv_std', None)
            }

            # Add type-specific metrics
            if model_type == 'regression':
                result.update({
                    'r2': eval_results['metrics']['r2'],
                    'rmse': eval_results['metrics']['rmse'],
                    'mae': eval_results['metrics']['mae']
                })
            elif model_type == 'classification':
                result.update({
                    'accuracy': eval_results['metrics']['accuracy'],
                    'f1': eval_results['metrics']['f1'],
                    'precision': eval_results['metrics']['precision'],
                    'recall': eval_results['metrics']['recall']
                })

            results.append(result)

        except Exception as e:
            results.append({
                'model': model_name,
                'error': str(e)
            })

    comparison_df = pd.DataFrame(results)

    # Sort by performance metric
    if model_type == 'regression' and 'r2' in comparison_df.columns:
        comparison_df = comparison_df.sort_values('r2', ascending=False)
    elif model_type == 'classification' and 'accuracy' in comparison_df.columns:
        comparison_df = comparison_df.sort_values('accuracy', ascending=False)

    return comparison_df
