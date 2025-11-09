"""
VexaAI Data Analyst - Configuration Settings
Centralized configuration management for the application
Works both locally (.env) and on Streamlit Cloud (secrets)
"""

import os
import streamlit as st
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"
TEMP_DIR = BASE_DIR / "temp"

# Create directories if they don't exist
LOGS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# Application settings
APP_NAME = "VexaAI Data Analyst Pro"
APP_VERSION = "2.0.0"
APP_AUTHOR = "John Evans Okyere"
APP_COMPANY = "VexaAI"

# ==================== HELPER FUNCTION FOR SECRETS ====================
def get_secret(key: str, default: str = "") -> str:
    """
    Get secret from Streamlit secrets (cloud) or environment variables (local)
    This allows the app to work in both environments seamlessly
    """
    try:
        # Try Streamlit secrets first (for cloud deployment)
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    
    # Fall back to environment variables (for local development)
    return os.getenv(key, default)

# ==================== SUPABASE CONFIGURATION ====================
SUPABASE_URL = get_secret("SUPABASE_URL", "")
SUPABASE_KEY = get_secret("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_ROLE_KEY = get_secret("SUPABASE_SERVICE_ROLE_KEY", "")

# xAI Grok Configuration
XAI_BASE_URL = "https://api.x.ai/v1"
XAI_MODELS = [
    "grok-4-fast-reasoning",
    "grok-2-1212",
    "grok-beta",
    "grok-vision-beta"
]
DEFAULT_XAI_MODEL = "grok-4-fast-reasoning"

# Data Processing Configuration
MAX_FILE_SIZE_MB = 200
SUPPORTED_FILE_TYPES = ["csv", "xlsx", "xls"]
MAX_ROWS_PREVIEW = 10
MAX_COLUMNS_DISPLAY = 50

# Data Cleaning Configuration
MISSING_VALUE_STRATEGIES = [
    "drop_rows",
    "drop_columns",
    "fill_mean",
    "fill_median",
    "fill_mode",
    "fill_constant",
    "forward_fill",
    "backward_fill",
    "interpolate"
]

OUTLIER_DETECTION_METHODS = [
    "iqr",
    "z_score",
    "isolation_forest",
    "modified_z_score"
]

ENCODING_METHODS = [
    "label_encoding",
    "one_hot_encoding",
    "ordinal_encoding",
    "target_encoding",
    "frequency_encoding"
]

SCALING_METHODS = [
    "standard_scaler",
    "min_max_scaler",
    "robust_scaler",
    "max_abs_scaler",
    "normalizer"
]

# Feature Engineering Configuration
FEATURE_ENGINEERING_OPERATIONS = [
    "polynomial_features",
    "interaction_features",
    "log_transform",
    "sqrt_transform",
    "binning",
    "date_features"
]

# Visualization Configuration
CHART_TYPES = [
    "histogram",
    "scatter",
    "line",
    "bar",
    "box",
    "violin",
    "heatmap",
    "correlation",
    "pie",
    "area"
]

PLOT_THEME = "plotly_white"
COLOR_SCHEMES = {
    "primary": ["#667eea", "#764ba2"],
    "secondary": ["#f093fb", "#f5576c"],
    "success": ["#4facfe", "#00f2fe"],
    "info": ["#43e97b", "#38f9d7"],
    "warning": ["#fa709a", "#fee140"],
    "danger": ["#ff0844", "#ffb199"]
}

# MLOps Configuration
ENABLE_LOGGING = True
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE_MAX_BYTES = 10485760  # 10MB
LOG_FILE_BACKUP_COUNT = 5

# Database Configuration
DB_TABLES = {
    "users": "users",
    "datasets": "datasets",
    "data_versions": "data_versions",
    "analysis_history": "analysis_history",
    "audit_logs": "audit_logs",
    "data_quality_reports": "data_quality_reports"
}

# Session Configuration
SESSION_TIMEOUT_MINUTES = 60
MAX_CONCURRENT_SESSIONS = 100

# Export Configuration
EXPORT_FORMATS = ["csv", "excel", "parquet", "json", "feather"]
EXPORT_COMPRESSION = ["none", "gzip", "bz2", "zip", "xz"]

# Statistics Configuration
STATISTICAL_TESTS = [
    "t_test",
    "anova",
    "chi_square",
    "correlation_test",
    "normality_test",
    "variance_test"
]

# AutoML Configuration
AUTOML_ENABLED = True
AUTOML_MAX_TIME_MINUTES = 10
AUTOML_METRIC_OPTIONS = [
    "accuracy",
    "precision",
    "recall",
    "f1",
    "roc_auc",
    "rmse",
    "mae",
    "r2"
]

# Cache Configuration
CACHE_TTL_SECONDS = 3600  # 1 hour
ENABLE_CACHING = True

# Security Configuration
PASSWORD_MIN_LENGTH = 8
PASSWORD_REQUIRE_SPECIAL_CHAR = True
PASSWORD_REQUIRE_NUMBER = True
PASSWORD_REQUIRE_UPPERCASE = True
SESSION_COOKIE_SECURE = True

# API Configuration
API_TIMEOUT_SECONDS = 30
API_MAX_RETRIES = 3
API_RETRY_DELAY_SECONDS = 1

# Monitoring Configuration
ENABLE_PERFORMANCE_MONITORING = True
ENABLE_ERROR_TRACKING = True
ENABLE_USER_ANALYTICS = True

# Data Quality Thresholds
DATA_QUALITY_THRESHOLDS = {
    "missing_data_threshold": 0.5,  # 50%
    "duplicate_threshold": 0.1,  # 10%
    "outlier_threshold": 0.05,  # 5%
    "cardinality_threshold": 0.95  # 95%
}

# UI Configuration
PAGE_ICONS = {
    "home": "🏠",
    "upload": "📂",
    "cleaning": "🧹",
    "analysis": "📈",
    "visualization": "📊",
    "dashboard": "🎛️",
    "history": "📁",
    "admin": "🔐",
    "settings": "⚙️"
}

# Feature Flags
FEATURES = {
    "data_versioning": True,
    "collaboration": True,
    "automl": True,
    "advanced_stats": True,
    "data_export": True,
    "api_integration": True,
    "scheduled_reports": False,  # Coming soon
    "real_time_processing": False  # Coming soon
}

def get_config() -> Dict[str, Any]:
    """Get all configuration as dictionary"""
    return {
        "app": {
            "name": APP_NAME,
            "version": APP_VERSION,
            "author": APP_AUTHOR,
            "company": APP_COMPANY
        },
        "supabase": {
            "url": SUPABASE_URL,
            "key": SUPABASE_KEY,
            "service_role_key": SUPABASE_SERVICE_ROLE_KEY
        },
        "xai": {
            "base_url": XAI_BASE_URL,
            "models": XAI_MODELS,
            "default_model": DEFAULT_XAI_MODEL
        },
        "data_processing": {
            "max_file_size_mb": MAX_FILE_SIZE_MB,
            "supported_file_types": SUPPORTED_FILE_TYPES
        },
        "features": FEATURES
    }

def is_feature_enabled(feature_name: str) -> bool:
    """Check if a feature is enabled"""
    return FEATURES.get(feature_name, False)