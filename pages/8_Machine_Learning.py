"""
VexaAI - Machine Learning Page
Train, evaluate, and compare ML models
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Import ML modules
from core.ml_models import MLModelTrainer, compare_models
from core.feature_selection import FeatureSelector, compare_feature_selection_methods
from core.dimensionality_reduction import DimensionalityReducer, compare_reduction_methods
from database.supabase_manager import SupabaseManager
from utils.logger import get_logger

logger = get_logger(__name__)

# Page config
st.set_page_config(page_title="Machine Learning - VexaAI", page_icon="🤖", layout="wide")

# Apply custom styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
    }
    .feature-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🤖 Machine Learning</h1>', unsafe_allow_html=True)
st.markdown("Train and evaluate machine learning models on your data")

# Initialize session state - check for uploaded dataset
df = st.session_state.get('df')
if df is None or (hasattr(df, 'empty') and df.empty):
    st.warning("⚠️ No data available. Please upload a dataset first from the **Data Upload** page.")
    st.info("👉 Go to **1_Data_Upload** in the sidebar to upload your CSV or Excel file.")
    st.stop()

# Sidebar - Model Configuration
st.sidebar.header("⚙️ ML Configuration")

# Task type
task_type = st.sidebar.selectbox(
    "Select Task Type",
    ["Classification", "Regression", "Clustering"],
    help="Choose the type of machine learning task"
)

# Main tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Data Preparation",
    "🔍 Feature Selection",
    "📉 Dimensionality Reduction",
    "🤖 Model Training",
    "📈 Model Evaluation"
])

# ========================================
# TAB 1: Data Preparation
# ========================================
with tab1:
    st.header("Data Preparation")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Dataset Overview")
        st.write(f"**Rows:** {len(df):,}")
        st.write(f"**Columns:** {len(df.columns):,}")

        # Show data types
        st.write("**Data Types:**")
        dtype_df = pd.DataFrame({
            'Column': df.dtypes.index,
            'Type': df.dtypes.values.astype(str)
        })
        st.dataframe(dtype_df, use_container_width=True, height=300)

    with col2:
        st.subheader("Missing Values")
        missing = df.isnull().sum()
        missing_pct = (missing / len(df) * 100).round(2)

        missing_df = pd.DataFrame({
            'Column': missing.index,
            'Missing': missing.values,
            'Percentage': missing_pct.values
        })
        missing_df = missing_df[missing_df['Missing'] > 0]

        if len(missing_df) > 0:
            st.dataframe(missing_df, use_container_width=True)
            st.warning(f"⚠️ Found {len(missing_df)} columns with missing values")
        else:
            st.success("✅ No missing values found!")

    st.divider()

    # Target and feature selection
    st.subheader("Select Target and Features")

    col1, col2 = st.columns([1, 2])

    with col1:
        if task_type in ["Classification", "Regression"]:
            target_column = st.selectbox(
                "Target Column",
                options=df.columns.tolist(),
                help="Select the column you want to predict"
            )
            st.session_state['ml_target'] = target_column
        else:
            st.info("Clustering is unsupervised - no target column needed")
            target_column = None

    with col2:
        # Select features
        all_cols = df.columns.tolist()
        default_features = [col for col in all_cols if col != target_column] if target_column else all_cols

        selected_features = st.multiselect(
            "Feature Columns",
            options=all_cols,
            default=default_features,
            help="Select columns to use as features"
        )
        st.session_state['ml_features'] = selected_features

    # Data split configuration
    if task_type != "Clustering":
        st.subheader("Train-Test Split")

        col1, col2, col3 = st.columns(3)

        with col1:
            test_size = st.slider("Test Set Size", 0.1, 0.5, 0.2, 0.05)
        with col2:
            random_state = st.number_input("Random Seed", 0, 999, 42)
        with col3:
            scale_features = st.checkbox("Scale Features", value=True,
                                        help="Standardize features using StandardScaler")

        st.session_state['ml_test_size'] = test_size
        st.session_state['ml_random_state'] = random_state
        st.session_state['ml_scale_features'] = scale_features

# ========================================
# TAB 2: Feature Selection
# ========================================
with tab2:
    st.header("Feature Selection")
    st.markdown("Select the most important features for your model")

    if 'ml_target' not in st.session_state and task_type != "Clustering":
        st.warning("⚠️ Please select target column in Data Preparation tab first")
    else:
        selection_method = st.selectbox(
            "Selection Method",
            [
                "Variance Threshold",
                "Correlation with Target",
                "Mutual Information",
                "Statistical Tests (ANOVA/F-test)",
                "Model-Based (Random Forest)",
                "Recursive Feature Elimination",
                "Remove Multicollinear Features",
                "Compare All Methods"
            ]
        )

        col1, col2 = st.columns([2, 1])

        with col2:
            if selection_method == "Variance Threshold":
                threshold = st.slider("Variance Threshold", 0.0, 1.0, 0.01, 0.01)
            elif selection_method == "Correlation with Target":
                threshold = st.slider("Correlation Threshold", 0.0, 1.0, 0.1, 0.05)
            elif selection_method in ["Mutual Information", "Statistical Tests (ANOVA/F-test)"]:
                k_features = st.slider("Number of Features to Select", 5, min(50, len(df.columns)), 10)
            elif selection_method == "Remove Multicollinear Features":
                threshold = st.slider("Correlation Threshold", 0.5, 1.0, 0.9, 0.05)

        if st.button("🔍 Run Feature Selection", type="primary"):
            with st.spinner("Selecting features..."):
                try:
                    selector = FeatureSelector()

                    if selection_method == "Variance Threshold":
                        result = selector.variance_threshold_selection(df, threshold=threshold)

                    elif selection_method == "Correlation with Target":
                        result = selector.correlation_based_selection(
                            df, st.session_state['ml_target'], threshold=threshold
                        )

                    elif selection_method == "Mutual Information":
                        result = selector.mutual_information_selection(
                            df, st.session_state['ml_target'],
                            k=k_features,
                            task_type=task_type.lower()
                        )

                    elif selection_method == "Statistical Tests (ANOVA/F-test)":
                        result = selector.statistical_test_selection(
                            df, st.session_state['ml_target'],
                            k=k_features,
                            task_type=task_type.lower()
                        )

                    elif selection_method == "Model-Based (Random Forest)":
                        result = selector.model_based_selection(
                            df, st.session_state['ml_target'],
                            task_type=task_type.lower()
                        )

                    elif selection_method == "Recursive Feature Elimination":
                        result = selector.recursive_feature_elimination(
                            df, st.session_state['ml_target'],
                            task_type=task_type.lower()
                        )

                    elif selection_method == "Remove Multicollinear Features":
                        result = selector.remove_multicollinear_features(df, threshold=threshold)

                    elif selection_method == "Compare All Methods":
                        result = compare_feature_selection_methods(
                            df, st.session_state['ml_target'],
                            task_type=task_type.lower()
                        )
                        st.subheader("Method Comparison")
                        st.dataframe(result, use_container_width=True)
                        st.stop()

                    # Display results
                    st.success(f"✅ Feature selection complete!")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Original Features", result['n_features_original'])
                    with col2:
                        st.metric("Selected Features", result['n_features_selected'])
                    with col3:
                        reduction_pct = (1 - result['n_features_selected'] / result['n_features_original']) * 100
                        st.metric("Reduction", f"{reduction_pct:.1f}%")

                    # Show selected features
                    st.subheader("Selected Features")
                    st.write(result['selected_features'])

                    # Store in session state
                    st.session_state['selected_features'] = result['selected_features']
                    st.session_state['feature_selection_result'] = result

                    # Visualize feature scores/importances
                    if 'correlations' in result:
                        corr_df = pd.DataFrame(result['correlations']).head(20)
                        fig = px.bar(corr_df, x='feature', y='abs_correlation',
                                    title="Top 20 Features by Correlation",
                                    color='abs_correlation',
                                    color_continuous_scale='viridis')
                        st.plotly_chart(fig, use_container_width=True)

                    elif 'importances' in result:
                        imp_df = pd.DataFrame(result['importances']).head(20)
                        fig = px.bar(imp_df, x='feature', y='importance',
                                    title="Top 20 Features by Importance",
                                    color='importance',
                                    color_continuous_scale='viridis')
                        st.plotly_chart(fig, use_container_width=True)

                except Exception as e:
                    st.error(f"Error during feature selection: {str(e)}")
                    logger.error(f"Feature selection error: {e}")

# ========================================
# TAB 3: Dimensionality Reduction
# ========================================
with tab3:
    st.header("Dimensionality Reduction")
    st.markdown("Reduce data dimensions for visualization and analysis")

    reduction_method = st.selectbox(
        "Reduction Method",
        ["PCA", "t-SNE", "UMAP", "Truncated SVD", "Compare Methods"]
    )

    col1, col2 = st.columns([2, 1])

    with col2:
        n_components = st.slider("Number of Components", 2, min(10, len(df.select_dtypes(include=[np.number]).columns)), 2)

        if reduction_method == "t-SNE":
            perplexity = st.slider("Perplexity", 5.0, 50.0, 30.0, 5.0)
            learning_rate = st.slider("Learning Rate", 10.0, 1000.0, 200.0, 10.0)
        elif reduction_method == "UMAP":
            n_neighbors = st.slider("N Neighbors", 2, 100, 15)
            min_dist = st.slider("Min Distance", 0.0, 1.0, 0.1, 0.05)

    if st.button("📉 Run Dimensionality Reduction", type="primary"):
        with st.spinner(f"Applying {reduction_method}..."):
            try:
                reducer = DimensionalityReducer()

                if reduction_method == "PCA":
                    result = reducer.pca_analysis(df, n_components=n_components)
                elif reduction_method == "t-SNE":
                    result = reducer.tsne_analysis(df, n_components=n_components,
                                                  perplexity=perplexity,
                                                  learning_rate=learning_rate)
                elif reduction_method == "UMAP":
                    result = reducer.umap_analysis(df, n_components=n_components,
                                                  n_neighbors=n_neighbors,
                                                  min_dist=min_dist)
                elif reduction_method == "Truncated SVD":
                    result = reducer.truncated_svd_analysis(df, n_components=n_components)
                elif reduction_method == "Compare Methods":
                    result = compare_reduction_methods(df, n_components=n_components)
                    st.subheader("Method Comparison")
                    for method, method_result in result.items():
                        with st.expander(f"{method.upper()} Results"):
                            st.json(method_result)
                    st.stop()

                if 'error' in result:
                    st.error(result['error'])
                    if 'install_command' in result:
                        st.code(result['install_command'])
                else:
                    st.success(f"✅ {reduction_method} complete!")

                    # Display metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Original Dimensions", result['n_features_original'])
                    with col2:
                        st.metric("Reduced Dimensions", result['n_components'])
                    with col3:
                        if 'total_variance_explained' in result:
                            st.metric("Variance Explained", f"{result['total_variance_explained']*100:.1f}%")

                    # Visualize reduced data
                    if n_components == 2:
                        transformed_df = result['transformed_data']
                        col_names = list(transformed_df.columns)

                        # 2D scatter plot
                        fig = px.scatter(
                            transformed_df,
                            x=col_names[0],
                            y=col_names[1],
                            title=f"{reduction_method} - 2D Projection",
                            opacity=0.7
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    elif n_components == 3:
                        transformed_df = result['transformed_data']
                        col_names = list(transformed_df.columns)

                        # 3D scatter plot
                        fig = px.scatter_3d(
                            transformed_df,
                            x=col_names[0],
                            y=col_names[1],
                            z=col_names[2],
                            title=f"{reduction_method} - 3D Projection",
                            opacity=0.7
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    # Show explained variance (for PCA)
                    if 'explained_variance' in result:
                        st.subheader("Explained Variance")
                        var_df = pd.DataFrame(result['explained_variance'])

                        fig = go.Figure()
                        fig.add_trace(go.Bar(
                            x=var_df['component'],
                            y=var_df['explained_variance_ratio'],
                            name='Individual'
                        ))
                        fig.add_trace(go.Scatter(
                            x=var_df['component'],
                            y=var_df['cumulative_variance_ratio'],
                            name='Cumulative',
                            mode='lines+markers'
                        ))
                        fig.update_layout(
                            title="Explained Variance by Component",
                            xaxis_title="Component",
                            yaxis_title="Variance Ratio"
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    # Store results
                    st.session_state['reduction_result'] = result

            except Exception as e:
                st.error(f"Error during dimensionality reduction: {str(e)}")
                logger.error(f"Dimensionality reduction error: {e}")

# ========================================
# TAB 4: Model Training
# ========================================
with tab4:
    st.header("Model Training")

    if 'ml_target' not in st.session_state and task_type != "Clustering":
        st.warning("⚠️ Please configure data in the Data Preparation tab first")
    else:
        # Model selection
        if task_type == "Classification":
            available_models = [
                "Logistic Regression", "Random Forest", "Gradient Boosting",
                "Decision Tree", "SVC", "KNN", "Naive Bayes", "MLP", "Extra Trees"
            ]
        elif task_type == "Regression":
            available_models = [
                "Linear Regression", "Ridge", "Lasso", "Random Forest",
                "Gradient Boosting", "Decision Tree", "SVR", "KNN", "MLP", "Extra Trees"
            ]
        else:  # Clustering
            available_models = ["K-Means", "DBSCAN", "Hierarchical", "MeanShift", "Spectral"]

        selected_model = st.selectbox("Select Model", available_models)

        # Model parameters
        with st.expander("⚙️ Model Parameters"):
            params = {}

            if "Random Forest" in selected_model or "Extra Trees" in selected_model:
                params['n_estimators'] = st.slider("Number of Trees", 50, 500, 100, 50)
                params['max_depth'] = st.slider("Max Depth", 1, 50, 10)
            elif "Gradient Boosting" in selected_model:
                params['n_estimators'] = st.slider("Number of Estimators", 50, 500, 100, 50)
                params['learning_rate'] = st.slider("Learning Rate", 0.01, 1.0, 0.1, 0.01)
            elif "K-Means" in selected_model:
                params['n_clusters'] = st.slider("Number of Clusters", 2, 20, 3)
            elif "KNN" in selected_model:
                params['n_neighbors'] = st.slider("Number of Neighbors", 1, 50, 5)

        col1, col2 = st.columns([1, 1])

        with col1:
            train_button = st.button("🚀 Train Model", type="primary", use_container_width=True)

        with col2:
            if task_type != "Clustering":
                compare_button = st.button("📊 Compare Multiple Models", use_container_width=True)
            else:
                compare_button = False

        # Train single model
        if train_button:
            with st.spinner(f"Training {selected_model}..."):
                try:
                    trainer = MLModelTrainer()

                    # Prepare data
                    target_col = st.session_state.get('ml_target')
                    feature_cols = st.session_state.get('selected_features',
                                                        st.session_state.get('ml_features'))

                    data = trainer.prepare_data(
                        df,
                        target_col if task_type != "Clustering" else feature_cols[0],
                        feature_cols if task_type != "Clustering" else None,
                        test_size=st.session_state.get('ml_test_size', 0.2),
                        random_state=st.session_state.get('ml_random_state', 42),
                        scale_features=st.session_state.get('ml_scale_features', True)
                    )

                    # Train model
                    model_name = selected_model.lower().replace(" ", "_")
                    train_result = trainer.train_model(
                        model_name,
                        data['X_train'],
                        data['y_train'],
                        model_type=task_type.lower(),
                        params=params
                    )

                    st.success(f"✅ Model trained successfully!")

                    # Display training metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Training Time", f"{train_result['training_time']:.2f}s")
                    with col2:
                        if 'cv_mean' in train_result:
                            st.metric("CV Score", f"{train_result['cv_mean']:.4f}")
                    with col3:
                        if 'cv_std' in train_result:
                            st.metric("CV Std Dev", f"{train_result['cv_std']:.4f}")

                    # Store model and data
                    st.session_state['trained_model'] = trainer
                    st.session_state['train_data'] = data
                    st.session_state['train_result'] = train_result

                    # Show feature importance
                    if 'feature_importance' in train_result:
                        st.subheader("Feature Importance")
                        imp_df = pd.DataFrame(train_result['feature_importance']).head(20)
                        fig = px.bar(imp_df, x='feature', y='importance',
                                    title="Top 20 Most Important Features",
                                    color='importance',
                                    color_continuous_scale='viridis')
                        st.plotly_chart(fig, use_container_width=True)

                except Exception as e:
                    st.error(f"Error training model: {str(e)}")
                    logger.error(f"Model training error: {e}")

        # Compare models
        if compare_button:
            with st.spinner("Comparing models..."):
                try:
                    model_names = [m.lower().replace(" ", "_") for m in available_models[:5]]

                    comparison_df = compare_models(
                        df,
                        st.session_state['ml_target'],
                        model_names,
                        model_type=task_type.lower(),
                        feature_columns=st.session_state.get('selected_features',
                                                            st.session_state.get('ml_features'))
                    )

                    st.subheader("Model Comparison")
                    st.dataframe(comparison_df, use_container_width=True)

                    # Visualize comparison
                    if task_type == "Classification":
                        metric_col = 'accuracy'
                    else:
                        metric_col = 'r2'

                    if metric_col in comparison_df.columns:
                        fig = px.bar(comparison_df, x='model', y=metric_col,
                                    title=f"Model Comparison by {metric_col.upper()}",
                                    color=metric_col,
                                    color_continuous_scale='viridis')
                        st.plotly_chart(fig, use_container_width=True)

                except Exception as e:
                    st.error(f"Error comparing models: {str(e)}")
                    logger.error(f"Model comparison error: {e}")

# ========================================
# TAB 5: Model Evaluation
# ========================================
with tab5:
    st.header("Model Evaluation")

    if 'trained_model' not in st.session_state:
        st.info("👈 Train a model first in the Model Training tab")
    else:
        trainer = st.session_state['trained_model']
        data = st.session_state['train_data']

        # Evaluate on test set
        with st.spinner("Evaluating model..."):
            try:
                eval_result = trainer.evaluate_model(data['X_test'], data['y_test'])

                st.success("✅ Evaluation complete!")

                # Display metrics based on task type
                if eval_result['model_type'] == 'regression':
                    st.subheader("Regression Metrics")

                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("R² Score", f"{eval_result['metrics']['r2']:.4f}")
                    with col2:
                        st.metric("RMSE", f"{eval_result['metrics']['rmse']:.4f}")
                    with col3:
                        st.metric("MAE", f"{eval_result['metrics']['mae']:.4f}")
                    with col4:
                        if eval_result['metrics'].get('mape'):
                            st.metric("MAPE", f"{eval_result['metrics']['mape']:.2f}%")

                    # Predicted vs Actual plot
                    st.subheader("Predicted vs Actual Values")
                    pred_df = pd.DataFrame({
                        'Actual': data['y_test'],
                        'Predicted': eval_result['predictions']
                    })

                    fig = px.scatter(pred_df, x='Actual', y='Predicted',
                                    title="Predicted vs Actual",
                                    opacity=0.6)
                    fig.add_trace(go.Scatter(x=pred_df['Actual'], y=pred_df['Actual'],
                                            mode='lines', name='Perfect Prediction',
                                            line=dict(color='red', dash='dash')))
                    st.plotly_chart(fig, use_container_width=True)

                    # Residuals plot
                    st.subheader("Residual Analysis")
                    residual_df = pd.DataFrame({
                        'Predicted': eval_result['predictions'],
                        'Residuals': eval_result['residuals']
                    })

                    fig = px.scatter(residual_df, x='Predicted', y='Residuals',
                                    title="Residual Plot",
                                    opacity=0.6)
                    fig.add_hline(y=0, line_dash="dash", line_color="red")
                    st.plotly_chart(fig, use_container_width=True)

                elif eval_result['model_type'] == 'classification':
                    st.subheader("Classification Metrics")

                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Accuracy", f"{eval_result['metrics']['accuracy']:.4f}")
                    with col2:
                        st.metric("Precision", f"{eval_result['metrics']['precision']:.4f}")
                    with col3:
                        st.metric("Recall", f"{eval_result['metrics']['recall']:.4f}")
                    with col4:
                        st.metric("F1 Score", f"{eval_result['metrics']['f1']:.4f}")

                    # Confusion matrix
                    st.subheader("Confusion Matrix")
                    cm = np.array(eval_result['confusion_matrix'])

                    fig = px.imshow(cm, text_auto=True,
                                   title="Confusion Matrix",
                                   labels=dict(x="Predicted", y="Actual"),
                                   color_continuous_scale='Blues')
                    st.plotly_chart(fig, use_container_width=True)

                    # Classification report
                    st.subheader("Classification Report")
                    report_df = pd.DataFrame(eval_result['classification_report']).T
                    st.dataframe(report_df, use_container_width=True)

                elif eval_result['model_type'] == 'clustering':
                    st.subheader("Clustering Metrics")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Silhouette Score", f"{eval_result['metrics']['silhouette_score']:.4f}")
                    with col2:
                        st.metric("Davies-Bouldin Score", f"{eval_result['metrics']['davies_bouldin_score']:.4f}")
                    with col3:
                        st.metric("Calinski-Harabasz Score", f"{eval_result['metrics']['calinski_harabasz_score']:.2f}")

                    # Cluster sizes
                    st.subheader("Cluster Distribution")
                    cluster_df = pd.DataFrame({
                        'Cluster': list(eval_result['cluster_sizes'].keys()),
                        'Size': list(eval_result['cluster_sizes'].values())
                    })

                    fig = px.bar(cluster_df, x='Cluster', y='Size',
                                title="Samples per Cluster",
                                color='Size',
                                color_continuous_scale='viridis')
                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"Error evaluating model: {str(e)}")
                logger.error(f"Model evaluation error: {e}")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p>🤖 Powered by VexaAI | Advanced Machine Learning Platform</p>
</div>
""", unsafe_allow_html=True)
