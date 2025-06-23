import streamlit as st
from ui_components import login_page, render_main_app
import time

# Page configuration
st.set_page_config(
    page_title="Ekstraksi Dokumen Imigrasi - PT Laman Davindo Bahman",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
def initialize_session_state():
    """Initialize all required session state variables"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'login_attempt' not in st.session_state:
        st.session_state.login_attempt = 0
    if 'user_role' not in st.session_state:
        st.session_state.user_role = "user"
    if 'session_start_time' not in st.session_state:
        from datetime import datetime
        st.session_state.session_start_time = datetime.now()
    if 'theme' not in st.session_state:
        st.session_state.theme = "light"

def add_custom_css():
    """Add enhanced custom CSS for better mobile and desktop experience"""
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Global font family */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Custom variables for theming */
    :root {
        --primary-color: #3b82f6;
        --secondary-color: #10b981;
        --accent-color: #f59e0b;
        --danger-color: #ef4444;
        --text-primary: #1f2937;
        --text-secondary: #6b7280;
        --bg-primary: #ffffff;
        --bg-secondary: #f9fafb;
        --border-color: #e5e7eb;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    }
    
    /* Dark theme variables */
    [data-theme="dark"] {
        --text-primary: #f9fafb;
        --text-secondary: #d1d5db;
        --bg-primary: #111827;
        --bg-secondary: #1f2937;
        --border-color: #374151;
    }
    
    /* Enhanced scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, var(--primary-color), #2563eb);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #2563eb, #1d4ed8);
    }
    
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .main .block-container {
        background: var(--bg-primary);
        border-radius: 1rem;
        box-shadow: var(--shadow-xl);
        margin: 1rem;
        padding: 2rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Header styling */
    .app-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        border-radius: 1rem;
        margin-bottom: 2rem;
        color: white;
        box-shadow: var(--shadow-lg);
    }
    
    .app-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .app-header p {
        font-size: 1.1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
    }
    
    /* Card components */
    .card {
        background: var(--bg-primary);
        border-radius: 1rem;
        padding: 1.5rem;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-color);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }
    
    .card-header {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--primary-color);
    }
    
    /* Enhanced button styling */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color), #2563eb);
        color: white;
        border: none;
        border-radius: 0.75rem;
        font-weight: 600;
        font-size: 1rem;
        padding: 0.75rem 2rem;
        transition: all 0.3s ease;
        box-shadow: var(--shadow-md);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
    }
    
    .stButton > button:active {
        transform: translateY(0);
        box-shadow: var(--shadow-sm);
    }
    
    /* Secondary button style */
    .secondary-button > button {
        background: transparent;
        color: var(--primary-color);
        border: 2px solid var(--primary-color);
        border-radius: 0.75rem;
        font-weight: 500;
        padding: 0.5rem 1.5rem;
        transition: all 0.3s ease;
    }
    
    .secondary-button > button:hover {
        background: var(--primary-color);
        color: white;
        transform: translateY(-1px);
    }
    
    /* File uploader enhancement */
    .stFileUploader > div {
        border: 2px dashed var(--primary-color);
        border-radius: 1rem;
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.05), rgba(16, 185, 129, 0.05));
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div:hover {
        border-color: var(--secondary-color);
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(16, 185, 129, 0.1));
        transform: scale(1.02);
    }
    
    /* Enhanced input fields */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea > div > div > textarea {
        border-radius: 0.75rem;
        border: 2px solid var(--border-color);
        transition: all 0.3s ease;
        font-size: 1rem;
        padding: 0.75rem;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border-radius: 1rem;
        overflow: hidden;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-color);
    }
    
    /* Alert messages enhancement */
    .stSuccess {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.1));
        border: 1px solid var(--secondary-color);
        border-radius: 0.75rem;
        padding: 1rem;
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(220, 38, 38, 0.1));
        border: 1px solid var(--danger-color);
        border-radius: 0.75rem;
        padding: 1rem;
    }
    
    .stWarning {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(217, 119, 6, 0.1));
        border: 1px solid var(--accent-color);
        border-radius: 0.75rem;
        padding: 1rem;
    }
    
    .stInfo {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(37, 99, 235, 0.1));
        border: 1px solid var(--primary-color);
        border-radius: 0.75rem;
        padding: 1rem;
    }
    
    /* Tab styling improvements */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        padding: 0.5rem;
        background: var(--bg-secondary);
        border-radius: 1rem;
        margin-bottom: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 1.5rem;
        border-radius: 0.75rem;
        font-weight: 500;
        transition: all 0.3s ease;
        border: none;
        background: transparent;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary-color), #2563eb);
        color: white;
        box-shadow: var(--shadow-md);
    }
    
    /* Sidebar enhancements */
    .css-1d391kg {
        background: linear-gradient(180deg, var(--bg-primary), var(--bg-secondary));
        border-right: 1px solid var(--border-color);
    }
    
    /* Metrics styling */
    .stMetric {
        background: var(--bg-primary);
        padding: 1rem;
        border-radius: 0.75rem;
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--border-color);
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        border-radius: 0.5rem;
    }
    
    /* Loading spinner */
    .stSpinner > div {
        border-top-color: var(--primary-color) !important;
        border-right-color: var(--secondary-color) !important;
    }
    
    /* Responsive design improvements */
    @media (max-width: 768px) {
        .main .block-container {
            margin: 0.5rem;
            padding: 1rem;
            border-radius: 0.5rem;
        }
        
        .app-header {
            padding: 1.5rem 1rem;
            margin-bottom: 1rem;
        }
        
        .app-header h1 {
            font-size: 1.8rem;
        }
        
        .card {
            padding: 1rem;
        }
        
        .stButton > button {
            width: 100%;
            padding: 0.75rem;
            font-size: 0.9rem;
        }
    }
    
    /* Animation classes */
    .fade-in {
        animation: fadeIn 0.6s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .slide-in {
        animation: slideIn 0.5s ease-out;
    }
    
    @keyframes slideIn {
        from { transform: translateX(-100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    /* Notification badge */
    .notification-badge {
        position: absolute;
        top: -5px;
        right: -5px;
        background: var(--danger-color);
        color: white;
        border-radius: 50%;
        width: 20px;
        height: 20px;
        font-size: 0.75rem;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

def add_app_header():
    """Add enhanced application header"""
    st.markdown("""
    <div class="app-header fade-in">
        <h1>🖥️ PT LAMAN DAVINDO BAHMAN</h1>
        <p>Sistem Ekstraksi Dokumen Imigrasi</p>
    </div>
    """, unsafe_allow_html=True)

def create_metric_cards():
    """Create dashboard metric cards"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📄 Total Dokumen",
            value="1,234",
            delta="12 hari ini",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            label="✅ Berhasil Diproses",
            value="1,180",
            delta="95.6%",
            delta_color="normal"
        )
    
    with col3:
        st.metric(
            label="⏱️ Rata-rata Waktu",
            value="2.3 detik",
            delta="-0.5 detik",
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            label="👥 Pengguna Aktif",
            value="24",
            delta="3 hari ini",
            delta_color="normal"
        )

