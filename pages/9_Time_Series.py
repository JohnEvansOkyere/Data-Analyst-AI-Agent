"""
VexaAI - Time Series Analysis Page
Analyze, decompose, and forecast time series data
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# Import time series modules
from core.time_series import TimeSeriesAnalyzer, auto_arima_order
from utils.logger import get_logger

logger = get_logger(__name__)

# Page config
st.set_page_config(page_title="Time Series Analysis - VexaAI", page_icon="📈", layout="wide")

# Apply custom styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #11998e15 0%, #38ef7d15 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #11998e;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">📈 Time Series Analysis</h1>', unsafe_allow_html=True)
st.markdown("Analyze temporal data, detect trends, and forecast future values")

# Initialize session state - check for uploaded dataset
df = st.session_state.get('df')
if df is None or (hasattr(df, 'empty') and df.empty):
    st.warning("⚠️ No data available. Please upload a dataset first from the **Data Upload** page.")
    st.info("👉 Go to **1_Data_Upload** in the sidebar to upload your CSV or Excel file.")
    st.stop()

# Sidebar - Configuration
st.sidebar.header("⚙️ Time Series Configuration")

# Select date and value columns
date_columns = []
for col in df.columns:
    try:
        # Skip numeric columns that look like IDs
        if df[col].dtype in ['int64', 'float64']:
            # Check if it's likely an ID (sequential integers)
            if df[col].nunique() == len(df):
                continue

        # Try to convert to datetime
        test_dates = pd.to_datetime(df[col], errors='coerce')

        # Only include if at least 50% of values are valid dates
        valid_pct = test_dates.notna().sum() / len(df)
        if valid_pct >= 0.5:
            date_columns.append(col)
    except:
        continue

if len(date_columns) == 0:
    st.error("⚠️ No date columns detected in the dataset.")
    st.info("""
    **Tips for time series analysis:**
    - Ensure you have a column with dates (e.g., '2024-01-01', 'Jan 2024')
    - Date columns should contain actual date/time values, not IDs
    - Common date column names: date, timestamp, time, datetime, period
    """)
    st.stop()

date_column = st.sidebar.selectbox("Date Column", date_columns)
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

if len(numeric_cols) == 0:
    st.error("⚠️ No numeric columns found for analysis.")
    st.stop()

value_column = st.sidebar.selectbox("Value Column", numeric_cols)

# Frequency
frequency_options = {
    'Auto-detect': None,
    'Daily': 'D',
    'Weekly': 'W',
    'Monthly': 'M',
    'Quarterly': 'Q',
    'Yearly': 'Y'
}
selected_freq = st.sidebar.selectbox("Frequency", list(frequency_options.keys()))
frequency = frequency_options[selected_freq]

# Main tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "🔄 Decomposition",
    "📉 Stationarity & ACF",
    "🎯 Forecasting",
    "🔍 Anomaly Detection"
])

# Initialize analyzer
analyzer = TimeSeriesAnalyzer()

# Prepare time series
try:
    ts = analyzer.prepare_time_series(df, date_column, value_column, frequency)
    st.session_state['time_series'] = ts
except Exception as e:
    st.error(f"Error preparing time series: {str(e)}")
    st.stop()

# ========================================
# TAB 1: Overview
# ========================================
with tab1:
    st.header("Time Series Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Data Points", len(ts))
    with col2:
        st.metric("Start Date", ts.index[0].strftime('%Y-%m-%d'))
    with col3:
        st.metric("End Date", ts.index[-1].strftime('%Y-%m-%d'))
    with col4:
        st.metric("Frequency", str(analyzer.frequency) if analyzer.frequency else "Unknown")

    # Plot time series
    st.subheader("Time Series Plot")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ts.index, y=ts.values, mode='lines', name=value_column))
    fig.update_layout(
        title=f"{value_column} over Time",
        xaxis_title="Date",
        yaxis_title=value_column,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    # Basic statistics
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Summary Statistics")
        stats_df = pd.DataFrame({
            'Statistic': ['Mean', 'Median', 'Std Dev', 'Min', 'Max', 'Range'],
            'Value': [
                f"{ts.mean():.2f}",
                f"{ts.median():.2f}",
                f"{ts.std():.2f}",
                f"{ts.min():.2f}",
                f"{ts.max():.2f}",
                f"{ts.max() - ts.min():.2f}"
            ]
        })
        st.dataframe(stats_df, use_container_width=True, hide_index=True)

    with col2:
        st.subheader("Trend Analysis")
        with st.spinner("Analyzing trend..."):
            trend_result = analyzer.trend_analysis(ts)

            st.write(f"**Direction:** {trend_result['trend_direction'].title()}")
            st.write(f"**Slope:** {trend_result['slope']:.4f}")
            st.write(f"**R² Score:** {trend_result['r_squared']:.4f}")
            st.write(f"**Total Change:** {trend_result['total_change']:.2f}")
            st.write(f"**Percent Change:** {trend_result['percent_change']:.2f}%")

# ========================================
# TAB 2: Decomposition
# ========================================
with tab2:
    st.header("Time Series Decomposition")
    st.markdown("Decompose the series into trend, seasonal, and residual components")

    col1, col2 = st.columns([2, 1])

    with col2:
        decomp_model = st.selectbox("Decomposition Model", ["Additive", "Multiplicative"])
        period = st.number_input("Seasonal Period", min_value=2, max_value=365, value=12,
                                help="Number of observations per seasonal cycle")

    if st.button("🔄 Decompose Time Series", type="primary"):
        with st.spinner("Decomposing time series..."):
            try:
                result = analyzer.decompose(
                    ts,
                    model=decomp_model.lower(),
                    period=period
                )

                if 'error' in result:
                    st.error(result['error'])
                else:
                    st.success("✅ Decomposition complete!")

                    # Display metrics
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Seasonal Strength", f"{result['seasonal_strength']:.4f}")
                    with col2:
                        st.metric("Trend Strength", f"{result['trend_strength']:.4f}")

                    # Plot components
                    fig = make_subplots(
                        rows=4, cols=1,
                        subplot_titles=('Observed', 'Trend', 'Seasonal', 'Residual'),
                        vertical_spacing=0.05
                    )

                    # Observed
                    observed_data = pd.Series(result['observed'])
                    fig.add_trace(
                        go.Scatter(x=list(observed_data.index), y=list(observed_data.values),
                                  mode='lines', name='Observed'),
                        row=1, col=1
                    )

                    # Trend
                    trend_data = pd.Series(result['trend'])
                    fig.add_trace(
                        go.Scatter(x=list(trend_data.index), y=list(trend_data.values),
                                  mode='lines', name='Trend'),
                        row=2, col=1
                    )

                    # Seasonal
                    seasonal_data = pd.Series(result['seasonal'])
                    fig.add_trace(
                        go.Scatter(x=list(seasonal_data.index), y=list(seasonal_data.values),
                                  mode='lines', name='Seasonal'),
                        row=3, col=1
                    )

                    # Residual
                    residual_data = pd.Series(result['residual'])
                    fig.add_trace(
                        go.Scatter(x=list(residual_data.index), y=list(residual_data.values),
                                  mode='lines', name='Residual'),
                        row=4, col=1
                    )

                    fig.update_layout(height=800, showlegend=False, title_text="Time Series Decomposition")
                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"Error during decomposition: {str(e)}")
                logger.error(f"Decomposition error: {e}")

# ========================================
# TAB 3: Stationarity & ACF
# ========================================
with tab3:
    st.header("Stationarity Tests & Autocorrelation")

    # Stationarity tests
    st.subheader("Stationarity Tests")

    if st.button("🔍 Test Stationarity", type="primary"):
        with st.spinner("Running stationarity tests..."):
            try:
                result = analyzer.analyze_stationarity(ts)

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Augmented Dickey-Fuller Test**")
                    st.write(f"Statistic: {result['adf_test']['statistic']:.4f}")
                    st.write(f"P-value: {result['adf_test']['p_value']:.4f}")

                    if result['adf_test']['is_stationary']:
                        st.success("✅ Series is stationary (ADF)")
                    else:
                        st.warning("⚠️ Series is non-stationary (ADF)")

                with col2:
                    st.markdown("**KPSS Test**")
                    st.write(f"Statistic: {result['kpss_test']['statistic']:.4f}")
                    st.write(f"P-value: {result['kpss_test']['p_value']:.4f}")

                    if result['kpss_test']['is_stationary']:
                        st.success("✅ Series is stationary (KPSS)")
                    else:
                        st.warning("⚠️ Series is non-stationary (KPSS)")

                st.info(f"**Recommendation:** {result['recommendation']}")

            except Exception as e:
                st.error(f"Error testing stationarity: {str(e)}")

    st.divider()

    # ACF/PACF Analysis
    st.subheader("Autocorrelation Analysis")

    lags = st.slider("Number of Lags", 10, 50, 40)

    if st.button("📊 Analyze Autocorrelation"):
        with st.spinner("Computing ACF and PACF..."):
            try:
                result = analyzer.autocorrelation_analysis(ts, lags=lags)

                col1, col2 = st.columns(2)

                with col1:
                    # ACF plot
                    fig = go.Figure()
                    fig.add_trace(go.Bar(x=result['lags'], y=result['acf'], name='ACF'))

                    # Add significance bounds
                    conf_int = 1.96 / np.sqrt(len(ts))
                    fig.add_hline(y=conf_int, line_dash="dash", line_color="red")
                    fig.add_hline(y=-conf_int, line_dash="dash", line_color="red")

                    fig.update_layout(title="Autocorrelation Function (ACF)",
                                    xaxis_title="Lag", yaxis_title="Correlation")
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    # PACF plot
                    fig = go.Figure()
                    fig.add_trace(go.Bar(x=result['lags'], y=result['pacf'], name='PACF'))

                    # Add significance bounds
                    fig.add_hline(y=conf_int, line_dash="dash", line_color="red")
                    fig.add_hline(y=-conf_int, line_dash="dash", line_color="red")

                    fig.update_layout(title="Partial Autocorrelation Function (PACF)",
                                    xaxis_title="Lag", yaxis_title="Correlation")
                    st.plotly_chart(fig, use_container_width=True)

                st.write(f"**Significant ACF Lags:** {result['significant_lags_acf'][:10]}")
                st.write(f"**Significant PACF Lags:** {result['significant_lags_pacf'][:10]}")

            except Exception as e:
                st.error(f"Error analyzing autocorrelation: {str(e)}")

# ========================================
# TAB 4: Forecasting
# ========================================
with tab4:
    st.header("Time Series Forecasting")

    model_type = st.selectbox(
        "Forecasting Model",
        ["ARIMA", "SARIMA", "Exponential Smoothing", "Auto ARIMA"]
    )

    col1, col2 = st.columns([2, 1])

    with col2:
        forecast_steps = st.slider("Forecast Horizon", 1, 100, 10)

        if model_type == "ARIMA":
            st.markdown("**ARIMA Parameters (p, d, q)**")
            p = st.number_input("p (AR order)", 0, 10, 1)
            d = st.number_input("d (Differencing)", 0, 2, 1)
            q = st.number_input("q (MA order)", 0, 10, 1)
            order = (p, d, q)
            seasonal_order = None

        elif model_type == "SARIMA":
            st.markdown("**ARIMA Parameters (p, d, q)**")
            p = st.number_input("p (AR order)", 0, 10, 1)
            d = st.number_input("d (Differencing)", 0, 2, 1)
            q = st.number_input("q (MA order)", 0, 10, 1)

            st.markdown("**Seasonal Parameters (P, D, Q, s)**")
            P = st.number_input("P (Seasonal AR)", 0, 5, 1)
            D = st.number_input("D (Seasonal Diff)", 0, 2, 1)
            Q = st.number_input("Q (Seasonal MA)", 0, 5, 1)
            s = st.number_input("s (Season length)", 2, 365, 12)

            order = (p, d, q)
            seasonal_order = (P, D, Q, s)

        elif model_type == "Exponential Smoothing":
            trend = st.selectbox("Trend", [None, 'add', 'mul'])
            seasonal = st.selectbox("Seasonal", [None, 'add', 'mul'])
            seasonal_periods = st.number_input("Seasonal Periods", 2, 365, 12) if seasonal else None

    if st.button("🎯 Fit Model and Forecast", type="primary"):
        with st.spinner(f"Fitting {model_type} model..."):
            try:
                # Fit model
                if model_type in ["ARIMA", "SARIMA"]:
                    if model_type == "Auto ARIMA":
                        st.info("Finding best ARIMA order...")
                        order = auto_arima_order(ts)
                        st.write(f"Best order found: {order}")

                    fit_result = analyzer.fit_arima(ts, order=order, seasonal_order=seasonal_order)

                elif model_type == "Exponential Smoothing":
                    fit_result = analyzer.fit_exponential_smoothing(
                        ts, trend=trend, seasonal=seasonal, seasonal_periods=seasonal_periods
                    )

                if 'error' in fit_result:
                    st.error(fit_result['error'])
                else:
                    st.success(f"✅ {model_type} model fitted successfully!")

                    # Display model metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("AIC", f"{fit_result['aic']:.2f}")
                    with col2:
                        st.metric("BIC", f"{fit_result['bic']:.2f}")
                    with col3:
                        if 'hqic' in fit_result:
                            st.metric("HQIC", f"{fit_result['hqic']:.2f}")

                    # Generate forecast
                    forecast_result = analyzer.forecast(steps=forecast_steps)

                    if 'error' not in forecast_result:
                        st.subheader("Forecast Results")

                        # Plot forecast
                        fig = go.Figure()

                        # Historical data
                        fig.add_trace(go.Scatter(
                            x=ts.index, y=ts.values,
                            mode='lines', name='Historical',
                            line=dict(color='blue')
                        ))

                        # Forecast
                        forecast_index = pd.date_range(
                            start=ts.index[-1] + pd.Timedelta(days=1),
                            periods=forecast_steps,
                            freq=analyzer.frequency if analyzer.frequency else 'D'
                        )
                        forecast_values = list(forecast_result['forecast'].values())

                        fig.add_trace(go.Scatter(
                            x=forecast_index, y=forecast_values,
                            mode='lines', name='Forecast',
                            line=dict(color='red', dash='dash')
                        ))

                        # Confidence intervals (if available)
                        if 'lower_bound' in forecast_result:
                            lower = list(forecast_result['lower_bound'].values())
                            upper = list(forecast_result['upper_bound'].values())

                            fig.add_trace(go.Scatter(
                                x=forecast_index, y=upper,
                                mode='lines', name='Upper Bound',
                                line=dict(width=0),
                                showlegend=False
                            ))

                            fig.add_trace(go.Scatter(
                                x=forecast_index, y=lower,
                                mode='lines', name='Lower Bound',
                                fill='tonexty',
                                line=dict(width=0),
                                showlegend=False
                            ))

                        fig.update_layout(
                            title=f"{model_type} Forecast",
                            xaxis_title="Date",
                            yaxis_title=value_column,
                            hovermode='x unified'
                        )
                        st.plotly_chart(fig, use_container_width=True)

                        # Forecast table
                        forecast_df = pd.DataFrame({
                            'Date': forecast_index,
                            'Forecast': forecast_values
                        })
                        if 'lower_bound' in forecast_result:
                            forecast_df['Lower Bound'] = lower
                            forecast_df['Upper Bound'] = upper

                        st.dataframe(forecast_df, use_container_width=True)

            except Exception as e:
                st.error(f"Error during forecasting: {str(e)}")
                logger.error(f"Forecasting error: {e}")

# ========================================
# TAB 5: Anomaly Detection
# ========================================
with tab5:
    st.header("Anomaly Detection")

    detection_method = st.selectbox(
        "Detection Method",
        ["IQR Method", "Z-Score", "Isolation Forest"]
    )

    col1, col2 = st.columns([2, 1])

    with col2:
        if detection_method == "IQR Method":
            threshold = st.slider("IQR Multiplier", 1.0, 3.0, 1.5, 0.1)
        elif detection_method == "Z-Score":
            threshold = st.slider("Z-Score Threshold", 2.0, 4.0, 3.0, 0.1)
        else:  # Isolation Forest
            threshold = st.slider("Contamination", 0.01, 0.5, 0.1, 0.01)

    if st.button("🔍 Detect Anomalies", type="primary"):
        with st.spinner("Detecting anomalies..."):
            try:
                method_map = {
                    "IQR Method": "iqr",
                    "Z-Score": "zscore",
                    "Isolation Forest": "isolation_forest"
                }

                result = analyzer.detect_anomalies(
                    ts,
                    method=method_map[detection_method],
                    threshold=threshold
                )

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Anomalies Detected", result['n_anomalies'])
                with col2:
                    st.metric("Anomaly Percentage", f"{result['anomaly_percentage']:.2f}%")

                if result['n_anomalies'] > 0:
                    # Plot time series with anomalies
                    fig = go.Figure()

                    # Normal points
                    fig.add_trace(go.Scatter(
                        x=ts.index, y=ts.values,
                        mode='lines', name='Normal',
                        line=dict(color='blue')
                    ))

                    # Anomalies
                    anomaly_dates = pd.to_datetime(result['anomaly_dates'])
                    anomaly_values = list(result['anomaly_values'].values())

                    fig.add_trace(go.Scatter(
                        x=anomaly_dates, y=anomaly_values,
                        mode='markers', name='Anomalies',
                        marker=dict(color='red', size=10, symbol='x')
                    ))

                    fig.update_layout(
                        title=f"Anomalies Detected using {detection_method}",
                        xaxis_title="Date",
                        yaxis_title=value_column,
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # Anomaly table
                    st.subheader("Detected Anomalies")
                    anomaly_df = pd.DataFrame({
                        'Date': result['anomaly_dates'],
                        'Value': anomaly_values
                    })
                    st.dataframe(anomaly_df, use_container_width=True)
                else:
                    st.info("No anomalies detected with the current settings.")

            except Exception as e:
                st.error(f"Error detecting anomalies: {str(e)}")
                logger.error(f"Anomaly detection error: {e}")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p>📈 Powered by VexaAI | Advanced Time Series Analytics</p>
</div>
""", unsafe_allow_html=True)
