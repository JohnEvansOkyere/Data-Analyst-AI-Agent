"""
Enhanced Authentication System with Supabase Integration
Supports user registration, login, and account management
"""

import streamlit as st
import hashlib
import re
from datetime import datetime
from utils.logger import get_logger, audit_logger

logger = get_logger(__name__)

class AuthManager:
    def __init__(self, supabase_client=None):
        """
        Initialize AuthManager with optional Supabase client
        
        Args:
            supabase_client: Supabase client instance (optional)
        """
        self.supabase = supabase_client
        self.use_supabase = supabase_client is not None
        
        # Fallback admin (only used if Supabase not configured)
        self.admin_username = "admin"
        self.admin_password_hash = self._hash_password("admin123")
        
        if not self.use_supabase:
            logger.warning("Supabase not configured. Using local authentication.")
    
    def _hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _validate_password(self, password):
        """
        Validate password strength
        Returns: (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not any(char.isupper() for char in password):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(char.islower() for char in password):
            return False, "Password must contain at least one lowercase letter"
        
        if not any(char.isdigit() for char in password):
            return False, "Password must contain at least one number"
        
        if not any(char in "!@#$%^&*()_+-=[]{}|;:,.<>?" for char in password):
            return False, "Password must contain at least one special character"
        
        return True, ""
    
    def _validate_username(self, username):
        """
        Validate username format
        Returns: (is_valid, error_message)
        """
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"
        
        if len(username) > 30:
            return False, "Username must be less than 30 characters"
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "Username can only contain letters, numbers, and underscores"
        
        return True, ""
    
    def register_user(self, username, email, password, full_name=""):
        """
        Register a new user
        
        Args:
            username: Unique username
            email: User email
            password: User password
            full_name: User's full name (optional)
        
        Returns:
            (success, message)
        """
        try:
            # Validate inputs
            username_valid, username_error = self._validate_username(username)
            if not username_valid:
                return False, username_error
            
            if not self._validate_email(email):
                return False, "Invalid email format"
            
            password_valid, password_error = self._validate_password(password)
            if not password_valid:
                return False, password_error
            
            if self.use_supabase:
                # Check if username already exists
                try:
                    response = self.supabase.table("users").select("username").eq("username", username).execute()
                    if response.data and len(response.data) > 0:
                        return False, "Username already exists"
                except Exception as e:
                    logger.error(f"Error checking username: {e}")
                
                # Check if email already exists
                try:
                    response = self.supabase.table("users").select("email").eq("email", email).execute()
                    if response.data and len(response.data) > 0:
                        return False, "Email already registered"
                except Exception as e:
                    logger.error(f"Error checking email: {e}")
                
                # Create user in Supabase
                try:
                    user_data = {
                        "username": username,
                        "email": email,
                        "password_hash": self._hash_password(password),
                        "full_name": full_name,
                        "role": "user",
                        "is_active": True,
                        "created_at": datetime.utcnow().isoformat(),
                        "updated_at": datetime.utcnow().isoformat()
                    }
                    
                    response = self.supabase.table("users").insert(user_data).execute()
                    
                    if response.data:
                        logger.info(f"New user registered: {username}")
                        audit_logger.log_user_action(username, "register", "User account created")
                        return True, "Account created successfully! Please login."
                    else:
                        return False, "Failed to create account. Please try again."
                        
                except Exception as e:
                    logger.error(f"Error creating user in Supabase: {e}")
                    return False, f"Database error: {str(e)}"
            
            else:
                # Local fallback (not recommended for production)
                return False, "Registration requires Supabase configuration"
        
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return False, f"Registration failed: {str(e)}"
    
    def authenticate_user(self, username, password):
        """
        Authenticate a user
        
        Args:
            username: Username or email
            password: User password
        
        Returns:
            (success, message, user_data)
        """
        try:
            if self.use_supabase:
                # Try to find user by username or email
                try:
                    response = self.supabase.table("users").select("*").or_(
                        f"username.eq.{username},email.eq.{username}"
                    ).execute()
                    
                    if not response.data or len(response.data) == 0:
                        return False, "Invalid username/email or password", None
                    
                    user = response.data[0]
                    
                    # Check if account is active
                    if not user.get("is_active", True):
                        return False, "Account is deactivated. Contact administrator.", None
                    
                    # Verify password
                    if user["password_hash"] == self._hash_password(password):
                        # Update last login
                        try:
                            self.supabase.table("users").update({
                                "last_login": datetime.utcnow().isoformat()
                            }).eq("id", user["id"]).execute()
                        except Exception as e:
                            logger.warning(f"Failed to update last login: {e}")
                        
                        audit_logger.log_user_action(user["username"], "login", "User logged in")
                        logger.info(f"User logged in: {user['username']}")
                        
                        return True, "Login successful!", user
                    else:
                        return False, "Invalid username/email or password", None
                
                except Exception as e:
                    logger.error(f"Authentication error: {e}")
                    return False, f"Authentication error: {str(e)}", None
            
            else:
                # Fallback to admin only
                if username == self.admin_username and self._hash_password(password) == self.admin_password_hash:
                    user_data = {
                        "username": self.admin_username,
                        "email": "admin@vexaai.com",
                        "role": "admin",
                        "full_name": "Administrator"
                    }
                    audit_logger.log_user_action(username, "login", "Admin logged in (local)")
                    return True, "Login successful!", user_data
                else:
                    return False, "Invalid username or password", None
        
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False, f"Authentication failed: {str(e)}", None
    
    def is_admin(self, username):
        """Check if user is admin"""
        try:
            if self.use_supabase:
                response = self.supabase.table("users").select("role").eq("username", username).execute()
                if response.data and len(response.data) > 0:
                    return response.data[0].get("role") == "admin"
            else:
                return username == self.admin_username
            return False
        except Exception as e:
            logger.error(f"Error checking admin status: {e}")
            return False
    
    def change_password(self, username, old_password, new_password):
        """Change user password"""
        try:
            # Validate new password
            password_valid, password_error = self._validate_password(new_password)
            if not password_valid:
                return False, password_error
            
            if self.use_supabase:
                # Verify old password first
                response = self.supabase.table("users").select("password_hash").eq("username", username).execute()
                
                if not response.data or len(response.data) == 0:
                    return False, "User not found"
                
                user = response.data[0]
                
                if user["password_hash"] != self._hash_password(old_password):
                    return False, "Current password is incorrect"
                
                # Update password
                update_response = self.supabase.table("users").update({
                    "password_hash": self._hash_password(new_password),
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("username", username).execute()
                
                if update_response.data:
                    audit_logger.log_user_action(username, "change_password", "Password changed")
                    return True, "Password changed successfully!"
                else:
                    return False, "Failed to update password"
            else:
                return False, "Password change requires Supabase configuration"
        
        except Exception as e:
            logger.error(f"Password change error: {e}")
            return False, f"Error changing password: {str(e)}"


def show_register_page(supabase_client=None):
    """Show user registration page"""
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1>📝 Create Your Account</h1>
        <p>Join VexaAI Data Analyst Pro</p>
    </div>
    """, unsafe_allow_html=True)
    
    auth_manager = AuthManager(supabase_client)
    
    if not auth_manager.use_supabase:
        st.error("⚠️ Registration is not available without Supabase configuration")
        st.info("Please configure Supabase in the sidebar to enable user registration")
        
        if st.button("← Back to Login"):
            st.session_state.show_register = False
            st.rerun()
        return
    
    with st.form("register_form"):
        st.markdown("### 📋 Registration Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input(
                "Full Name",
                placeholder="John Doe",
                help="Your full name"
            )
            
            username = st.text_input(
                "Username *",
                placeholder="johndoe",
                help="Unique username (3-30 characters, letters, numbers, underscore only)"
            )
        
        with col2:
            email = st.text_input(
                "Email *",
                placeholder="john@example.com",
                help="Valid email address"
            )
            
            st.write("")  # Spacer
            st.write("")  # Spacer
        
        password = st.text_input(
            "Password *",
            type="password",
            help="Min 8 chars, uppercase, lowercase, number, special character"
        )
        
        confirm_password = st.text_input(
            "Confirm Password *",
            type="password"
        )
        
        # Password requirements
        with st.expander("🔐 Password Requirements"):
            st.markdown("""
            Your password must contain:
            - ✓ At least 8 characters
            - ✓ At least one uppercase letter (A-Z)
            - ✓ At least one lowercase letter (a-z)
            - ✓ At least one number (0-9)
            - ✓ At least one special character (!@#$%^&*...)
            """)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            register_button = st.form_submit_button(
                "📝 Create Account",
                type="primary",
                use_container_width=True
            )
        
        with col2:
            if st.form_submit_button("← Back to Login", use_container_width=True):
                st.session_state.show_register = False
                st.rerun()
        
        if register_button:
            # Validation
            if not all([username, email, password, confirm_password]):
                st.error("❌ Please fill in all required fields (marked with *)")
            elif password != confirm_password:
                st.error("❌ Passwords don't match!")
            else:
                with st.spinner("Creating your account..."):
                    success, message = auth_manager.register_user(
                        username=username.strip(),
                        email=email.strip().lower(),
                        password=password,
                        full_name=full_name.strip()
                    )
                    
                    if success:
                        st.success(f"✅ {message}")
                        st.balloons()
                        st.info("👉 Click 'Back to Login' to sign in with your new account")
                    else:
                        st.error(f"❌ {message}")


