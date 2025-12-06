"""
Dimensionality Reduction Module
Provides PCA, t-SNE, UMAP, and other dimensionality reduction techniques.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
import warnings
warnings.filterwarnings('ignore')

from sklearn.decomposition import PCA, TruncatedSVD, FactorAnalysis, FastICA, NMF
from sklearn.manifold import TSNE, Isomap, MDS, LocallyLinearEmbedding
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.preprocessing import StandardScaler
from sklearn.random_projection import GaussianRandomProjection, SparseRandomProjection


class DimensionalityReducer:
    """
    Comprehensive dimensionality reduction toolkit.
    """

    def __init__(self):
        self.reducer = None
        self.scaler = None
        self.method_used = None
        self.n_components = None
        self.feature_names = None

    def pca_analysis(
        self,
        df: pd.DataFrame,
        n_components: Optional[Union[int, float]] = None,
        scale_features: bool = True,
        exclude_columns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Principal Component Analysis.

        Args:
            df: Input DataFrame
            n_components: Number of components (int) or variance to retain (float 0-1)
            scale_features: Whether to standardize features
            exclude_columns: Columns to exclude

        Returns:
            PCA results with explained variance and components
        """
        if exclude_columns is None:
            exclude_columns = []

        # Select numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        feature_cols = [col for col in numeric_cols if col not in exclude_columns]

        X = df[feature_cols].fillna(0)
        self.feature_names = feature_cols

        # Scale features
        if scale_features:
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
        else:
            X_scaled = X.values

        # Determine n_components
        if n_components is None:
            n_components = min(X_scaled.shape)
        elif isinstance(n_components, float) and 0 < n_components < 1:
            # Keep variance ratio
            pass
        else:
            n_components = min(int(n_components), X_scaled.shape[1])

        # Apply PCA
        pca = PCA(n_components=n_components, random_state=42)
        X_transformed = pca.fit_transform(X_scaled)

        self.reducer = pca
        self.method_used = 'pca'
        self.n_components = pca.n_components_

        # Create component names
        component_names = [f'PC{i+1}' for i in range(pca.n_components_)]

        # Transformed data
        transformed_df = pd.DataFrame(
            X_transformed,
            columns=component_names,
            index=df.index
        )

        # Feature loadings (components)
        loadings = pd.DataFrame(
            pca.components_.T,
            columns=component_names,
            index=feature_cols
        )

        # Explained variance
        explained_variance = pd.DataFrame({
            'component': component_names,
            'explained_variance': pca.explained_variance_,
            'explained_variance_ratio': pca.explained_variance_ratio_,
            'cumulative_variance_ratio': np.cumsum(pca.explained_variance_ratio_)
        })

        # Feature importance (based on loadings)
        feature_importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': np.abs(loadings).sum(axis=1)
        }).sort_values('importance', ascending=False)

        return {
            'method': 'pca',
            'n_components': int(pca.n_components_),
            'n_features_original': len(feature_cols),
            'total_variance_explained': float(pca.explained_variance_ratio_.sum()),
            'transformed_data': transformed_df,
            'explained_variance': explained_variance.to_dict('records'),
            'loadings': loadings.to_dict(),
            'feature_importance': feature_importance.to_dict('records'),
            'singular_values': pca.singular_values_.tolist()
        }

    def tsne_analysis(
        self,
        df: pd.DataFrame,
        n_components: int = 2,
        perplexity: float = 30.0,
        learning_rate: float = 200.0,
        n_iter: int = 1000,
        scale_features: bool = True,
        exclude_columns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        t-SNE (t-Distributed Stochastic Neighbor Embedding).

        Args:
            df: Input DataFrame
            n_components: Number of dimensions (typically 2 or 3)
            perplexity: Balance between local and global structure (5-50)
            learning_rate: Learning rate (10-1000)
            n_iter: Number of iterations
            scale_features: Whether to standardize features
            exclude_columns: Columns to exclude

        Returns:
            t-SNE results
        """
        if exclude_columns is None:
            exclude_columns = []

        # Select numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        feature_cols = [col for col in numeric_cols if col not in exclude_columns]

        X = df[feature_cols].fillna(0)
        self.feature_names = feature_cols

        # Scale features
        if scale_features:
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
        else:
            X_scaled = X.values

        # Apply t-SNE
        tsne = TSNE(
            n_components=n_components,
            perplexity=perplexity,
            learning_rate=learning_rate,
            n_iter=n_iter,
            random_state=42,
            verbose=0
        )

        X_transformed = tsne.fit_transform(X_scaled)

        self.reducer = tsne
        self.method_used = 'tsne'
        self.n_components = n_components

        # Create component names
        component_names = [f'tSNE{i+1}' for i in range(n_components)]

        # Transformed data
        transformed_df = pd.DataFrame(
            X_transformed,
            columns=component_names,
            index=df.index
        )

        return {
            'method': 'tsne',
            'n_components': n_components,
            'n_features_original': len(feature_cols),
            'perplexity': perplexity,
            'learning_rate': learning_rate,
            'n_iter': n_iter,
            'kl_divergence': float(tsne.kl_divergence_),
            'transformed_data': transformed_df
        }

    def umap_analysis(
        self,
        df: pd.DataFrame,
        n_components: int = 2,
        n_neighbors: int = 15,
        min_dist: float = 0.1,
        metric: str = 'euclidean',
        scale_features: bool = True,
        exclude_columns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        UMAP (Uniform Manifold Approximation and Projection).
        Note: Requires 'umap-learn' package.

        Args:
            df: Input DataFrame
            n_components: Number of dimensions
            n_neighbors: Size of local neighborhood (2-100)
            min_dist: Minimum distance between points (0.0-1.0)
            metric: Distance metric
            scale_features: Whether to standardize features
            exclude_columns: Columns to exclude

        Returns:
            UMAP results
        """
        try:
            import umap
        except ImportError:
            return {
                'error': 'UMAP not installed. Install with: pip install umap-learn',
                'install_command': 'pip install umap-learn'
            }

        if exclude_columns is None:
            exclude_columns = []

        # Select numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        feature_cols = [col for col in numeric_cols if col not in exclude_columns]

        X = df[feature_cols].fillna(0)
        self.feature_names = feature_cols

        # Scale features
        if scale_features:
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
        else:
            X_scaled = X.values

        # Apply UMAP
        reducer = umap.UMAP(
            n_components=n_components,
            n_neighbors=n_neighbors,
            min_dist=min_dist,
            metric=metric,
            random_state=42
        )

        X_transformed = reducer.fit_transform(X_scaled)

        self.reducer = reducer
        self.method_used = 'umap'
        self.n_components = n_components

        # Create component names
        component_names = [f'UMAP{i+1}' for i in range(n_components)]

        # Transformed data
        transformed_df = pd.DataFrame(
            X_transformed,
            columns=component_names,
            index=df.index
        )

        return {
            'method': 'umap',
            'n_components': n_components,
            'n_features_original': len(feature_cols),
            'n_neighbors': n_neighbors,
            'min_dist': min_dist,
            'metric': metric,
            'transformed_data': transformed_df
        }

    def lda_analysis(
        self,
        df: pd.DataFrame,
        target_column: str,
        n_components: Optional[int] = None,
        scale_features: bool = True
    ) -> Dict[str, Any]:
        """
        Linear Discriminant Analysis (supervised).

        Args:
            df: Input DataFrame
            target_column: Target column for supervision
            n_components: Number of components (max = n_classes - 1)
            scale_features: Whether to standardize features

        Returns:
            LDA results
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
        self.feature_names = list(X.columns)

        # Encode target if needed
        from sklearn.preprocessing import LabelEncoder
        if y.dtype == 'object' or y.dtype.name == 'category':
            le = LabelEncoder()
            y = le.fit_transform(y)

        # Determine max components
        n_classes = len(np.unique(y))
        max_components = min(n_classes - 1, X.shape[1])

        if n_components is None:
            n_components = max_components
        else:
            n_components = min(n_components, max_components)

        # Scale features
        if scale_features:
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
        else:
            X_scaled = X

        # Apply LDA
        lda = LinearDiscriminantAnalysis(n_components=n_components)
        X_transformed = lda.fit_transform(X_scaled, y)

        self.reducer = lda
        self.method_used = 'lda'
        self.n_components = n_components

        # Create component names
        component_names = [f'LD{i+1}' for i in range(n_components)]

        # Transformed data
        transformed_df = pd.DataFrame(
            X_transformed,
            columns=component_names,
            index=df.index
        )

        # Explained variance ratio
        explained_variance = pd.DataFrame({
            'component': component_names,
            'explained_variance_ratio': lda.explained_variance_ratio_,
            'cumulative_variance_ratio': np.cumsum(lda.explained_variance_ratio_)
        })

        return {
            'method': 'lda',
            'n_components': n_components,
            'n_features_original': X.shape[1],
            'n_classes': n_classes,
            'total_variance_explained': float(lda.explained_variance_ratio_.sum()),
            'transformed_data': transformed_df,
            'explained_variance': explained_variance.to_dict('records')
        }

    def truncated_svd_analysis(
        self,
        df: pd.DataFrame,
        n_components: int = 2,
        n_iter: int = 5,
        exclude_columns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Truncated SVD (good for sparse matrices).

        Args:
            df: Input DataFrame
            n_components: Number of components
            n_iter: Number of iterations
            exclude_columns: Columns to exclude

        Returns:
            SVD results
        """
        if exclude_columns is None:
            exclude_columns = []

        # Select numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        feature_cols = [col for col in numeric_cols if col not in exclude_columns]

        X = df[feature_cols].fillna(0)
        self.feature_names = feature_cols

        # Apply SVD
        n_components = min(n_components, X.shape[1] - 1)
        svd = TruncatedSVD(n_components=n_components, n_iter=n_iter, random_state=42)
        X_transformed = svd.fit_transform(X)

        self.reducer = svd
        self.method_used = 'svd'
        self.n_components = n_components

        # Create component names
        component_names = [f'SVD{i+1}' for i in range(n_components)]

        # Transformed data
        transformed_df = pd.DataFrame(
            X_transformed,
            columns=component_names,
            index=df.index
        )

        # Explained variance
        explained_variance = pd.DataFrame({
            'component': component_names,
            'explained_variance_ratio': svd.explained_variance_ratio_,
            'cumulative_variance_ratio': np.cumsum(svd.explained_variance_ratio_)
        })

        return {
            'method': 'truncated_svd',
            'n_components': n_components,
            'n_features_original': len(feature_cols),
            'total_variance_explained': float(svd.explained_variance_ratio_.sum()),
            'transformed_data': transformed_df,
            'explained_variance': explained_variance.to_dict('records')
        }

    def autoencoder_analysis(
        self,
        df: pd.DataFrame,
        encoding_dim: int = 2,
        hidden_layers: List[int] = [64, 32],
        epochs: int = 100,
        batch_size: int = 32,
        scale_features: bool = True,
        exclude_columns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Autoencoder for dimensionality reduction.
        Note: Requires TensorFlow/Keras.

        Args:
            df: Input DataFrame
            encoding_dim: Dimension of encoded representation
            hidden_layers: Hidden layer sizes
            epochs: Training epochs
            batch_size: Batch size
            scale_features: Whether to standardize features
            exclude_columns: Columns to exclude

        Returns:
            Autoencoder results
        """
        try:
            from tensorflow import keras
            from tensorflow.keras import layers, models
        except ImportError:
            return {
                'error': 'TensorFlow not installed. Install with: pip install tensorflow',
                'install_command': 'pip install tensorflow'
            }

        if exclude_columns is None:
            exclude_columns = []

        # Select numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        feature_cols = [col for col in numeric_cols if col not in exclude_columns]

        X = df[feature_cols].fillna(0)
        self.feature_names = feature_cols
        input_dim = len(feature_cols)

        # Scale features
        if scale_features:
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
        else:
            X_scaled = X.values

        # Build autoencoder
        # Encoder
        encoder_input = layers.Input(shape=(input_dim,))
        x = encoder_input

        for hidden_size in hidden_layers:
            x = layers.Dense(hidden_size, activation='relu')(x)

        encoded = layers.Dense(encoding_dim, activation='relu', name='encoded')(x)

        # Decoder
        x = encoded
        for hidden_size in reversed(hidden_layers):
            x = layers.Dense(hidden_size, activation='relu')(x)

        decoder_output = layers.Dense(input_dim, activation='linear')(x)

        # Full autoencoder
        autoencoder = models.Model(encoder_input, decoder_output)
        encoder = models.Model(encoder_input, encoded)

        # Compile and train
        autoencoder.compile(optimizer='adam', loss='mse')
        history = autoencoder.fit(
            X_scaled, X_scaled,
            epochs=epochs,
            batch_size=batch_size,
            shuffle=True,
            verbose=0,
            validation_split=0.2
        )

        # Transform data
        X_transformed = encoder.predict(X_scaled, verbose=0)

        self.reducer = encoder
        self.method_used = 'autoencoder'
        self.n_components = encoding_dim

        # Create component names
        component_names = [f'AE{i+1}' for i in range(encoding_dim)]

        # Transformed data
        transformed_df = pd.DataFrame(
            X_transformed,
            columns=component_names,
            index=df.index
        )

        return {
            'method': 'autoencoder',
            'encoding_dim': encoding_dim,
            'n_features_original': input_dim,
            'hidden_layers': hidden_layers,
            'final_loss': float(history.history['loss'][-1]),
            'final_val_loss': float(history.history['val_loss'][-1]),
            'transformed_data': transformed_df,
            'training_history': {
                'loss': [float(x) for x in history.history['loss']],
                'val_loss': [float(x) for x in history.history['val_loss']]
            }
        }

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform new data using fitted reducer.

        Args:
            df: Input DataFrame

        Returns:
            Transformed DataFrame
        """
        if self.reducer is None:
            raise ValueError("No reducer fitted. Run an analysis method first.")

        # Get feature columns
        feature_cols = [col for col in self.feature_names if col in df.columns]

        if len(feature_cols) != len(self.feature_names):
            raise ValueError("Input DataFrame missing some features used in training")

        X = df[feature_cols].fillna(0)

        # Scale if scaler was used
        if self.scaler is not None:
            X_scaled = self.scaler.transform(X)
        else:
            X_scaled = X.values

        # Transform
        X_transformed = self.reducer.transform(X_scaled)

        # Create component names
        component_names = [f'{self.method_used.upper()}{i+1}' for i in range(self.n_components)]

        return pd.DataFrame(
            X_transformed,
            columns=component_names,
            index=df.index
        )


def compare_reduction_methods(
    df: pd.DataFrame,
    methods: Optional[List[str]] = None,
    n_components: int = 2,
    exclude_columns: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Compare multiple dimensionality reduction methods.

    Args:
        df: Input DataFrame
        methods: List of methods to compare
        n_components: Number of components for each method
        exclude_columns: Columns to exclude

    Returns:
        Comparison results
    """
    if methods is None:
        methods = ['pca', 'tsne', 'truncated_svd']

    results = {}
    reducer = DimensionalityReducer()

    for method in methods:
        try:
            if method == 'pca':
                result = reducer.pca_analysis(df, n_components=n_components, exclude_columns=exclude_columns)
            elif method == 'tsne':
                result = reducer.tsne_analysis(df, n_components=n_components, exclude_columns=exclude_columns)
            elif method == 'umap':
                result = reducer.umap_analysis(df, n_components=n_components, exclude_columns=exclude_columns)
            elif method == 'truncated_svd':
                result = reducer.truncated_svd_analysis(df, n_components=n_components, exclude_columns=exclude_columns)
            else:
                continue

            results[method] = result

        except Exception as e:
            results[method] = {'error': str(e)}

    return results
