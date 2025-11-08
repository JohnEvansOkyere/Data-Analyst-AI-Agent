import streamlit as st
import hashlib
import json
import os
from datetime import datetime, timedelta
from utils.logger import get_logger, audit_logger

logger = get_logger(__name__)

class AuthManager:
    def __init__(self):
        self.admin_username = "admin"
        self.admin_password_hash = self._hash_password("admin123")
        self.users_file = "authorized_users.json"
        self.load_authorized_users()
    
    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def load_authorized_users(self):
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r') as f:
                    self.authorized_users = json.load(f)
            else:
                self.authorized_users = {
                    self.admin_username: {
                        "password_hash": self.admin_password_hash,
                        "role": "admin",
                        "created_at": datetime.now().isoformat(),
                        "is_active": True
                    }
                }
                self.save_authorized_users()
        except Exception as e:
            logger.error(f"Error loading users: {e}")
            self.authorized_users = {}
    
    def save_authorized_users(self):
        try:
            with open(self.users_file, 'w') as f:
                json.dump(self.authorized_users, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving users: {e}")
    
    def add_user(self, username, password, role="user"):
        if username in self.authorized_users:
            return False, "User already exists"
        
        password_hash = self._hash_password(password)
        self.authorized_users[username] = {
            "password_hash": password_hash,
            "role": role,
            "created_at": datetime.now().isoformat(),
            "is_active": True
        }
        self.save_authorized_users()
        audit_logger.log_user_action("admin", "add_user", f"Added user: {username}")
        return True, "User added successfully"
    
    def remove_user(self, username):
        if username == self.admin_username:
            return False, "Cannot remove admin user"
        
        if username in self.authorized_users:
            del self.authorized_users[username]
            self.save_authorized_users()
            audit_logger.log_user_action("admin", "remove_user", f"Removed user: {username}")
            return True, "User removed successfully"
        return False, "User not found"
    
    def authenticate_user(self, username, password):
        if username not in self.authorized_users:
            return False, "Invalid username or password"
        
        user = self.authorized_users[username]
        if not user.get("is_active", True):
            return False, "Account is deactivated"
        
        if user["password_hash"] == self._hash_password(password):
            audit_logger.log_user_action(username, "login", "User logged in")
            return True, "Authentication successful"
        
        return False, "Invalid username or password"
    
    def change_password(self, username, old_password, new_password):
        if username not in self.authorized_users:
            return False, "User not found"
        
        user = self.authorized_users[username]
        if user["password_hash"] != self._hash_password(old_password):
            return False, "Current password is incorrect"
        
        user["password_hash"] = self._hash_password(new_password)
        self.save_authorized_users()
        audit_logger.log_user_action(username, "change_password", "Password changed")
        return True, "Password changed successfully"
    
    def get_all_users(self):
        return list(self.authorized_users.keys())
    
    def is_admin(self, username):
        if username in self.authorized_users:
            return self.authorized_users[username].get("role") == "admin"
        return False

def show_login_page():
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1>🔐 VexaAI Data Analyst Pro</h1>
        <p>Please login to access the application</p>
    </div>
    """, unsafe_allow_html=True)
    
    auth_manager = AuthManager()
    
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if username and password:
                success, message = auth_manager.authenticate_user(username, password)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.is_admin = auth_manager.is_admin(username)
                    st.success("Login successful! Redirecting...")
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Please enter both username and password")
    
    with st.expander("🔑 Admin Access"):
        st.markdown("""
        **Default Admin Credentials:**
        - Username: `admin`
        - Password: `admin123`
        
        **Please change the default password after first login!**
        """)
    
    st.markdown("""
    <div style="text-align: center; margin-top: 3rem; color: #666;">
        <p>Developed by John Evans Okyere | VexaAI © 2025</p>
    </div>
    """, unsafe_allow_html=True)

def check_authentication():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        show_login_page()
        return False
    
    return True
