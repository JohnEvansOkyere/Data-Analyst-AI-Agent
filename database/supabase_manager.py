"""
VexaAI Data Analyst - Supabase Database Integration
Handles all database operations with Supabase
"""

import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import pandas as pd
from supabase import create_client, Client
from config.settings import SUPABASE_URL, SUPABASE_KEY, DB_TABLES
from utils.logger import get_logger

logger = get_logger(__name__)


class SupabaseManager:
    """Manager class for Supabase operations"""
    
    def __init__(self):
        """Initialize Supabase client from environment variables"""
        self.url = SUPABASE_URL
        self.key = SUPABASE_KEY
        self.client: Optional[Client] = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Supabase client"""
        try:
            if self.url and self.key:
                self.client = create_client(self.url, self.key)
                logger.info("✅ Supabase client initialized successfully")
            else:
                logger.warning("⚠️ Supabase credentials not found in environment")
                self.client = None
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase client: {e}")
            self.client = None
    
    def is_connected(self) -> bool:
        """Check if Supabase client is connected"""
        return self.client is not None
    
    # ==================== DATASET OPERATIONS ====================
    
    def save_dataset(
        self,
        user_id: str,
        dataset_name: str,
        file_name: str,
        file_size: int,
        rows: int,
        columns: int,
        column_info: Dict,
        metadata: Optional[Dict] = None
    ) -> Optional[str]:
        """Save dataset metadata to Supabase"""
        try:
            if not self.client:
                logger.warning("Supabase client not initialized")
                return None
            
            data = {
                "user_id": user_id,
                "dataset_name": dataset_name,
                "file_name": file_name,
                "file_size": file_size,
                "rows": rows,
                "columns": columns,
                "column_info": column_info,  # Already a dict, don't JSON stringify
                "metadata": metadata or {},
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Attempting to save dataset: {dataset_name}")
            response = self.client.table("datasets").insert(data).execute()
            
            if response.data and len(response.data) > 0:
                dataset_id = response.data[0]["id"]
                logger.info(f"✅ Dataset saved successfully: {dataset_id}")
                return dataset_id
            else:
                logger.error(f"❌ No data returned from Supabase insert")
                return None
            
        except Exception as e:
            logger.error(f"❌ Error saving dataset: {e}")
            return None
    
    def get_user_datasets(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get all datasets for a user"""
        try:
            if not self.client:
                return []
            
            response = (
                self.client.table("datasets")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"Error getting user datasets: {e}")
            return []
    
    def get_dataset_by_id(self, dataset_id: str) -> Optional[Dict]:
        """Get dataset by ID"""
        try:
            if not self.client:
                return None
            
            response = (
                self.client.table("datasets")
                .select("*")
                .eq("id", dataset_id)
                .single()
                .execute()
            )
            
            return response.data if response.data else None
            
        except Exception as e:
            logger.error(f"Error getting dataset: {e}")
            return None
    
    def delete_dataset(self, dataset_id: str) -> bool:
        """Delete a dataset"""
        try:
            if not self.client:
                return False
            
            self.client.table("datasets").delete().eq("id", dataset_id).execute()
            logger.info(f"Dataset deleted: {dataset_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting dataset: {e}")
            return False
    
    # ==================== DATA VERSION OPERATIONS ====================
    
    def save_data_version(
        self,
        dataset_id: str,
        version_number: int,
        operation_type: str,
        operations_applied: List[str],
        rows_before: int,
        rows_after: int,
        columns_before: int,
        columns_after: int,
        metadata: Optional[Dict] = None
    ) -> Optional[str]:
        """Save a data version"""
        try:
            if not self.client:
                return None
            
            data = {
                "dataset_id": dataset_id,
                "version_number": version_number,
                "operation_type": operation_type,
                "operations_applied": operations_applied,  # Already a list
                "rows_before": rows_before,
                "rows_after": rows_after,
                "columns_before": columns_before,
                "columns_after": columns_after,
                "metadata": metadata or {},
                "created_at": datetime.utcnow().isoformat()
            }
            
            response = self.client.table("data_versions").insert(data).execute()
            
            if response.data and len(response.data) > 0:
                version_id = response.data[0]["id"]
                logger.info(f"✅ Data version saved: {version_id}")
                return version_id
            
            return None
            
        except Exception as e:
            logger.error(f"Error saving data version: {e}")
            return None
    
    def get_dataset_versions(self, dataset_id: str) -> List[Dict]:
        """Get all versions of a dataset"""
        try:
            if not self.client:
                return []
            
            response = (
                self.client.table("data_versions")
                .select("*")
                .eq("dataset_id", dataset_id)
                .order("version_number", desc=True)
                .execute()
            )
            
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"Error getting dataset versions: {e}")
            return []
    
    # ==================== ANALYSIS HISTORY OPERATIONS ====================
    
    def save_analysis(
        self,
        user_id: str,
        dataset_id: str,
        query: str,
        sql_query: str,
        results_preview: str,
        interpretation: str,
        execution_time: float
    ) -> Optional[str]:
        """Save analysis history"""
        try:
            if not self.client:
                return None
            
            data = {
                "user_id": user_id,
                "dataset_id": dataset_id,
                "query": query,
                "sql_query": sql_query,
                "results_preview": results_preview,
                "interpretation": interpretation,
                "execution_time": execution_time,
                "created_at": datetime.utcnow().isoformat()
            }
            
            response = self.client.table("analysis_history").insert(data).execute()
            
            if response.data and len(response.data) > 0:
                analysis_id = response.data[0]["id"]
                logger.info(f"✅ Analysis saved: {analysis_id}")
                return analysis_id
            
            return None
            
        except Exception as e:
            logger.error(f"Error saving analysis: {e}")
            return None
    
    def get_user_analysis_history(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get user's analysis history"""
        try:
            if not self.client:
                return []
            
            response = (
                self.client.table("analysis_history")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"Error getting analysis history: {e}")
            return []
    
    # ==================== AUDIT LOG OPERATIONS ====================
    
    def log_user_activity(
        self,
        user_id: str,
        activity_type: str,
        description: str,
        metadata: Optional[Dict] = None
    ) -> Optional[str]:
        """Log user activity"""
        try:
            if not self.client:
                return None
            
            data = {
                "user_id": user_id,
                "activity_type": activity_type,
                "description": description,
                "metadata": metadata or {},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            response = self.client.table("audit_logs").insert(data).execute()
            
            if response.data and len(response.data) > 0:
                log_id = response.data[0]["id"]
                return log_id
            
            return None
            
        except Exception as e:
            logger.error(f"Error logging user activity: {e}")
            return None
    
    def get_user_activity_logs(self, user_id: str, limit: int = 100) -> List[Dict]:
        """Get user activity logs"""
        try:
            if not self.client:
                return []
            
            response = (
                self.client.table("audit_logs")
                .select("*")
                .eq("user_id", user_id)
                .order("timestamp", desc=True)
                .limit(limit)
                .execute()
            )
            
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"Error getting activity logs: {e}")
            return []
    
    # ==================== DATA QUALITY REPORTS ====================
    
    def save_data_quality_report(
        self,
        dataset_id: str,
        report_data: Dict,
        quality_score: float
    ) -> Optional[str]:
        """Save data quality report"""
        try:
            if not self.client:
                return None
            
            data = {
                "dataset_id": dataset_id,
                "report_data": report_data,  # Already a dict
                "quality_score": quality_score,
                "created_at": datetime.utcnow().isoformat()
            }
            
            response = self.client.table("data_quality_reports").insert(data).execute()
            
            if response.data and len(response.data) > 0:
                report_id = response.data[0]["id"]
                logger.info(f"✅ Data quality report saved: {report_id}")
                return report_id
            
            return None
            
        except Exception as e:
            logger.error(f"Error saving data quality report: {e}")
            return None
    
    def get_latest_quality_report(self, dataset_id: str) -> Optional[Dict]:
        """Get latest data quality report"""
        try:
            if not self.client:
                return None
            
            response = (
                self.client.table("data_quality_reports")
                .select("*")
                .eq("dataset_id", dataset_id)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            
            if response.data:
                return response.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting quality report: {e}")
            return None


# Global instance
_supabase_manager = None


def get_supabase_manager() -> SupabaseManager:
    """Get or create Supabase manager instance"""
    global _supabase_manager
    if _supabase_manager is None:
        _supabase_manager = SupabaseManager()
    return _supabase_manager