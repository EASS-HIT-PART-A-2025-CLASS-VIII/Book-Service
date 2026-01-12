import streamlit as st
import requests
from typing import Optional

API_URL = "http://localhost:8000"


def initialize_session_state():
    """Initialize session state variables with persistence"""
    # Use query params to persist login state across refreshes
    params = st.query_params
    
    # Check if we have a saved token in URL
    if "logged_in" not in st.session_state:
        if "token" in params:
            st.session_state.logged_in = True
            st.session_state.access_token = params["token"]
            # Verify token and get user info
            user = get_current_user()
            if user:
                st.session_state.user = user
            else:
                st.session_state.logged_in = False
                st.session_state.access_token = None
        else:
            st.session_state.logged_in = False
            st.session_state.access_token = None
            st.session_state.user = None

def register_user(username: str, email: str, password: str, full_name: str) -> tuple[bool, str]:
    """Register a new user"""
    try:
        response = requests.post(
            f"{API_URL}/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password,
                "full_name": full_name
            }
        )
        
        if response.status_code == 200:
            return True, "Registration successful! Please login."
        else:
            error_detail = response.json().get("detail", "Registration failed")
            return False, error_detail
            
    except Exception as e:
        return False, f"Error: {str(e)}"


def login_user(username: str, password: str) -> tuple[bool, str]:
    """Login user and store JWT token"""
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json={
                "username": username,
                "password": password
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.access_token = data["access_token"]
            st.session_state.user = data["user"]
            st.session_state.logged_in = True
            
            # Save token in URL to persist across refreshes
            st.query_params["token"] = data["access_token"]
            
            return True, f"Welcome back, {data['user']['username']}!"
        else:
            error_detail = response.json().get("detail", "Login failed")
            return False, error_detail
            
    except Exception as e:
        return False, f"Error: {str(e)}"


def logout_user():
    """Logout user and clear session"""
    st.session_state.logged_in = False
    st.session_state.access_token = None
    st.session_state.user = None
    
    # Clear token from URL
    if "token" in st.query_params:
        del st.query_params["token"]

def get_current_user() -> Optional[dict]:
    """Get current user info from token"""
    if not st.session_state.get("access_token"):
        return None
    
    try:
        response = requests.get(
            f"{API_URL}/auth/me",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            # Token expired or invalid
            logout_user()
            return None
            
    except Exception as e:
        st.error(f"Error verifying user: {str(e)}")
        return None


def show_login_page():
    """Display login/register page with beautiful styling"""
    
    # Custom CSS for pink theme
    st.markdown("""
    <style>
    /* Main container styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: #FFE4E9;
        padding: 20px;
        border-radius: 15px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 10px;
        padding: 10px 30px;
        font-weight: 600;
        color: #FF69B4;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #FF69B4 0%, #FF1493 100%);
        color: white;
    }
    
    /* Form styling */
    .stTextInput > div > div > input {
        border: 2px solid #FFB6C1;
        border-radius: 10px;
        padding: 10px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #FF69B4;
        box-shadow: 0 0 0 0.2rem rgba(255, 105, 180, 0.25);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #FF69B4 0%, #FF1493 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 30px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(255, 105, 180, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Beautiful header
    st.markdown("""
    <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #FFE4E9 0%, #FFF0F5 100%); 
                border-radius: 20px; margin-bottom: 30px;'>
        <h1 style='color: #FF1493; margin: 0;'>📚 Book Library</h1>
        <p style='color: #FF69B4; font-size: 1.2em; margin: 10px 0 0 0;'>Welcome! Please login or create an account</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Login", "✨ Register"])
    
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown("### Login to Your Account")
            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if not username or not password:
                    st.error("⚠️ Please fill in all fields")
                else:
                    success, message = login_user(username, password)
                    if success:
                        st.success("✅ " + message)
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ " + message)
    
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.form("register_form"):
            st.markdown("### Create Your Account")
            
            col1, col2 = st.columns(2)
            with col1:
                reg_username = st.text_input("👤 Username*", placeholder="Choose a username")
                reg_full_name = st.text_input("✨ Full Name", placeholder="Your full name")
            with col2:
                reg_email = st.text_input("📧 Email*", placeholder="your.email@example.com")
                reg_password = st.text_input("🔒 Password*", type="password", placeholder="At least 6 characters")
            
            reg_password2 = st.text_input("🔒 Confirm Password*", type="password", placeholder="Re-enter your password")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                register = st.form_submit_button("Create Account", use_container_width=True)
            
            if register:
                if not reg_username or not reg_email or not reg_password:
                    st.error("⚠️ Please fill in all required fields (*)")
                elif reg_password != reg_password2:
                    st.error("❌ Passwords do not match")
                elif len(reg_password) < 6:
                    st.error("⚠️ Password must be at least 6 characters")
                else:
                    success, message = register_user(
                        reg_username, 
                        reg_email, 
                        reg_password,
                        reg_full_name or reg_username
                    )
                    if success:
                        st.success("✅ " + message)
                        st.balloons()
                        st.info("💡 Now switch to the Login tab to sign in!")
                    else:
                        st.error("❌ " + message)

def require_login():
    """Decorator to require login for a page"""
    initialize_session_state()
    
    if not st.session_state.logged_in:
        show_login_page()
        st.stop()
    
    # Verify token is still valid
    user = get_current_user()
    if not user:
        st.warning("Your session has expired. Please login again.")
        show_login_page()
        st.stop()


def show_user_info():
    """Display current user info at the top of the page"""
    if st.session_state.get("logged_in") and st.session_state.get("user"):
        user = st.session_state.user
        
        # Create columns for welcome message and logout button
        col1, col2, col3 = st.columns([2, 4, 1])
        
        with col1:
            st.markdown(f"👤 Welcome **{user['username']}**")
        
        with col3:
            if st.button("🚪 Logout", use_container_width=True):
                logout_user()
                st.success("Logged out successfully!")
                st.rerun()