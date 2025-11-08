"""
Admin Panel Page - User Management
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.auth import check_authentication, AuthManager
from utils.logger import get_logger

logger = get_logger(__name__)

st.set_page_config(page_title="Admin Panel", page_icon="🔐", layout="wide")

def main():
    if not check_authentication():
        return
    
    # Check if user is admin
    if not st.session_state.get('is_admin', False):
        st.error("🚫 Access Denied: Admin privileges required")
        st.info("Only administrators can access this page")
        return
    
    st.title("🔐 Admin Panel")
    st.markdown("User management and system administration")
    
    auth_manager = AuthManager()
    
    # ==================== ADD USER ====================
    st.markdown("### ➕ Add New User")
    
    with st.form("add_user_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            new_username = st.text_input("Username", placeholder="johndoe")
        
        with col2:
            new_password = st.text_input("Password", type="password", placeholder="********")
        
        with col3:
            new_role = st.selectbox("Role", ["user", "admin"])
        
        add_button = st.form_submit_button("➕ Add User", use_container_width=True)
        
        if add_button:
            if new_username and new_password:
                if len(new_password) < 6:
                    st.error("❌ Password must be at least 6 characters long")
                else:
                    success, message = auth_manager.add_user(new_username, new_password, new_role)
                    if success:
                        st.success(f"✅ {message}")
                        logger.info(f"Admin added user: {new_username}")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
            else:
                st.error("❌ Please fill in all fields")
    
    # ==================== USER LIST ====================
    st.markdown("---")
    st.markdown("### 👥 Current Users")
    
    users = auth_manager.get_all_users()
    
    st.metric("Total Users", len(users))
    
    # Display users
    for user in users:
        user_info = auth_manager.authorized_users[user]
        
        with st.expander(f"👤 {user} ({user_info.get('role', 'user')})"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**Username:**", user)
                st.write("**Role:**", user_info.get('role', 'user'))
            
            with col2:
                st.write("**Status:**", "🟢 Active" if user_info.get('is_active', True) else "🔴 Inactive")
                st.write("**Created:**", user_info.get('created_at', 'N/A')[:10])
            
            with col3:
                if user != "admin":
                    if st.button(f"🗑️ Remove {user}", key=f"remove_{user}"):
                        success, message = auth_manager.remove_user(user)
                        if success:
                            st.success(f"✅ {message}")
                            logger.info(f"Admin removed user: {user}")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                else:
                    st.info("Cannot remove admin")
    
    # ==================== CHANGE PASSWORD ====================
    st.markdown("---")
    st.markdown("### 🔐 Change Your Password")
    
    with st.form("change_password_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            current_password = st.text_input("Current Password", type="password")
        
        with col2:
            new_password = st.text_input("New Password", type="password")
        
        with col3:
            confirm_password = st.text_input("Confirm New Password", type="password")
        
        change_button = st.form_submit_button("🔐 Change Password", use_container_width=True)
        
        if change_button:
            if not all([current_password, new_password, confirm_password]):
                st.error("❌ Please fill in all fields")
            elif new_password != confirm_password:
                st.error("❌ New passwords don't match")
            elif len(new_password) < 6:
                st.error("❌ Password must be at least 6 characters long")
            else:
                success, message = auth_manager.change_password(
                    st.session_state.username,
                    current_password,
                    new_password
                )
                if success:
                    st.success(f"✅ {message}")
                    logger.info(f"User {st.session_state.username} changed password")
                else:
                    st.error(f"❌ {message}")
    
    # ==================== SYSTEM INFO ====================
    st.markdown("---")
    st.markdown("### ℹ️ System Information")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"**Total Users:** {len(users)}")
    
    with col2:
        admin_count = sum(1 for u in users if auth_manager.authorized_users[u].get('role') == 'admin')
        st.info(f"**Admins:** {admin_count}")
    
    with col3:
        user_count = len(users) - admin_count
        st.info(f"**Regular Users:** {user_count}")

if __name__ == "__main__":
    main()