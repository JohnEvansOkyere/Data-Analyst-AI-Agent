import streamlit as st
import hashlib
import json
import os
from datetime import datetime, timedelta

class AuthManager:
    def __init__(self):
        self.admin_username = "admin"
        # Default admin password - you should change this
        self.admin_password_hash = self._hash_password("admin123")
        self.users_file = "authorized_users.json"
        self.load_authorized_users()
    
    def _hash_password(self, password):
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def load_authorized_users(self):
        """Load authorized users from file"""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r') as f:
                    self.authorized_users = json.load(f)
            else:
                # Initialize with admin user
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
            st.error(f"Error loading users: {e}")
            self.authorized_users = {}
    
    def save_authorized_users(self):
        """Save authorized users to file"""
        try:
            with open(self.users_file, 'w') as f:
                json.dump(self.authorized_users, f, indent=2)
        except Exception as e:
            st.error(f"Error saving users: {e}")
    
    def add_user(self, username, password, role="user"):
        """Add a new authorized user (admin only)"""
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
        return True, "User added successfully"
    
    def remove_user(self, username):
        """Remove a user (admin only)"""
        if username == self.admin_username:
            return False, "Cannot remove admin user"
        
        if username in self.authorized_users:
            del self.authorized_users[username]
            self.save_authorized_users()
            return True, "User removed successfully"
        return False, "User not found"
    
    def authenticate_user(self, username, password):
        """Authenticate a user"""
        if username not in self.authorized_users:
            return False, "Invalid username or password"
        
        user = self.authorized_users[username]
        if not user.get("is_active", True):
            return False, "Account is deactivated"
        
        if user["password_hash"] == self._hash_password(password):
            return True, "Authentication successful"
        
        return False, "Invalid username or password"
    
    def change_password(self, username, old_password, new_password):
        """Change user password"""
        if username not in self.authorized_users:
            return False, "User not found"
        
        user = self.authorized_users[username]
        if user["password_hash"] != self._hash_password(old_password):
            return False, "Current password is incorrect"
        
        user["password_hash"] = self._hash_password(new_password)
        self.save_authorized_users()
        return True, "Password changed successfully"
    
    def get_all_users(self):
        """Get list of all users (admin only)"""
        return list(self.authorized_users.keys())
    
    def is_admin(self, username):
        """Check if user is admin"""
        if username in self.authorized_users:
            return self.authorized_users[username].get("role") == "admin"
        return False

def show_login_page():
    """Show the login page"""
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1>🔐 VexaAI Data Analyst</h1>
        <p>Please login to access the application</p>
    </div>
    """, unsafe_allow_html=True)
    
    auth_manager = AuthManager()
    
    # Login form
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
    
    # Admin login info
    with st.expander("🔑 Admin Access"):
        st.markdown("""
        **Default Admin Credentials:**
        - Username: `admin`
        - Password: `admin123`
        
        **Please change the default password after first login!**
        """)
    
    # Footer
    st.markdown("""
    <div style="text-align: center; margin-top: 3rem; color: #666;">
        <p>Developed by John Evans Okyere | VexaAI © 2025</p>
    </div>
    """, unsafe_allow_html=True)

def show_admin_panel():
    """Show admin panel for user management"""
    auth_manager = AuthManager()
    
    st.markdown("## 👨‍💼 Admin Panel")
    
    # Add new user
    with st.expander("➕ Add New User", expanded=True):
        with st.form("add_user_form"):
            new_username = st.text_input("Username", key="new_username")
            new_password = st.text_input("Password", type="password", key="new_password")
            new_role = st.selectbox("Role", ["user", "admin"], key="new_role")
            add_button = st.form_submit_button("Add User")
            
            if add_button:
                if new_username and new_password:
                    success, message = auth_manager.add_user(new_username, new_password, new_role)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please enter both username and password")
    
    # Remove user
    with st.expander("🗑️ Remove User"):
        users = auth_manager.get_all_users()
        users.remove("admin")  # Don't show admin in removal list
        
        if users:
            user_to_remove = st.selectbox("Select user to remove", users)
            if st.button("Remove User"):
                success, message = auth_manager.remove_user(user_to_remove)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        else:
            st.info("No users to remove")
    
    # Change password
    with st.expander("🔐 Change Password"):
        with st.form("change_password_form"):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            change_button = st.form_submit_button("Change Password")
            
            if change_button:
                if new_password == confirm_password:
                    success, message = auth_manager.change_password(
                        st.session_state.username, 
                        current_password, 
                        new_password
                    )
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.error("New passwords don't match")
    
    # User list
    with st.expander("👥 Current Users"):
        users = auth_manager.get_all_users()
        for user in users:
            role = auth_manager.authorized_users[user].get("role", "user")
            status = "🟢 Active" if auth_manager.authorized_users[user].get("is_active", True) else "🔴 Inactive"
            st.write(f"**{user}** - {role} - {status}")

def check_authentication():
    """Check if user is authenticated"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        show_login_page()
        return False
    
    return True
