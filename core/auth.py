"""
VexaAI Data Analyst Pro - Authentication System
Supabase-based user authentication with registration and login
"""

import streamlit as st
import hashlib
from datetime import datetime
from supabase import create_client, Client
from database.supabase_manager import get_supabase_manager
from config.settings import SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_ROLE_KEY
from utils.logger import get_logger, audit_logger

logger = get_logger(__name__)


class SupabaseAuthManager:
    """Authentication manager using Supabase database"""
    
    def __init__(self):
        self.supabase_manager = get_supabase_manager()
        self.client = self.supabase_manager.client if self.supabase_manager.is_connected() else None
        
        # Admin client with service role key for privileged operations
        self.admin_client = None
        if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
            try:
                self.admin_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
                logger.info("✅ Admin client initialized with service role key")
            except Exception as e:
                logger.error(f"❌ Failed to initialize admin client: {e}")
        
        if not self.client:
            logger.warning("Supabase not connected - authentication will not work")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username: str, email: str, password: str, full_name: str = "") -> tuple[bool, str]:
        """Register a new user in Supabase"""
        try:
            if not self.client:
                return False, "Database connection not available"
            
            if not username or not email or not password:
                return False, "All fields are required"
            
            if len(password) < 8:
                return False, "Password must be at least 8 characters"
            
            if "@" not in email:
                return False, "Invalid email address"
            
            existing = self.client.table('users').select('*').or_(
                f'username.eq.{username},email.eq.{email}'
            ).execute()
            
            if existing.data:
                return False, "Username or email already exists"
            
            password_hash = self._hash_password(password)
            user_data = {
                "username": username,
                "email": email,
                "password_hash": password_hash,
                "full_name": full_name,
                "role": "user",
                "is_active": True,
                "created_at": datetime.utcnow().isoformat()
            }
            
            response = self.client.table('users').insert(user_data).execute()
            
            if response.data:
                logger.info(f"New user registered: {username}")
                audit_logger.log_user_action(username, "register", "User registered successfully")
                return True, "Account created successfully! Please login."
            else:
                return False, "Failed to create account"
                
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return False, f"Registration failed: {str(e)}"
    
    def authenticate_user(self, username: str, password: str) -> tuple[bool, str, dict]:
        """Authenticate user against Supabase database"""
        try:
            if not self.client:
                return False, "Database connection not available", {}
            
            response = self.client.table('users').select('*').or_(
                f'username.eq.{username},email.eq.{username}'
            ).execute()
            
            if not response.data:
                return False, "Invalid username or password", {}
            
            user = response.data[0]
            
            if not user.get('is_active', True):
                return False, "Account is deactivated", {}
            
            password_hash = self._hash_password(password)
            if user['password_hash'] == password_hash:
                # Use admin client to update last login (bypass RLS)
                update_client = self.admin_client if self.admin_client else self.client
                update_client.table('users').update({
                    'last_login': datetime.utcnow().isoformat()
                }).eq('id', user['id']).execute()
                
                logger.info(f"User logged in: {user['username']}")
                audit_logger.log_user_action(user['username'], "login", "User logged in successfully")
                
                return True, "Login successful", user
            else:
                return False, "Invalid username or password", {}
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False, f"Login failed: {str(e)}", {}
    
    def get_user_by_username(self, username: str) -> dict:
        """Get user data by username"""
        try:
            client = self.admin_client if self.admin_client else self.client
            if not client:
                return {}
            
            response = client.table('users').select('*').eq('username', username).execute()
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"Error fetching user: {e}")
            return {}
    
    def get_all_users(self) -> list:
        """Get all users (admin only - uses service role)"""
        try:
            client = self.admin_client if self.admin_client else self.client
            if not client:
                return []
            
            response = client.table('users').select('username, email, full_name, role, is_active, created_at').execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching users: {e}")
            return []
    
    def update_password(self, username: str, old_password: str, new_password: str) -> tuple[bool, str]:
        """Update user password"""
        try:
            if not self.client:
                return False, "Database connection not available"
            
            success, message, user = self.authenticate_user(username, old_password)
            if not success:
                return False, "Current password is incorrect"
            
            if len(new_password) < 8:
                return False, "New password must be at least 8 characters"
            
            new_hash = self._hash_password(new_password)
            
            # Use admin client for update (bypass RLS)
            update_client = self.admin_client if self.admin_client else self.client
            update_client.table('users').update({
                'password_hash': new_hash,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', user['id']).execute()
            
            logger.info(f"Password updated for user: {username}")
            audit_logger.log_user_action(username, "password_change", "Password changed successfully")
            
            return True, "Password updated successfully"
            
        except Exception as e:
            logger.error(f"Password update error: {e}")
            return False, f"Failed to update password: {str(e)}"
    
    def deactivate_user(self, username: str) -> tuple[bool, str]:
        """Deactivate a user account (admin only - uses service role)"""
        try:
            if not self.admin_client:
                return False, "Admin privileges required. Service role key not configured."
            
            if username == "admin":
                return False, "Cannot deactivate admin account"
            
            self.admin_client.table('users').update({
                'is_active': False,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('username', username).execute()
            
            logger.info(f"User deactivated: {username}")
            audit_logger.log_user_action("admin", "deactivate_user", f"Deactivated user: {username}")
            
            return True, f"User {username} deactivated successfully"
            
        except Exception as e:
            logger.error(f"Error deactivating user: {e}")
            return False, f"Failed to deactivate user: {str(e)}"
    
    def activate_user(self, username: str) -> tuple[bool, str]:
        """Activate a user account (admin only - uses service role)"""
        try:
            if not self.admin_client:
                return False, "Admin privileges required. Service role key not configured."
            
            self.admin_client.table('users').update({
                'is_active': True,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('username', username).execute()
            
            logger.info(f"User activated: {username}")
            audit_logger.log_user_action("admin", "activate_user", f"Activated user: {username}")
            
            return True, f"User {username} activated successfully"
            
        except Exception as e:
            logger.error(f"Error activating user: {e}")
            return False, f"Failed to activate user: {str(e)}"
    
    def delete_user(self, username: str) -> tuple[bool, str]:
        """Delete a user account (admin only - uses service role)"""
        try:
            if not self.admin_client:
                return False, "Admin privileges required. Service role key not configured."
            
            if username == "admin":
                return False, "Cannot delete admin account"
            
            self.admin_client.table('users').delete().eq('username', username).execute()
            
            logger.info(f"User deleted: {username}")
            audit_logger.log_user_action("admin", "delete_user", f"Deleted user: {username}")
            
            return True, f"User {username} deleted successfully"
            
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False, f"Failed to delete user: {str(e)}"
    
    def is_admin(self, username: str) -> bool:
        """Check if user is admin"""
        user = self.get_user_by_username(username)
        return user.get('role') == 'admin'


def show_login_page():
    """Show the login page with tabs for login and registration"""
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1>🔐 VexaAI Data Analyst Pro</h1>
        <p>Welcome! Please login or create an account</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])
    
    auth_manager = SupabaseAuthManager()
    
    if not auth_manager.client:
        st.error("❌ Database connection not available. Please configure Supabase in your .env file.")
        st.info("Required: SUPABASE_URL and SUPABASE_ANON_KEY")
        return
    
    with tab1:
        st.markdown("### 🔑 Login to Your Account")
        
        with st.form("login_form"):
            login_username = st.text_input("Username or Email", placeholder="Enter username or email")
            login_password = st.text_input("Password", type="password", placeholder="Enter password")
            login_button = st.form_submit_button("🚀 Login", use_container_width=True)
            
            if login_button:
                if login_username and login_password:
                    success, message, user_data = auth_manager.authenticate_user(login_username, login_password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.username = user_data['username']
                        st.session_state.user_email = user_data['email']
                        st.session_state.user_full_name = user_data.get('full_name', '')
                        st.session_state.is_admin = (user_data['role'] == 'admin')
                        st.session_state.user_id = user_data['id']
                        st.success("✅ Login successful! Redirecting...")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.error("Please enter both username and password")
        
        with st.expander("🔑 Default Admin Access"):
            st.markdown("""
            **Default Admin Credentials:**
            - Username: `admin`
            - Password: `admin123`
            
            **⚠️ Please change the default password after first login!**
            """)
    
    with tab2:
        st.markdown("### 📝 Create New Account")
        
        with st.form("register_form"):
            reg_username = st.text_input("Username", placeholder="Choose a unique username")
            reg_email = st.text_input("Email", placeholder="Enter your email address")
            reg_full_name = st.text_input("Full Name (optional)", placeholder="Your full name")
            reg_password = st.text_input("Password", type="password", placeholder="At least 8 characters")
            reg_confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
            register_button = st.form_submit_button("✨ Create Account", use_container_width=True)
            
            if register_button:
                if not all([reg_username, reg_email, reg_password, reg_confirm_password]):
                    st.error("❌ Please fill in all required fields")
                elif reg_password != reg_confirm_password:
                    st.error("❌ Passwords do not match")
                elif len(reg_password) < 8:
                    st.error("❌ Password must be at least 8 characters")
                else:
                    success, message = auth_manager.register_user(
                        username=reg_username,
                        email=reg_email,
                        password=reg_password,
                        full_name=reg_full_name
                    )
                    if success:
                        st.success(f"✅ {message}")
                        st.info("👈 Please go to the Login tab to sign in")
                    else:
                        st.error(f"❌ {message}")
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>🔒 Your data is secure and encrypted</p>
        <p>Developed by John Evans Okyere | VexaAI © 2025</p>
    </div>
    """, unsafe_allow_html=True)


def check_authentication() -> bool:
    """Check if user is authenticated"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        show_login_page()
        return False
    
    return True


# ==================== BACKWARD COMPATIBILITY ====================
# Alias for old code that imports AuthManager
AuthManager = SupabaseAuthManager