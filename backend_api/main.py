# backend_api/main.py

"""
VexaAI Backend API - FastAPI Wrapper
Connects Next.js frontend to existing Python backend
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import pandas as pd
import sys
from pathlib import Path
import jwt
import os
from datetime import datetime, timedelta
import tempfile

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.auth import SupabaseAuthManager
from core.ml_engine import preprocess_and_save, generate_sql_query, execute_query, interpret_results
from core.ai_client import get_unified_client
from core.data_analysis import DataAnalyzer
from database.supabase_manager import get_supabase_manager
from utils.logger import get_logger, audit_logger

logger = get_logger(__name__)

app = FastAPI(title="VexaAI API", version="1.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"

# Initialize managers
auth_manager = SupabaseAuthManager()
db_manager = get_supabase_manager()

# Initialize AI client with available API keys from environment
def initialize_ai_client():
    """Initialize AI client with available API keys from environment"""
    client = get_unified_client()

    # Try to initialize available providers in priority order: XAI > GROQ > GEMINI
    xai_key = os.getenv("XAI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")

    providers_initialized = []

    # Priority 1: xAI (Grok)
    if xai_key:
        try:
            client.add_client("xai", xai_key)
            providers_initialized.append("xai")
            logger.info("✅ xAI (Grok) client initialized from environment")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize xAI: {e}")

    # Priority 2: Groq
    if groq_key:
        try:
            client.add_client("groq", groq_key)
            providers_initialized.append("groq")
            logger.info("✅ Groq client initialized from environment")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize Groq: {e}")

    # Priority 3: Gemini
    if gemini_key:
        try:
            client.add_client("gemini", gemini_key)
            providers_initialized.append("gemini")
            logger.info("✅ Gemini client initialized from environment")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize Gemini: {e}")

    # Set active provider (prefer XAI > Groq > Gemini)
    if providers_initialized:
        active = providers_initialized[0]  # First available
        client.set_active_provider(active)
        logger.info(f"✅ Active AI provider set to: {active}")
    else:
        logger.warning("⚠️ No AI providers configured. AI features will not work.")

    return client

# Initialize AI client on startup
ai_client = initialize_ai_client()

# ==================== MODELS ====================

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    full_name: str

class AIQueryRequest(BaseModel):
    query: str
    dataset_id: str

class AIConfigRequest(BaseModel):
    provider: str  # xai, groq, gemini
    api_key: str
    model: str

# ==================== AUTH HELPERS ====================

def create_token(username: str, is_admin: bool = False) -> str:
    """Create JWT token"""
    payload = {
        "username": username,
        "is_admin": is_admin,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """Verify JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ==================== AUTH ENDPOINTS ====================

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """Login endpoint"""
    try:
        success, message = auth_manager.verify_credentials(request.username, request.password)
        
        if success:
            user = auth_manager.get_user(request.username)
            is_admin = user.get('role') == 'admin' if user else False
            
            token = create_token(request.username, is_admin)
            
            return {
                "success": True,
                "token": token,
                "user": {
                    "username": request.username,
                    "email": user.get('email'),
                    "full_name": user.get('full_name'),
                    "is_admin": is_admin
                }
            }
        else:
            raise HTTPException(status_code=401, detail=message)
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/register")
async def register(request: RegisterRequest):
    """Register endpoint"""
    try:
        success, message = auth_manager.register_user(
            request.username,
            request.email,
            request.password,
            request.full_name
        )
        
        if success:
            return {"success": True, "message": message}
        else:
            raise HTTPException(status_code=400, detail=message)
            
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/auth/me")
async def get_current_user(payload: Dict = Depends(verify_token)):
    """Get current user info"""
    try:
        user = auth_manager.get_user(payload['username'])
        return {
            "username": payload['username'],
            "email": user.get('email'),
            "full_name": user.get('full_name'),
            "is_admin": payload.get('is_admin', False)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== DATA UPLOAD ====================

@app.post("/api/data/upload")
async def upload_data(
    file: UploadFile = File(...),
    dataset_name: str = Form(...),
    payload: Dict = Depends(verify_token)
):
    """Upload dataset"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # Read file directly with pandas
        if file.filename.endswith('.csv'):
            df = pd.read_csv(tmp_path, encoding='utf-8', na_values=['NA', 'N/A', 'missing'])
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(tmp_path, na_values=['NA', 'N/A', 'missing'])
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload CSV or Excel file")

        # Basic preprocessing
        df.columns = (
            df.columns.astype(str).str.strip()
            .str.replace(' ', '_')
            .str.replace('[^A-Za-z0-9_]', '', regex=True)
        )

        # Get file stats
        import os
        file_size = os.path.getsize(tmp_path)

        # Get column info
        column_info = {}
        for col in df.columns:
            column_info[col] = {
                "dtype": str(df[col].dtype),
                "non_null": int(df[col].count()),
                "null": int(df[col].isnull().sum())
            }

        # Save full dataset to Supabase
        # Store full data in metadata (Supabase JSONB can handle large data)
        dataset_id = db_manager.save_dataset(
            user_id=payload['username'],
            dataset_name=dataset_name,
            file_name=file.filename,
            file_size=file_size,
            rows=len(df),
            columns=len(df.columns),
            column_info=column_info,
            metadata={
                "original_filename": file.filename,
                "data": df.to_dict('records'),  # Store full dataset
                "columns": df.columns.tolist(),
                "dtypes": df.dtypes.astype(str).to_dict()
            }
        )

        if dataset_id:
            return {
                "success": True,
                "message": "Dataset uploaded successfully",
                "dataset": {
                    "id": dataset_id,
                    "name": dataset_name,
                    "rows": len(df),
                    "columns": len(df.columns),
                    "filename": file.filename,
                    "preview": df.head(5).to_dict('records')
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to save dataset")
            
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup
        if 'tmp_path' in locals():
            os.unlink(tmp_path)

# ==================== DATASETS ====================

@app.get("/api/data/datasets")
async def get_datasets(payload: Dict = Depends(verify_token)):
    """Get user datasets"""
    try:
        datasets = db_manager.get_user_datasets(payload['username'])
        # Transform datasets to match frontend expectations
        transformed_datasets = []
        for ds in datasets:
            transformed_datasets.append({
                "id": ds.get('id'),
                "dataset_name": ds.get('dataset_name'),
                "file_name": ds.get('file_name'),
                "row_count": ds.get('rows'),  # Frontend expects row_count
                "column_count": ds.get('columns'),  # Frontend expects column_count
                "file_size": ds.get('file_size'),
                "created_at": ds.get('created_at'),
                "column_info": ds.get('column_info', {})
            })
        return {"datasets": transformed_datasets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/dataset/{dataset_id}")
async def get_dataset(dataset_id: str, payload: Dict = Depends(verify_token)):
    """Get dataset details with full data"""
    try:
        dataset = db_manager.get_dataset_by_id(dataset_id)

        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        metadata = dataset.get('metadata', {})

        # Return dataset with full data
        return {
            "id": dataset.get('id'),
            "name": dataset.get('dataset_name'),
            "filename": dataset.get('file_name'),
            "rows": dataset.get('rows'),
            "columns": dataset.get('columns'),
            "column_info": dataset.get('column_info', {}),
            "created_at": dataset.get('created_at'),
            "file_size": dataset.get('file_size'),
            "data": metadata.get('data', []),  # Full dataset
            "column_names": metadata.get('columns', []),
            "dtypes": metadata.get('dtypes', {})
        }

    except Exception as e:
        logger.error(f"Error loading dataset: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== AI CONFIGURATION ====================

@app.get("/api/ai/status")
async def get_ai_status(payload: Dict = Depends(verify_token)):
    """Check if AI is already configured from environment"""
    try:
        client = get_unified_client()
        providers = client.get_available_providers()

        return {
            "configured": len(providers) > 0,
            "active_provider": client.active_provider,
            "active_model": client.active_model,
            "available_providers": providers
        }
    except Exception as e:
        logger.error(f"AI status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/configure")
async def configure_ai(request: AIConfigRequest, payload: Dict = Depends(verify_token)):
    """Configure AI provider"""
    try:
        client = get_unified_client()
        
        # Add client
        client.add_client(request.provider, request.api_key)
        client.set_active_provider(request.provider, request.model)
        
        return {
            "success": True,
            "provider": request.provider,
            "model": request.model
        }
        
    except Exception as e:
        logger.error(f"AI config error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== AI QUERIES ====================

@app.post("/api/ai/query")
async def ai_query(request: AIQueryRequest, payload: Dict = Depends(verify_token)):
    """Process AI query"""
    try:
        # Load dataset
        dataset = db_manager.get_dataset_by_id(request.dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        # Get data from metadata
        data = dataset.get('metadata', {}).get('data', [])
        df = pd.DataFrame(data)
        
        # Get AI client
        client = get_unified_client()
        
        # Generate SQL
        sql_query = generate_sql_query(
            request.query,
            df.columns.tolist(),
            "data",
            client
        )
        
        # Execute query
        results = execute_query(df, sql_query)
        
        # Interpret results
        interpretation = interpret_results(
            request.query,
            sql_query,
            results,
            client
        )
        
        # Log activity
        audit_logger.log_user_action(
            payload['username'],
            "ai_query",
            f"Query: {request.query}"
        )
        
        return {
            "success": True,
            "sql": sql_query,
            "results": results.to_dict('records'),
            "interpretation": interpretation,
            "rows": len(results),
            "columns": len(results.columns)
        }
        
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== STATISTICS ====================

@app.post("/api/stats/ttest")
async def perform_ttest(
    dataset_id: str = Form(...),
    column: str = Form(...),
    group_column: str = Form(...),
    payload: Dict = Depends(verify_token)
):
    """Perform T-test"""
    try:
        dataset = db_manager.get_dataset_by_id(dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        # Get data from metadata
        data = dataset.get('metadata', {}).get('data', [])
        df = pd.DataFrame(data)
        
        analyzer = DataAnalyzer(df)
        result = analyzer.perform_t_test(column, group_column)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ADMIN ====================

@app.get("/api/admin/users")
async def get_all_users(payload: Dict = Depends(verify_token)):
    """Get all users (admin only)"""
    if not payload.get('is_admin'):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        users = auth_manager.get_all_users()
        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== HEALTH CHECK ====================

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected" if db_manager.is_connected() else "disconnected"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
# ==================== DATA CLEANING ====================

@app.post("/api/data/clean/missing")
async def handle_missing_data(
    dataset_id: str = Form(...),
    strategy: str = Form(...),
    columns: List[str] = Form(...),
    fill_value: Optional[str] = Form(None),
    payload: Dict = Depends(verify_token)
):
    """Handle missing data"""
    try:
        dataset = db_manager.get_dataset_by_id(dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        # Get data
        data = dataset.get('metadata', {}).get('data', [])
        df = pd.DataFrame(data)
        
        # Apply strategy
        from core.data_cleaning import DataCleaner
        cleaner = DataCleaner(df)
        
        if strategy == "drop_rows":
            df = cleaner.handle_missing(method="drop_rows", columns=columns)
        elif strategy == "drop_columns":
            df = cleaner.handle_missing(method="drop_columns", columns=columns)
        elif strategy == "fill_mean":
            df = cleaner.handle_missing(method="mean", columns=columns)
        elif strategy == "fill_median":
            df = cleaner.handle_missing(method="median", columns=columns)
        elif strategy == "fill_mode":
            df = cleaner.handle_missing(method="mode", columns=columns)
        elif strategy == "fill_constant":
            df = cleaner.handle_missing(method="constant", columns=columns, fill_value=fill_value)
        elif strategy == "forward_fill":
            df = cleaner.handle_missing(method="ffill", columns=columns)
        elif strategy == "backward_fill":
            df = cleaner.handle_missing(method="bfill", columns=columns)
        elif strategy == "interpolate":
            df = cleaner.handle_missing(method="interpolate", columns=columns)
        
        return {
            "success": True,
            "data": df.to_dict('records'),
            "rows": len(df),
            "columns": len(df.columns)
        }
    except Exception as e:
        logger.error(f"Error handling missing data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/data/clean/duplicates")
async def remove_duplicates(
    dataset_id: str = Form(...),
    payload: Dict = Depends(verify_token)
):
    """Remove duplicate rows"""
    try:
        dataset = db_manager.get_dataset_by_id(dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        data = dataset.get('metadata', {}).get('data', [])
        df = pd.DataFrame(data)
        
        df = df.drop_duplicates()
        
        return {
            "success": True,
            "data": df.to_dict('records'),
            "rows": len(df)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/data/clean/outliers")
async def remove_outliers(
    dataset_id: str = Form(...),
    columns: List[str] = Form(...),
    method: str = Form("iqr"),
    payload: Dict = Depends(verify_token)
):
    """Remove outliers"""
    try:
        dataset = db_manager.get_dataset_by_id(dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        data = dataset.get('metadata', {}).get('data', [])
        df = pd.DataFrame(data)
        
        from core.data_cleaning import DataCleaner
        cleaner = DataCleaner(df)
        df = cleaner.remove_outliers(columns=columns, method=method)
        
        return {
            "success": True,
            "data": df.to_dict('records'),
            "rows": len(df)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/download/{dataset_id}")
async def download_dataset(dataset_id: str, payload: Dict = Depends(verify_token)):
    """Download cleaned dataset as CSV"""
    try:
        dataset = db_manager.get_dataset_by_id(dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        data = dataset.get('metadata', {}).get('data', [])
        df = pd.DataFrame(data)

        # Convert to CSV
        csv_data = df.to_csv(index=False)

        from fastapi.responses import Response
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={dataset.get('file_name', 'dataset.csv')}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== PROFESSIONAL EDA ENDPOINTS ====================

@app.get("/api/eda/profile/{dataset_id}")
async def get_data_profile(dataset_id: str, payload: Dict = Depends(verify_token)):
    """Get comprehensive data profiling (like pandas-profiling)"""
    try:
        dataset = db_manager.get_dataset_by_id(dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        data = dataset.get('metadata', {}).get('data', [])
        df = pd.DataFrame(data)
        analyzer = DataAnalyzer(df)

        # Generate comprehensive summary
        summary = analyzer.generate_summary_statistics()

        # Add shape info
        summary['shape'] = {"rows": len(df), "columns": len(df.columns)}
        summary['columns'] = df.columns.tolist()
        summary['numeric_columns'] = analyzer.numeric_cols
        summary['categorical_columns'] = analyzer.categorical_cols

        # Add duplicate info
        summary['duplicates'] = {
            "count": int(df.duplicated().sum()),
            "percentage": float(df.duplicated().sum() / len(df) * 100) if len(df) > 0 else 0
        }

        return summary

    except Exception as e:
        logger.error(f"Error profiling data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/eda/correlation")
async def calculate_correlation(
    dataset_id: str = Form(...),
    method: str = Form("pearson"),
    payload: Dict = Depends(verify_token)
):
    """Calculate correlation matrix"""
    try:
        dataset = db_manager.get_dataset_by_id(dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        data = dataset.get('metadata', {}).get('data', [])
        df = pd.DataFrame(data)
        analyzer = DataAnalyzer(df)

        corr_matrix = analyzer.calculate_correlations(method=method)

        return {
            "correlation_matrix": corr_matrix.to_dict() if not corr_matrix.empty else {},
            "method": method,
            "columns": corr_matrix.columns.tolist() if not corr_matrix.empty else []
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/eda/distribution")
async def get_distribution(
    dataset_id: str = Form(...),
    column: str = Form(...),
    bins: int = Form(30),
    payload: Dict = Depends(verify_token)
):
    """Get distribution data for a column"""
    try:
        dataset = db_manager.get_dataset_by_id(dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        data = dataset.get('metadata', {}).get('data', [])
        df = pd.DataFrame(data)

        col_data = df[column].dropna()

        # Check if numeric or categorical
        if pd.api.types.is_numeric_dtype(col_data):
            # Histogram data
            hist, bin_edges = np.histogram(col_data, bins=bins)

            return {
                "type": "numeric",
                "histogram": {
                    "counts": hist.tolist(),
                    "bin_edges": bin_edges.tolist()
                },
                "stats": {
                    "mean": float(col_data.mean()),
                    "median": float(col_data.median()),
                    "std": float(col_data.std()),
                    "min": float(col_data.min()),
                    "max": float(col_data.max()),
                    "q25": float(col_data.quantile(0.25)),
                    "q75": float(col_data.quantile(0.75)),
                    "skewness": float(col_data.skew()),
                    "kurtosis": float(col_data.kurtosis())
                }
            }
        else:
            # Value counts for categorical
            value_counts = col_data.value_counts().head(20)

            return {
                "type": "categorical",
                "value_counts": value_counts.to_dict(),
                "unique_count": int(col_data.nunique()),
                "mode": str(col_data.mode()[0]) if len(col_data.mode()) > 0 else None
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/eda/outliers")
async def detect_outliers_endpoint(
    dataset_id: str = Form(...),
    column: str = Form(...),
    method: str = Form("iqr"),
    payload: Dict = Depends(verify_token)
):
    """Detect outliers in a column"""
    try:
        dataset = db_manager.get_dataset_by_id(dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        data = dataset.get('metadata', {}).get('data', [])
        df = pd.DataFrame(data)
        analyzer = DataAnalyzer(df)

        result = analyzer.detect_outliers(column, method)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/eda/normality")
async def test_normality_endpoint(
    dataset_id: str = Form(...),
    columns: str = Form(None),  # Comma-separated column names
    payload: Dict = Depends(verify_token)
):
    """Test normality of columns"""
    try:
        dataset = db_manager.get_dataset_by_id(dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        data = dataset.get('metadata', {}).get('data', [])
        df = pd.DataFrame(data)
        analyzer = DataAnalyzer(df)

        col_list = columns.split(',') if columns else None
        results = analyzer.test_normality(col_list)

        return {"normality_tests": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/eda/anova")
async def perform_anova_endpoint(
    dataset_id: str = Form(...),
    column: str = Form(...),
    group_column: str = Form(...),
    payload: Dict = Depends(verify_token)
):
    """Perform ANOVA test"""
    try:
        dataset = db_manager.get_dataset_by_id(dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        data = dataset.get('metadata', {}).get('data', [])
        df = pd.DataFrame(data)
        analyzer = DataAnalyzer(df)

        result = analyzer.perform_anova(column, group_column)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/eda/chi-square")
async def perform_chi_square_endpoint(
    dataset_id: str = Form(...),
    column1: str = Form(...),
    column2: str = Form(...),
    payload: Dict = Depends(verify_token)
):
    """Perform chi-square test"""
    try:
        dataset = db_manager.get_dataset_by_id(dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        data = dataset.get('metadata', {}).get('data', [])
        df = pd.DataFrame(data)
        analyzer = DataAnalyzer(df)

        result = analyzer.perform_chi_square(column1, column2)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/eda/insights/{dataset_id}")
async def get_automated_insights(dataset_id: str, payload: Dict = Depends(verify_token)):
    """Generate automated insights about the dataset"""
    try:
        dataset = db_manager.get_dataset_by_id(dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        data = dataset.get('metadata', {}).get('data', [])
        df = pd.DataFrame(data)
        analyzer = DataAnalyzer(df)

        insights = []

        # Missing data insights
        missing = df.isnull().sum()
        high_missing = missing[missing > len(df) * 0.1]  # > 10% missing
        if len(high_missing) > 0:
            insights.append({
                "type": "warning",
                "category": "data_quality",
                "title": "High Missing Data",
                "message": f"{len(high_missing)} columns have >10% missing values",
                "details": high_missing.to_dict()
            })

        # Duplicate insights
        dup_count = df.duplicated().sum()
        if dup_count > 0:
            insights.append({
                "type": "warning",
                "category": "data_quality",
                "title": "Duplicate Rows",
                "message": f"Found {dup_count} duplicate rows ({dup_count/len(df)*100:.2f}%)"
            })

        # High cardinality categorical features
        for col in analyzer.categorical_cols:
            unique_ratio = df[col].nunique() / len(df)
            if unique_ratio > 0.9:
                insights.append({
                    "type": "info",
                    "category": "feature_engineering",
                    "title": "High Cardinality Feature",
                    "message": f"Column '{col}' has {df[col].nunique()} unique values ({unique_ratio*100:.1f}% of rows)",
                    "suggestion": "Consider grouping rare categories or using embeddings"
                })

        # Highly correlated features
        if len(analyzer.numeric_cols) >= 2:
            corr_matrix = analyzer.calculate_correlations()
            high_corr = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    if abs(corr_matrix.iloc[i, j]) > 0.9:
                        high_corr.append({
                            "col1": corr_matrix.columns[i],
                            "col2": corr_matrix.columns[j],
                            "correlation": float(corr_matrix.iloc[i, j])
                        })

            if high_corr:
                insights.append({
                    "type": "warning",
                    "category": "multicollinearity",
                    "title": "Highly Correlated Features",
                    "message": f"Found {len(high_corr)} pairs of highly correlated features (|r| > 0.9)",
                    "details": high_corr,
                    "suggestion": "Consider removing redundant features"
                })

        # Imbalanced target (if last column is categorical and small unique values)
        if len(analyzer.categorical_cols) > 0:
            last_col = df.columns[-1]
            if last_col in analyzer.categorical_cols and df[last_col].nunique() <= 10:
                value_counts = df[last_col].value_counts()
                imbalance_ratio = value_counts.max() / value_counts.min()
                if imbalance_ratio > 3:
                    insights.append({
                        "type": "warning",
                        "category": "class_imbalance",
                        "title": "Imbalanced Target Variable",
                        "message": f"Column '{last_col}' has imbalanced distribution (ratio: {imbalance_ratio:.1f}:1)",
                        "details": value_counts.to_dict(),
                        "suggestion": "Consider using SMOTE, class weights, or stratified sampling"
                    })

        return {"insights": insights, "total_insights": len(insights)}

    except Exception as e:
        logger.error(f"Error generating insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))
