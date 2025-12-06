"""
VexaAI - Clustering & Segmentation Page
Discover patterns and segments in your data using clustering algorithms
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Import modules
from core.ml_models import MLModelTrainer
from core.dimensionality_reduction import DimensionalityReducer
from core.feature_selection import FeatureSelector
from utils.logger import get_logger

logger = get_logger(__name__)

# Page config
st.set_page_config(page_title="Clustering & Segmentation - VexaAI", page_icon="🎯", layout="wide")

# Apply custom styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .cluster-card {
        background: linear-gradient(135deg, #f093fb15 0%, #f5576c15 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #f093fb;
        margin: 1rem 0;
    }
    .segment-info {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🎯 Clustering & Segmentation</h1>', unsafe_allow_html=True)
st.markdown("Discover hidden patterns and natural groupings in your data")

# Initialize session state - check for uploaded dataset
df = st.session_state.get('df')
if df is None or (hasattr(df, 'empty') and df.empty):
    st.warning("⚠️ No data available. Please upload a dataset first from the **Data Upload** page.")
    st.info("👉 Go to **1_Data_Upload** in the sidebar to upload your CSV or Excel file.")
    st.stop()

# Sidebar - Configuration
st.sidebar.header("⚙️ Clustering Configuration")

# Select features for clustering
all_numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

if len(all_numeric_cols) == 0:
    st.error("⚠️ No numeric columns found in the dataset. Clustering requires numeric features.")
    st.stop()

st.sidebar.subheader("Feature Selection")
selected_features = st.sidebar.multiselect(
    "Select Features for Clustering",
    options=all_numeric_cols,
    default=all_numeric_cols[:5] if len(all_numeric_cols) >= 5 else all_numeric_cols,
    help="Choose numeric columns to use for clustering"
)

if len(selected_features) < 2:
    st.warning("⚠️ Please select at least 2 features for clustering")
    st.stop()

# Preprocessing options
st.sidebar.subheader("Preprocessing")
scale_features = st.sidebar.checkbox("Standardize Features", value=True,
                                      help="Recommended for clustering - normalizes feature scales")
handle_missing = st.sidebar.selectbox(
    "Handle Missing Values",
    ["Drop rows", "Fill with mean", "Fill with median", "Fill with zero"],
    help="How to handle missing values"
)

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Data Overview",
    "🎯 Clustering",
    "📈 Cluster Analysis",
    "💼 Business Insights"
])

# Prepare data function
def prepare_clustering_data(df, features, scale=True, missing_method='Drop rows'):
    """Prepare data for clustering"""
    # Select features
    X = df[features].copy()

    # Handle missing values
    if missing_method == 'Drop rows':
        X = X.dropna()
    elif missing_method == 'Fill with mean':
        X = X.fillna(X.mean())
    elif missing_method == 'Fill with median':
        X = X.fillna(X.median())
    else:  # Fill with zero
        X = X.fillna(0)

    # Scale features
    if scale:
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        X = pd.DataFrame(X_scaled, columns=features, index=X.index)
        return X, scaler

    return X, None

# ========================================
# TAB 1: Data Overview
# ========================================
with tab1:
    st.header("Data Overview for Clustering")

    # Prepare data
    X_prepared, scaler = prepare_clustering_data(df, selected_features, scale_features, handle_missing)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Samples", len(df))
    with col2:
        st.metric("Samples for Clustering", len(X_prepared))
    with col3:
        st.metric("Features Selected", len(selected_features))
    with col4:
        missing_pct = ((len(df) - len(X_prepared)) / len(df) * 100)
        st.metric("Data Used", f"{100-missing_pct:.1f}%")

    # Feature statistics
    st.subheader("Feature Statistics")
    stats_df = X_prepared.describe().T
    stats_df['missing'] = df[selected_features].isnull().sum().values
    stats_df['missing_pct'] = (stats_df['missing'] / len(df) * 100).round(2)
    st.dataframe(stats_df, use_container_width=True)

    # Feature correlations
    st.subheader("Feature Correlation Heatmap")
    corr_matrix = X_prepared.corr()

    fig = px.imshow(
        corr_matrix,
        text_auto='.2f',
        aspect='auto',
        color_continuous_scale='RdBu_r',
        title="Feature Correlations"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Feature distributions
    st.subheader("Feature Distributions")

    col1, col2 = st.columns(2)

    for idx, feature in enumerate(selected_features[:6]):  # Limit to 6 for performance
        col = col1 if idx % 2 == 0 else col2

        with col:
            fig = px.histogram(
                X_prepared,
                x=feature,
                title=f"{feature} Distribution",
                marginal='box'
            )
            st.plotly_chart(fig, use_container_width=True)

# ========================================
# TAB 2: Clustering
# ========================================
with tab2:
    st.header("Clustering Algorithms")

    # Prepare data
    X_prepared, scaler = prepare_clustering_data(df, selected_features, scale_features, handle_missing)

    # Algorithm selection
    clustering_algorithm = st.selectbox(
        "Select Clustering Algorithm",
        [
            "K-Means",
            "DBSCAN",
            "Hierarchical (Agglomerative)",
            "Mean Shift",
            "Spectral Clustering"
        ],
        help="Choose the clustering algorithm to use"
    )

    # Algorithm-specific parameters
    st.subheader("Algorithm Parameters")

    col1, col2, col3 = st.columns(3)

    params = {}

    if clustering_algorithm == "K-Means":
        with col1:
            n_clusters = st.slider("Number of Clusters", 2, 15, 3)
            params['n_clusters'] = n_clusters
        with col2:
            max_iter = st.slider("Max Iterations", 100, 1000, 300)
            params['max_iter'] = max_iter
        with col3:
            n_init = st.slider("Number of Initializations", 5, 20, 10)
            params['n_init'] = n_init

    elif clustering_algorithm == "DBSCAN":
        with col1:
            eps = st.slider("Epsilon (neighborhood size)", 0.1, 5.0, 0.5, 0.1)
            params['eps'] = eps
        with col2:
            min_samples = st.slider("Minimum Samples", 2, 20, 5)
            params['min_samples'] = min_samples

    elif clustering_algorithm == "Hierarchical (Agglomerative)":
        with col1:
            n_clusters = st.slider("Number of Clusters", 2, 15, 3)
            params['n_clusters'] = n_clusters
        with col2:
            linkage = st.selectbox("Linkage Method", ['ward', 'complete', 'average', 'single'])
            params['linkage'] = linkage

    elif clustering_algorithm == "Mean Shift":
        st.info("Mean Shift automatically determines the number of clusters")
        with col1:
            bandwidth = st.slider("Bandwidth (kernel width)", 0.5, 5.0, 1.0, 0.1)
            params['bandwidth'] = bandwidth

    elif clustering_algorithm == "Spectral Clustering":
        with col1:
            n_clusters = st.slider("Number of Clusters", 2, 15, 3)
            params['n_clusters'] = n_clusters
        with col2:
            affinity = st.selectbox("Affinity", ['rbf', 'nearest_neighbors'])
            params['affinity'] = affinity

    # Run clustering button
    col1, col2 = st.columns([1, 3])

    with col1:
        run_clustering = st.button("🎯 Run Clustering", type="primary", use_container_width=True)

    with col2:
        visualize_2d = st.checkbox("Visualize in 2D (using PCA)", value=True)

    if run_clustering:
        with st.spinner(f"Running {clustering_algorithm}..."):
            try:
                # Initialize trainer
                trainer = MLModelTrainer()

                # Map algorithm name to model name
                model_map = {
                    "K-Means": "kmeans",
                    "DBSCAN": "dbscan",
                    "Hierarchical (Agglomerative)": "hierarchical",
                    "Mean Shift": "meanshift",
                    "Spectral Clustering": "spectral"
                }

                model_name = model_map[clustering_algorithm]

                # Create dummy target for clustering (not used)
                y_dummy = np.zeros(len(X_prepared))

                # Train clustering model
                result = trainer.train_model(
                    model_name,
                    X_prepared.values,
                    y_dummy,
                    model_type='clustering',
                    params=params
                )

                # Get cluster labels
                if hasattr(trainer.model, 'labels_'):
                    labels = trainer.model.labels_
                elif hasattr(trainer.model, 'predict'):
                    labels = trainer.model.predict(X_prepared.values)
                else:
                    st.error("Could not get cluster labels from model")
                    st.stop()

                # Store results in session state
                st.session_state['cluster_labels'] = labels
                st.session_state['cluster_model'] = trainer
                st.session_state['clustering_features'] = selected_features
                st.session_state['X_prepared'] = X_prepared

                # Calculate metrics
                from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score

                # Filter out noise points for DBSCAN
                valid_mask = labels != -1
                n_noise = np.sum(labels == -1)

                if valid_mask.sum() > 0:
                    silhouette = silhouette_score(X_prepared.values[valid_mask], labels[valid_mask])
                    davies_bouldin = davies_bouldin_score(X_prepared.values[valid_mask], labels[valid_mask])
                    calinski = calinski_harabasz_score(X_prepared.values[valid_mask], labels[valid_mask])
                else:
                    silhouette = davies_bouldin = calinski = None

                n_clusters_found = len(np.unique(labels[labels != -1]))

                st.success(f"✅ Clustering complete! Found {n_clusters_found} clusters")

                # Display metrics
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Clusters Found", n_clusters_found)
                with col2:
                    if silhouette is not None:
                        st.metric("Silhouette Score", f"{silhouette:.4f}")
                        st.caption("Higher is better (max 1.0)")
                with col3:
                    if davies_bouldin is not None:
                        st.metric("Davies-Bouldin", f"{davies_bouldin:.4f}")
                        st.caption("Lower is better")
                with col4:
                    if n_noise > 0:
                        st.metric("Noise Points", n_noise)
                        st.caption(f"{n_noise/len(labels)*100:.1f}% of data")

                # Cluster distribution
                st.subheader("Cluster Distribution")

                cluster_counts = pd.Series(labels).value_counts().sort_index()
                cluster_df = pd.DataFrame({
                    'Cluster': cluster_counts.index,
                    'Count': cluster_counts.values,
                    'Percentage': (cluster_counts.values / len(labels) * 100).round(2)
                })
                cluster_df['Cluster'] = cluster_df['Cluster'].apply(
                    lambda x: f'Cluster {x}' if x != -1 else 'Noise'
                )

                col1, col2 = st.columns([1, 2])

                with col1:
                    st.dataframe(cluster_df, use_container_width=True, hide_index=True)

                with col2:
                    fig = px.pie(
                        cluster_df,
                        values='Count',
                        names='Cluster',
                        title='Cluster Size Distribution'
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # Visualization
                if visualize_2d:
                    st.subheader("2D Visualization (PCA)")

                    # Reduce to 2D using PCA
                    reducer = DimensionalityReducer()
                    pca_result = reducer.pca_analysis(
                        pd.DataFrame(X_prepared.values, columns=selected_features),
                        n_components=2,
                        scale_features=False  # Already scaled
                    )

                    # Add cluster labels to PCA data
                    pca_df = pca_result['transformed_data'].copy()
                    pca_df['Cluster'] = labels
                    pca_df['Cluster'] = pca_df['Cluster'].apply(
                        lambda x: f'Cluster {x}' if x != -1 else 'Noise'
                    )

                    # Create scatter plot
                    fig = px.scatter(
                        pca_df,
                        x='PC1',
                        y='PC2',
                        color='Cluster',
                        title=f'{clustering_algorithm} - 2D Projection',
                        opacity=0.7,
                        size_max=10
                    )

                    fig.update_layout(
                        width=800,
                        height=600
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # Show variance explained
                    st.info(f"PCA Variance Explained: {pca_result['total_variance_explained']*100:.2f}%")

            except Exception as e:
                st.error(f"Error during clustering: {str(e)}")
                logger.error(f"Clustering error: {e}")
                import traceback
                st.code(traceback.format_exc())

# ========================================
# TAB 3: Cluster Analysis
# ========================================
with tab3:
    st.header("Cluster Analysis & Profiling")

    if 'cluster_labels' not in st.session_state:
        st.info("👈 Run clustering in the **Clustering** tab first to analyze clusters")
    else:
        labels = st.session_state['cluster_labels']
        X_prepared = st.session_state['X_prepared']
        features = st.session_state['clustering_features']

        # Add clusters to original dataframe
        df_with_clusters = df.loc[X_prepared.index].copy()
        df_with_clusters['Cluster'] = labels

        # Filter out noise if present
        unique_clusters = sorted([c for c in np.unique(labels) if c != -1])

        if -1 in labels:
            st.warning(f"⚠️ {np.sum(labels == -1)} noise points detected (labeled as -1)")

        # Cluster selection
        selected_cluster = st.selectbox(
            "Select Cluster to Analyze",
            options=unique_clusters,
            format_func=lambda x: f"Cluster {x}"
        )

        # Get cluster data
        cluster_mask = df_with_clusters['Cluster'] == selected_cluster
        cluster_data = df_with_clusters[cluster_mask]

        st.subheader(f"Cluster {selected_cluster} Profile")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Cluster Size", len(cluster_data))
        with col2:
            st.metric("% of Total", f"{len(cluster_data)/len(df_with_clusters)*100:.2f}%")
        with col3:
            st.metric("Features Used", len(features))

        # Feature statistics comparison
        st.subheader("Feature Statistics Comparison")

        comparison_data = []

        for feature in features:
            cluster_mean = cluster_data[feature].mean()
            overall_mean = df_with_clusters[feature].mean()
            cluster_std = cluster_data[feature].std()
            overall_std = df_with_clusters[feature].std()

            comparison_data.append({
                'Feature': feature,
                'Cluster Mean': f"{cluster_mean:.2f}",
                'Overall Mean': f"{overall_mean:.2f}",
                'Difference': f"{cluster_mean - overall_mean:+.2f}",
                'Cluster Std': f"{cluster_std:.2f}",
                'Overall Std': f"{overall_std:.2f}"
            })

        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)

        # Feature comparison visualization
        st.subheader("Feature Distribution Comparison")

        selected_feature = st.selectbox(
            "Select Feature to Visualize",
            options=features
        )

        fig = go.Figure()

        # Overall distribution
        fig.add_trace(go.Histogram(
            x=df_with_clusters[selected_feature],
            name='Overall',
            opacity=0.5,
            marker_color='blue'
        ))

        # Cluster distribution
        fig.add_trace(go.Histogram(
            x=cluster_data[selected_feature],
            name=f'Cluster {selected_cluster}',
            opacity=0.7,
            marker_color='red'
        ))

        fig.update_layout(
            title=f'{selected_feature} Distribution',
            xaxis_title=selected_feature,
            yaxis_title='Count',
            barmode='overlay'
        )

        st.plotly_chart(fig, use_container_width=True)

        # Cluster characteristics
        st.subheader("Top Characteristics")

        # Find features where cluster differs most from overall
        differences = []
        for feature in features:
            cluster_mean = cluster_data[feature].mean()
            overall_mean = df_with_clusters[feature].mean()
            overall_std = df_with_clusters[feature].std()

            # Z-score of difference
            z_score = (cluster_mean - overall_mean) / overall_std if overall_std > 0 else 0

            differences.append({
                'Feature': feature,
                'Z-Score': abs(z_score),
                'Direction': 'Higher' if z_score > 0 else 'Lower',
                'Cluster Mean': cluster_mean,
                'Overall Mean': overall_mean
            })

        diff_df = pd.DataFrame(differences).sort_values('Z-Score', ascending=False)

        st.markdown("**Features that define this cluster (ordered by deviation from overall mean):**")

        for idx, row in diff_df.head(5).iterrows():
            direction_emoji = "📈" if row['Direction'] == 'Higher' else "📉"
            st.markdown(
                f"{direction_emoji} **{row['Feature']}**: {row['Direction']} than average "
                f"(Cluster: {row['Cluster Mean']:.2f}, Overall: {row['Overall Mean']:.2f})"
            )

# ========================================
# TAB 4: Business Insights
# ========================================
with tab4:
    st.header("Business Insights & Export")

    if 'cluster_labels' not in st.session_state:
        st.info("👈 Run clustering in the **Clustering** tab first to generate insights")
    else:
        labels = st.session_state['cluster_labels']
        X_prepared = st.session_state['X_prepared']
        features = st.session_state['clustering_features']

        # Add clusters to original dataframe
        df_with_clusters = df.loc[X_prepared.index].copy()
        df_with_clusters['Cluster'] = labels

        st.subheader("Cluster Summary")

        # Overall cluster summary
        cluster_summary = []

        for cluster_id in sorted([c for c in np.unique(labels) if c != -1]):
            cluster_data = df_with_clusters[df_with_clusters['Cluster'] == cluster_id]

            # Get top characteristics
            characteristics = []
            for feature in features[:3]:  # Top 3 features
                cluster_mean = cluster_data[feature].mean()
                overall_mean = df_with_clusters[feature].mean()

                if cluster_mean > overall_mean:
                    characteristics.append(f"High {feature}")
                else:
                    characteristics.append(f"Low {feature}")

            cluster_summary.append({
                'Cluster': f'Cluster {cluster_id}',
                'Size': len(cluster_data),
                'Percentage': f"{len(cluster_data)/len(df_with_clusters)*100:.1f}%",
                'Key Characteristics': ', '.join(characteristics)
            })

        summary_df = pd.DataFrame(cluster_summary)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

        # Export options
        st.subheader("Export Clustered Data")

        col1, col2, col3 = st.columns(3)

        with col1:
            # Download full dataset with clusters
            csv = df_with_clusters.to_csv(index=False)
            st.download_button(
                label="📥 Download Full Data with Clusters",
                data=csv,
                file_name="clustered_data.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col2:
            # Download cluster summary
            summary_csv = summary_df.to_csv(index=False)
            st.download_button(
                label="📊 Download Cluster Summary",
                data=summary_csv,
                file_name="cluster_summary.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col3:
            # Download cluster profiles
            profiles = []
            for cluster_id in sorted([c for c in np.unique(labels) if c != -1]):
                cluster_data = df_with_clusters[df_with_clusters['Cluster'] == cluster_id]

                profile = {'Cluster': f'Cluster {cluster_id}', 'Size': len(cluster_data)}

                for feature in features:
                    profile[f'{feature}_mean'] = cluster_data[feature].mean()
                    profile[f'{feature}_std'] = cluster_data[feature].std()

                profiles.append(profile)

            profiles_df = pd.DataFrame(profiles)
            profiles_csv = profiles_df.to_csv(index=False)

            st.download_button(
                label="📈 Download Cluster Profiles",
                data=profiles_csv,
                file_name="cluster_profiles.csv",
                mime="text/csv",
                use_container_width=True
            )

        # Sample data from each cluster
        st.subheader("Sample Data from Each Cluster")

        for cluster_id in sorted([c for c in np.unique(labels) if c != -1]):
            with st.expander(f"Cluster {cluster_id} - Sample Data (first 5 rows)"):
                cluster_data = df_with_clusters[df_with_clusters['Cluster'] == cluster_id]
                st.dataframe(cluster_data.head(), use_container_width=True)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p>🎯 Powered by VexaAI | Advanced Clustering & Segmentation</p>
</div>
""", unsafe_allow_html=True)
