"""
Time Series Analysis Module
Provides comprehensive time series analysis including decomposition, forecasting, and anomaly detection.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Statistical models
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller, kpss, acf, pacf
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.vector_ar.var_model import VAR
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# Additional analysis
from scipy import stats
from sklearn.metrics import mean_squared_error, mean_absolute_error, mean_absolute_percentage_error


class TimeSeriesAnalyzer:
    """
    Comprehensive time series analysis and forecasting.
    """

    def __init__(self):
        self.model = None
        self.data = None
        self.date_column = None
        self.value_column = None
        self.frequency = None

    def prepare_time_series(
        self,
        df: pd.DataFrame,
        date_column: str,
        value_column: str,
        frequency: Optional[str] = None
    ) -> pd.Series:
        """
        Prepare time series data.

        Args:
            df: Input DataFrame
            date_column: Name of date column
            value_column: Name of value column
            frequency: Frequency of time series ('D', 'W', 'M', 'Q', 'Y', etc.)

        Returns:
            Time series as pandas Series with DatetimeIndex
        """
        # Convert date column to datetime
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])

        # Sort by date
        df = df.sort_values(date_column)

        # Set date as index
        ts = df.set_index(date_column)[value_column]

        # Infer frequency if not provided
        if frequency is None:
            try:
                ts = ts.asfreq(pd.infer_freq(ts.index))
                self.frequency = ts.index.freq
            except:
                # If inference fails, use daily
                self.frequency = 'D'
        else:
            ts = ts.asfreq(frequency)
            self.frequency = frequency

        # Handle missing values with interpolation
        ts = ts.interpolate(method='linear')

        self.data = ts
        self.date_column = date_column
        self.value_column = value_column

        return ts

    def analyze_stationarity(self, ts: Optional[pd.Series] = None) -> Dict[str, Any]:
        """
        Test for stationarity using ADF and KPSS tests.

        Args:
            ts: Time series (uses self.data if None)

        Returns:
            Stationarity test results
        """
        if ts is None:
            ts = self.data

        if ts is None:
            raise ValueError("No time series data available")

        # Augmented Dickey-Fuller test
        adf_result = adfuller(ts.dropna())

        # KPSS test
        kpss_result = kpss(ts.dropna())

        results = {
            'adf_test': {
                'statistic': float(adf_result[0]),
                'p_value': float(adf_result[1]),
                'critical_values': {k: float(v) for k, v in adf_result[4].items()},
                'is_stationary': adf_result[1] < 0.05  # Reject null hypothesis
            },
            'kpss_test': {
                'statistic': float(kpss_result[0]),
                'p_value': float(kpss_result[1]),
                'critical_values': {k: float(v) for k, v in kpss_result[3].items()},
                'is_stationary': kpss_result[1] > 0.05  # Fail to reject null hypothesis
            },
            'recommendation': ''
        }

        # Provide recommendation
        if results['adf_test']['is_stationary'] and results['kpss_test']['is_stationary']:
            results['recommendation'] = 'Series is stationary. No differencing needed.'
        elif not results['adf_test']['is_stationary']:
            results['recommendation'] = 'Series is non-stationary. Consider differencing or transformation.'
        else:
            results['recommendation'] = 'Mixed results. Consider visual inspection and additional tests.'

        return results

    def decompose(
        self,
        ts: Optional[pd.Series] = None,
        model: str = 'additive',
        period: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Decompose time series into trend, seasonal, and residual components.

        Args:
            ts: Time series (uses self.data if None)
            model: 'additive' or 'multiplicative'
            period: Seasonal period (auto-detected if None)

        Returns:
            Decomposition components
        """
        if ts is None:
            ts = self.data

        if ts is None:
            raise ValueError("No time series data available")

        # Auto-detect period if not provided
        if period is None:
            freq = ts.index.freq if hasattr(ts.index, 'freq') else None
            if freq == 'D' or freq == 'B':
                period = 7  # Weekly seasonality
            elif freq == 'W':
                period = 52  # Yearly seasonality
            elif freq == 'M':
                period = 12  # Yearly seasonality
            elif freq == 'Q':
                period = 4  # Yearly seasonality
            else:
                period = 12  # Default

        # Perform decomposition
        try:
            decomposition = seasonal_decompose(
                ts.dropna(),
                model=model,
                period=period,
                extrapolate_trend='freq'
            )

            return {
                'trend': decomposition.trend.to_dict(),
                'seasonal': decomposition.seasonal.to_dict(),
                'residual': decomposition.resid.to_dict(),
                'observed': ts.to_dict(),
                'model': model,
                'period': period,
                'seasonal_strength': float(1 - (decomposition.resid.var() / (decomposition.resid.var() + decomposition.seasonal.var()))),
                'trend_strength': float(1 - (decomposition.resid.var() / (decomposition.resid.var() + decomposition.trend.var())))
            }
        except Exception as e:
            return {'error': f'Decomposition failed: {str(e)}'}

    def autocorrelation_analysis(
        self,
        ts: Optional[pd.Series] = None,
        lags: int = 40
    ) -> Dict[str, Any]:
        """
        Analyze autocorrelation and partial autocorrelation.

        Args:
            ts: Time series (uses self.data if None)
            lags: Number of lags to compute

        Returns:
            ACF and PACF values
        """
        if ts is None:
            ts = self.data

        if ts is None:
            raise ValueError("No time series data available")

        ts_clean = ts.dropna()

        # Compute ACF and PACF
        acf_values = acf(ts_clean, nlags=lags)
        pacf_values = pacf(ts_clean, nlags=lags)

        return {
            'acf': acf_values.tolist(),
            'pacf': pacf_values.tolist(),
            'lags': list(range(lags + 1)),
            'significant_lags_acf': [i for i, val in enumerate(acf_values) if abs(val) > 1.96/np.sqrt(len(ts_clean))],
            'significant_lags_pacf': [i for i, val in enumerate(pacf_values) if abs(val) > 1.96/np.sqrt(len(ts_clean))]
        }

    def fit_arima(
        self,
        ts: Optional[pd.Series] = None,
        order: Tuple[int, int, int] = (1, 1, 1),
        seasonal_order: Optional[Tuple[int, int, int, int]] = None
    ) -> Dict[str, Any]:
        """
        Fit ARIMA or SARIMA model.

        Args:
            ts: Time series (uses self.data if None)
            order: (p, d, q) order for ARIMA
            seasonal_order: (P, D, Q, s) for SARIMA (None = no seasonality)

        Returns:
            Model fit results
        """
        if ts is None:
            ts = self.data

        if ts is None:
            raise ValueError("No time series data available")

        ts_clean = ts.dropna()

        try:
            if seasonal_order is not None:
                # SARIMA model
                model = SARIMAX(
                    ts_clean,
                    order=order,
                    seasonal_order=seasonal_order,
                    enforce_stationarity=False,
                    enforce_invertibility=False
                )
            else:
                # ARIMA model
                model = ARIMA(ts_clean, order=order)

            # Fit model
            self.model = model.fit()

            # Extract results
            results = {
                'model_type': 'SARIMA' if seasonal_order else 'ARIMA',
                'order': order,
                'seasonal_order': seasonal_order,
                'aic': float(self.model.aic),
                'bic': float(self.model.bic),
                'hqic': float(self.model.hqic),
                'parameters': self.model.params.to_dict(),
                'p_values': self.model.pvalues.to_dict(),
                'residuals': self.model.resid.to_dict(),
                'fitted_values': self.model.fittedvalues.to_dict()
            }

            # Residual analysis
            residuals = self.model.resid
            results['residual_analysis'] = {
                'mean': float(residuals.mean()),
                'std': float(residuals.std()),
                'skewness': float(stats.skew(residuals)),
                'kurtosis': float(stats.kurtosis(residuals)),
                'ljung_box_p_value': float(self.model.test_serial_correlation('ljungbox')[0][-1, -1])
            }

            return results

        except Exception as e:
            return {'error': f'ARIMA fitting failed: {str(e)}'}

    def fit_exponential_smoothing(
        self,
        ts: Optional[pd.Series] = None,
        trend: Optional[str] = 'add',
        seasonal: Optional[str] = 'add',
        seasonal_periods: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Fit Exponential Smoothing (Holt-Winters) model.

        Args:
            ts: Time series (uses self.data if None)
            trend: 'add', 'mul', or None
            seasonal: 'add', 'mul', or None
            seasonal_periods: Number of periods in a season

        Returns:
            Model fit results
        """
        if ts is None:
            ts = self.data

        if ts is None:
            raise ValueError("No time series data available")

        ts_clean = ts.dropna()

        try:
            model = ExponentialSmoothing(
                ts_clean,
                trend=trend,
                seasonal=seasonal,
                seasonal_periods=seasonal_periods
            )

            self.model = model.fit()

            return {
                'model_type': 'Exponential Smoothing',
                'trend': trend,
                'seasonal': seasonal,
                'seasonal_periods': seasonal_periods,
                'aic': float(self.model.aic),
                'bic': float(self.model.bic),
                'parameters': {
                    'smoothing_level': float(self.model.params['smoothing_level']),
                    'smoothing_trend': float(self.model.params.get('smoothing_trend', 0)),
                    'smoothing_seasonal': float(self.model.params.get('smoothing_seasonal', 0))
                },
                'fitted_values': self.model.fittedvalues.to_dict()
            }

        except Exception as e:
            return {'error': f'Exponential Smoothing failed: {str(e)}'}

    def forecast(
        self,
        steps: int = 10,
        confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        """
        Generate forecasts using fitted model.

        Args:
            steps: Number of steps ahead to forecast
            confidence_level: Confidence level for prediction intervals

        Returns:
            Forecast results with prediction intervals
        """
        if self.model is None:
            raise ValueError("No model fitted. Call fit_arima() or fit_exponential_smoothing() first.")

        try:
            # Generate forecast
            if hasattr(self.model, 'get_forecast'):
                # ARIMA/SARIMA
                forecast_result = self.model.get_forecast(steps=steps)
                forecast_values = forecast_result.predicted_mean
                conf_int = forecast_result.conf_int(alpha=1-confidence_level)

                return {
                    'forecast': forecast_values.to_dict(),
                    'lower_bound': conf_int.iloc[:, 0].to_dict(),
                    'upper_bound': conf_int.iloc[:, 1].to_dict(),
                    'confidence_level': confidence_level,
                    'steps': steps
                }
            else:
                # Exponential Smoothing
                forecast_values = self.model.forecast(steps=steps)

                return {
                    'forecast': forecast_values.to_dict(),
                    'steps': steps,
                    'note': 'Confidence intervals not available for this model type'
                }

        except Exception as e:
            return {'error': f'Forecasting failed: {str(e)}'}

    def cross_validate_forecast(
        self,
        ts: Optional[pd.Series] = None,
        order: Tuple[int, int, int] = (1, 1, 1),
        test_size: int = 10,
        window_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Cross-validate forecasting model using rolling window.

        Args:
            ts: Time series (uses self.data if None)
            order: ARIMA order
            test_size: Number of observations for testing
            window_size: Size of training window (None = expanding window)

        Returns:
            Cross-validation results
        """
        if ts is None:
            ts = self.data

        if ts is None:
            raise ValueError("No time series data available")

        ts_clean = ts.dropna()

        # Split into train and test
        train = ts_clean[:-test_size]
        test = ts_clean[-test_size:]

        predictions = []
        actuals = []

        for i in range(len(test)):
            # Define training data
            if window_size is None:
                # Expanding window
                train_data = ts_clean[:len(train) + i]
            else:
                # Rolling window
                train_data = ts_clean[max(0, len(train) + i - window_size):len(train) + i]

            try:
                # Fit model
                model = ARIMA(train_data, order=order)
                model_fit = model.fit()

                # Forecast one step ahead
                forecast = model_fit.forecast(steps=1)
                predictions.append(float(forecast.iloc[0]))
                actuals.append(float(test.iloc[i]))

            except Exception as e:
                continue

        if len(predictions) == 0:
            return {'error': 'Cross-validation failed'}

        # Calculate metrics
        predictions = np.array(predictions)
        actuals = np.array(actuals)

        mse = mean_squared_error(actuals, predictions)
        mae = mean_absolute_error(actuals, predictions)
        rmse = np.sqrt(mse)

        # MAPE (avoid division by zero)
        mape = mean_absolute_percentage_error(actuals, predictions) if (actuals != 0).all() else None

        return {
            'predictions': predictions.tolist(),
            'actuals': actuals.tolist(),
            'metrics': {
                'mse': float(mse),
                'rmse': float(rmse),
                'mae': float(mae),
                'mape': float(mape) if mape is not None else None
            },
            'test_size': len(predictions),
            'window_type': 'expanding' if window_size is None else 'rolling'
        }

    def detect_anomalies(
        self,
        ts: Optional[pd.Series] = None,
        method: str = 'iqr',
        threshold: float = 1.5
    ) -> Dict[str, Any]:
        """
        Detect anomalies in time series.

        Args:
            ts: Time series (uses self.data if None)
            method: 'iqr', 'zscore', or 'isolation_forest'
            threshold: Threshold for anomaly detection

        Returns:
            Anomaly detection results
        """
        if ts is None:
            ts = self.data

        if ts is None:
            raise ValueError("No time series data available")

        ts_clean = ts.dropna()
        anomalies = pd.Series(False, index=ts_clean.index)

        if method == 'iqr':
            Q1 = ts_clean.quantile(0.25)
            Q3 = ts_clean.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            anomalies = (ts_clean < lower_bound) | (ts_clean > upper_bound)

        elif method == 'zscore':
            z_scores = np.abs(stats.zscore(ts_clean))
            anomalies = z_scores > threshold

        elif method == 'isolation_forest':
            from sklearn.ensemble import IsolationForest
            model = IsolationForest(contamination=threshold, random_state=42)
            predictions = model.fit_predict(ts_clean.values.reshape(-1, 1))
            anomalies = predictions == -1

        anomaly_indices = ts_clean.index[anomalies]
        anomaly_values = ts_clean[anomalies]

        return {
            'n_anomalies': int(anomalies.sum()),
            'anomaly_percentage': float(anomalies.sum() / len(ts_clean) * 100),
            'anomaly_dates': [str(d) for d in anomaly_indices],
            'anomaly_values': anomaly_values.to_dict(),
            'method': method,
            'threshold': threshold
        }

    def trend_analysis(
        self,
        ts: Optional[pd.Series] = None
    ) -> Dict[str, Any]:
        """
        Analyze trend in time series.

        Args:
            ts: Time series (uses self.data if None)

        Returns:
            Trend analysis results
        """
        if ts is None:
            ts = self.data

        if ts is None:
            raise ValueError("No time series data available")

        ts_clean = ts.dropna()

        # Linear trend
        X = np.arange(len(ts_clean)).reshape(-1, 1)
        y = ts_clean.values

        from sklearn.linear_model import LinearRegression
        model = LinearRegression()
        model.fit(X, y)

        trend_line = model.predict(X)
        slope = float(model.coef_[0])
        intercept = float(model.intercept_)
        r2 = float(model.score(X, y))

        # Determine trend direction
        if slope > 0:
            trend_direction = 'increasing'
        elif slope < 0:
            trend_direction = 'decreasing'
        else:
            trend_direction = 'stable'

        # Calculate average rate of change
        avg_change = float(ts_clean.diff().mean())

        return {
            'trend_direction': trend_direction,
            'slope': slope,
            'intercept': intercept,
            'r_squared': r2,
            'average_change': avg_change,
            'trend_line': {str(ts_clean.index[i]): float(trend_line[i]) for i in range(len(trend_line))},
            'start_value': float(ts_clean.iloc[0]),
            'end_value': float(ts_clean.iloc[-1]),
            'total_change': float(ts_clean.iloc[-1] - ts_clean.iloc[0]),
            'percent_change': float((ts_clean.iloc[-1] - ts_clean.iloc[0]) / ts_clean.iloc[0] * 100)
        }


def auto_arima_order(ts: pd.Series, max_p: int = 5, max_d: int = 2, max_q: int = 5) -> Tuple[int, int, int]:
    """
    Automatically determine best ARIMA order using AIC.

    Args:
        ts: Time series
        max_p: Maximum AR order
        max_d: Maximum differencing order
        max_q: Maximum MA order

    Returns:
        Best (p, d, q) order
    """
    best_aic = np.inf
    best_order = (0, 0, 0)

    for p in range(max_p + 1):
        for d in range(max_d + 1):
            for q in range(max_q + 1):
                try:
                    model = ARIMA(ts, order=(p, d, q))
                    fitted = model.fit()

                    if fitted.aic < best_aic:
                        best_aic = fitted.aic
                        best_order = (p, d, q)
                except:
                    continue

    return best_order