def show_login_page(supabase_client=None):
    """Show login page"""
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1>🔐 VexaAI Data Analyst Pro</h1>
        <p>Login to access your data analysis platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    auth_manager = AuthManager(supabase_client)
    
    with st.form("login_form"):
        st.markdown("### 🔑 Login Credentials")
        
        username = st.text_input(
            "Username or Email",
            placeholder="Enter your username or email"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password"
        )
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            login_button = st.form_submit_button(
                "🔐 Login",
                type="primary",
                use_container_width=True
            )
        
        with col2:
            if st.form_submit_button("📝 Create Account", use_container_width=True):
                st.session_state.show_register = True
                st.rerun()
        
        if login_button:
            if username and password:
                with st.spinner("Authenticating..."):
                    success, message, user_data = auth_manager.authenticate_user(username, password)
                    
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.username = user_data["username"]
                        st.session_state.user_email = user_data.get("email", "")
                        st.session_state.user_full_name = user_data.get("full_name", "")
                        st.session_state.is_admin = user_data.get("role") == "admin"
                        
                        st.success(f"✅ {message}")
                        st.balloons()
                        
                        # Small delay for better UX
                        import time
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
            else:
                st.error("❌ Please enter both username/email and password")
    
    # Info section
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("ℹ️ About VexaAI Data Analyst Pro"):
            st.markdown("""
            **Features:**
            - 🤖 AI-Powered Data Analysis
            - 🧹 Advanced Data Cleaning
            - 📊 Interactive Visualizations
            - 📈 Statistical Analysis
            - 💾 Cloud Storage (Supabase)
            - 🔒 Secure Authentication
            """)
    
    with col2:
        if not auth_manager.use_supabase:
            with st.expander("🔑 Default Admin (No Supabase)"):
                st.warning("Supabase not configured. Using default admin.")
                st.markdown("""
                **Default Admin Credentials:**
                - Username: `admin`
                - Password: `admin123`
                
                ⚠️ Configure Supabase for full functionality!
                """)
    
    # Footer
    st.markdown("""
    <div style="text-align: center; margin-top: 3rem; color: #666;">
        <p>Developed by John Evans Okyere | VexaAI © 2025</p>
        <p><small>Powered by Grok AI & Supabase</small></p>
    </div>
    """, unsafe_allow_html=True)


def check_authentication(supabase_client=None):
    """
    Check if user is authenticated
    
    Args:
        supabase_client: Optional Supabase client for enhanced features
    
    Returns:
        bool: True if authenticated, False otherwise
    """

    if supabase_client is None:
        supabase_client = st.session_state.get("supabase_client", None)

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if "show_register" not in st.session_state:
        st.session_state.show_register = False
    
    if not st.session_state.authenticated:
        if st.session_state.show_register:
            show_register_page(supabase_client)
        else:
            show_login_page(supabase_client)
        return False
    
    return True