"""
Admin Panel - User Management
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.auth import check_authentication, SupabaseAuthManager
from database.supabase_manager import get_supabase_manager
from utils.ui_components import apply_modern_css, render_page_header, render_section_header
from utils.logger import get_logger

logger = get_logger(__name__)

st.set_page_config(page_title="Admin Panel", page_icon="🔐", layout="wide")

def main():
    # Check authentication
    if not check_authentication():
        return
    
    # Check if user is admin
    if not st.session_state.get('is_admin', False):
        st.error("🚫 Access Denied")
        st.warning("You need administrator privileges to access this page.")
        st.info("👈 Please contact your system administrator for access.")
        return
    
    # Apply modern CSS
    apply_modern_css()
    
    # Page header
    render_page_header(
        title="Admin Panel",
        subtitle="User management and system administration",
        icon="🔐"
    )
    
    # Initialize auth manager
    auth_manager = SupabaseAuthManager()
    db_manager = get_supabase_manager()
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "👥 Users", 
        "📊 Statistics", 
        "📝 Audit Logs",
        "⚙️ Settings"
    ])
    
    # ==================== TAB 1: USERS ====================
    with tab1:
        render_section_header("👥 User Management")
        
        # Get all users
        users = auth_manager.get_all_users()
        
        if users:
            # Display users in a nice format
            st.markdown(f"**Total Users:** {len(users)}")
            
            # Convert to DataFrame for display
            users_df = pd.DataFrame(users)
            
            # Format the DataFrame
            if 'created_at' in users_df.columns:
                users_df['created_at'] = pd.to_datetime(users_df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
            
            # Display table
            st.dataframe(
                users_df,
                use_container_width=True,
                height=400,
                column_config={
                    "username": st.column_config.TextColumn("Username", width="medium"),
                    "email": st.column_config.TextColumn("Email", width="medium"),
                    "full_name": st.column_config.TextColumn("Full Name", width="medium"),
                    "role": st.column_config.TextColumn("Role", width="small"),
                    "is_active": st.column_config.CheckboxColumn("Active", width="small"),
                    "created_at": st.column_config.TextColumn("Created", width="medium"),
                }
            )
            
            # User actions
            st.markdown("---")
            render_section_header("🔧 User Actions")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Activate/Deactivate User**")
                
                user_to_modify = st.selectbox(
                    "Select User",
                    options=[u['username'] for u in users if u['username'] != 'admin'],
                    key="modify_user"
                )
                
                action_col1, action_col2 = st.columns(2)
                
                with action_col1:
                    if st.button("✅ Activate", use_container_width=True):
                        success, message = auth_manager.activate_user(user_to_modify)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                
                with action_col2:
                    if st.button("🚫 Deactivate", use_container_width=True):
                        success, message = auth_manager.deactivate_user(user_to_modify)
                        if success:
                            st.warning(message)
                            st.rerun()
                        else:
                            st.error(message)
            
            with col2:
                st.markdown("**Delete User**")
                st.warning("⚠️ This action cannot be undone!")
                
                user_to_delete = st.selectbox(
                    "Select User to Delete",
                    options=[u['username'] for u in users if u['username'] != 'admin'],
                    key="delete_user"
                )
                
                if st.button("🗑️ Delete User", use_container_width=True, type="primary"):
                    success, message = auth_manager.delete_user(user_to_delete)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
        else:
            st.info("No users found in the database.")
    
    # ==================== TAB 2: STATISTICS ====================
    with tab2:
        render_section_header("📊 System Statistics")
        
        # Get statistics
        total_users = len(users)
        active_users = sum(1 for u in users if u.get('is_active', True))
        admin_users = sum(1 for u in users if u.get('role') == 'admin')
        
        # Get dataset stats
        datasets = []
        for user in users:
            user_datasets = db_manager.get_user_datasets(user['username'])
            datasets.extend(user_datasets)
        
        total_datasets = len(datasets)
        
        # Get audit logs
        all_logs = []
        for user in users:
            user_logs = db_manager.get_user_activity_logs(user['username'], limit=100)
            all_logs.extend(user_logs)
        
        total_logs = len(all_logs)
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👥 Total Users", total_users)
        
        with col2:
            st.metric("✅ Active Users", active_users)
        
        with col3:
            st.metric("📊 Total Datasets", total_datasets)
        
        with col4:
            st.metric("📝 Audit Logs", total_logs)
        
        # User activity chart
        if users:
            st.markdown("---")
            st.markdown("### 👤 User Details")
            
            user_details = []
            for user in users:
                user_datasets = db_manager.get_user_datasets(user['username'])
                user_logs = db_manager.get_user_activity_logs(user['username'], limit=10)
                
                user_details.append({
                    "Username": user['username'],
                    "Email": user['email'],
                    "Role": user['role'],
                    "Status": "✅ Active" if user.get('is_active', True) else "🚫 Inactive",
                    "Datasets": len(user_datasets),
                    "Activities": len(user_logs)
                })
            
            details_df = pd.DataFrame(user_details)
            st.dataframe(details_df, use_container_width=True, height=400)
    
    # ==================== TAB 3: AUDIT LOGS ====================
    with tab3:
        render_section_header("📝 Recent Audit Logs")
        
        # Get all audit logs
        all_logs = []
        for user in users:
            user_logs = db_manager.get_user_activity_logs(user['username'], limit=50)
            all_logs.extend(user_logs)
        
        # Sort by timestamp
        all_logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        if all_logs:
            # Display logs
            st.markdown(f"**Showing last {min(len(all_logs), 100)} activities**")
            
            logs_df = pd.DataFrame(all_logs[:100])
            
            # Format timestamp
            if 'timestamp' in logs_df.columns:
                logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
            
            st.dataframe(
                logs_df,
                use_container_width=True,
                height=500,
                column_config={
                    "user_id": st.column_config.TextColumn("User", width="medium"),
                    "activity_type": st.column_config.TextColumn("Activity", width="medium"),
                    "description": st.column_config.TextColumn("Description", width="large"),
                    "timestamp": st.column_config.TextColumn("Time", width="medium"),
                }
            )
        else:
            st.info("No audit logs found.")
    
    # ==================== TAB 4: SETTINGS ====================
    with tab4:
        render_section_header("⚙️ Admin Settings")
        
        st.markdown("### 🔐 Change Admin Password")
        
        with st.form("change_password_form"):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            submit_button = st.form_submit_button("🔄 Change Password")
            
            if submit_button:
                if not all([current_password, new_password, confirm_password]):
                    st.error("❌ Please fill in all fields")
                elif new_password != confirm_password:
                    st.error("❌ New passwords do not match")
                elif len(new_password) < 8:
                    st.error("❌ Password must be at least 8 characters")
                else:
                    success, message = auth_manager.update_password(
                        st.session_state.username,
                        current_password,
                        new_password
                    )
                    if success:
                        st.success(f"✅ {message}")
                    else:
                        st.error(f"❌ {message}")
        
        st.markdown("---")
        st.markdown("### 🗄️ Database Status")
        
        if db_manager.is_connected():
            st.success("✅ Supabase Connected")
            st.info(f"📍 URL: {db_manager.url[:30]}...")
        else:
            st.error("❌ Supabase Not Connected")
            st.warning("Check your .env file for SUPABASE_URL and SUPABASE_ANON_KEY")
        
        st.markdown("---")
        st.markdown("### 📊 System Information")
        
        info_col1, info_col2 = st.columns(2)
        
        with info_col1:
            st.markdown("""
            **Application:**
            - Name: VexaAI Data Analyst Pro
            - Version: 2.0.0
            - Environment: Production
            """)
        
        with info_col2:
            st.markdown("""
            **Database:**
            - Type: Supabase (PostgreSQL)
            - Tables: 6
            - RLS: Disabled (Development)
            """)

if __name__ == "__main__":
    main()