def add_loading_animation():
    """Add loading animation"""
    return st.empty()

def show_progress_bar(progress_text="Processing...", progress_value=0):
    """Show animated progress bar"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(progress_value + 1):
        progress_bar.progress(i)
        status_text.text(f'{progress_text} {i}%')
        time.sleep(0.01)

def create_notification_system():
    """Create a notification system"""
    if 'notifications' not in st.session_state:
        st.session_state.notifications = []
    
    # Add sample notifications
    notifications = [
        {"type": "success", "message": "Dokumen berhasil diproses", "time": "2 menit lalu"},
        {"type": "info", "message": "Update sistem tersedia", "time": "1 jam lalu"},
        {"type": "warning", "message": "Kapasitas storage 80%", "time": "3 jam lalu"}
    ]
    
    if notifications:
        with st.sidebar:
            st.markdown("### 🔔 Notifikasi")
            for notif in notifications[:3]:  # Show only recent 3
                icon = {"success": "✅", "info": "ℹ️", "warning": "⚠️"}.get(notif["type"], "📝")
                st.markdown(f"""
                <div class="card" style="padding: 0.75rem; margin-bottom: 0.5rem;">
                    <small style="color: var(--text-secondary);">{notif["time"]}</small><br>
                    {icon} {notif["message"]}
                </div>
                """, unsafe_allow_html=True)

def check_session_timeout():
    """Check if user session has timed out with enhanced UI"""
    if st.session_state.logged_in:
        from datetime import datetime, timedelta
        current_time = datetime.now()
        session_duration = current_time - st.session_state.session_start_time
        
        # Set timeout to 8 hours
        timeout_duration = timedelta(hours=8)
        
        # Show session time remaining in sidebar
        remaining_time = timeout_duration - session_duration
        if remaining_time.total_seconds() > 0:
            hours, remainder = divmod(remaining_time.total_seconds(), 3600)
            minutes, _ = divmod(remainder, 60)
            
            with st.sidebar:
                st.markdown("---")
                st.markdown(f"""
                <div style='text-align: center; color: var(--text-secondary); font-size: 0.8rem;'>
                    ⏰ Sesi berakhir dalam: {int(hours)}j {int(minutes)}m
                </div>
                """, unsafe_allow_html=True)
        else:
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.error("⏰ Session telah berakhir. Silakan login kembali.")
            st.rerun()

def main():
    """Enhanced main application function"""
    # Initialize session state
    initialize_session_state()
    
    # Add custom CSS
    add_custom_css()
    
    # Add app header
    if st.session_state.logged_in:
        add_app_header()
    
    # Check session timeout
    check_session_timeout()
    
    # Main application logic
    try:
        if not st.session_state.logged_in:
            login_page()
        else:
            # Create dashboard metrics
            create_metric_cards()
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Create notification system
            create_notification_system()
            
            # Render main app
            render_main_app()
            
    except Exception as e:
        st.error(f"❌ Terjadi kesalahan dalam aplikasi: {str(e)}")
        st.info("💡 Silakan refresh halaman atau hubungi administrator jika masalah berlanjut.")
        
        # Add debug info in development
        if st.checkbox("🔧 Show Debug Info (Development Only)"):
            st.exception(e)

def show_app_info():
    """Show enhanced application information in sidebar footer"""
    if st.session_state.logged_in:
        with st.sidebar:
            st.markdown("---")
            
            # Theme toggle (placeholder - implement theme switching logic)
            theme_col1, theme_col2 = st.columns(2)
            with theme_col1:
                if st.button("🌙 Dark"):
                    st.session_state.theme = "dark"
            with theme_col2:
                if st.button("☀️ Light"):
                    st.session_state.theme = "light"
            
            st.markdown("---")
            st.markdown("""
            <div style='text-align: center; color: var(--text-secondary); font-size: 0.8rem;'>
                <p><strong>🏢 PT Laman Davindo Bahman</strong></p>
                <p>📄 Immigration Document Extraction System</p>
                <p>🔄 Version 2.1 - 2025</p>
                <p>👤 User: """ + st.session_state.get('username', 'Guest') + """</p>
            </div>
            """, unsafe_allow_html=True)

# Run the application
if __name__ == "__main__":
    main()
    show_app_info()
