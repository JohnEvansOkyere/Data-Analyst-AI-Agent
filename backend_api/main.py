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
        
        # Process file
        class TempFile:
            def __init__(self, path, filename):
                self.name = filename
                self._path = path
            def seek(self, pos):
                pass
        
        temp_file = TempFile(tmp_path, file.filename)
        df = preprocess_and_save(temp_file)
        
        # Save to Supabase
        success = db_manager.save_dataset(
            user_id=payload['username'],
            dataset_name=dataset_name,
            dataframe=df,
            file_path=tmp_path
        )
        
        if success:
            datasets = db_manager.get_user_datasets(payload['username'])
            latest = datasets[0] if datasets else None
            
            return {
                "success": True,
                "message": "Dataset uploaded successfully",
                "dataset": {
                    "id": latest['id'],
                    "name": latest['dataset_name'],
                    "rows": latest['row_count'],
                    "columns": latest['column_count']
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
        return {"datasets": datasets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/dataset/{dataset_id}")
async def get_dataset(dataset_id: str, payload: Dict = Depends(verify_token)):
    """Get dataset details"""
    try:
        df = db_manager.load_dataset(dataset_id)
        
        if df is None:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        # Get basic info
        info = {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "preview": df.head(10).to_dict('records')
        }
        
        return info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== AI CONFIGURATION ====================

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
        df = db_manager.load_dataset(request.dataset_id)
        if df is None:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
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
        df = db_manager.load_dataset(dataset_id)
        if df is None:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
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