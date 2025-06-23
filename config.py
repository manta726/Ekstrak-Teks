"""
Configuration settings for LDB Application
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Database configuration
DATABASE_CONFIG = {
    'db_path': BASE_DIR / 'database' / 'ldb_database.db',
    'backup_path': BASE_DIR / 'database' / 'backups',
}

# Application settings
APP_CONFIG = {
    'title': 'Ekstraksi Dokumen Imigrasi',
    'version': '2.0.0',
    'description': 'Aplikasi berbasis Streamlit untuk mengekstrak data dari dokumen PDF imigrasi',
    'max_file_size': 50 * 1024 * 1024,  # 50MB
    'allowed_extensions': ['.pdf', '.jpg', '.jpeg', '.png'],
    'session_timeout': 3600,  # 1 hour
}

# Security settings
SECURITY_CONFIG = {
    'password_min_length': 6,
    'max_login_attempts': 3,
    'lockout_duration': 300,  # 5 minutes
    'session_secret': os.getenv('SESSION_SECRET', 'your-secret-key-here'),
}

# Document types
DOCUMENT_TYPES = {
    'SKTT': 'Surat Keterangan Tinggal Terbatas',
    'EVLN': 'Exit Visa Luar Negeri',
    'ITAS': 'Izin Tinggal Terbatas',
    'ITK': 'Izin Tinggal Kunjungan',
    'NOTIFICATION': 'Notifikasi Imigrasi'
}

# Logging configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file_path': BASE_DIR / 'logs' / 'app.log',
}

# Streamlit page configuration
PAGE_CONFIG = {
    'page_title': APP_CONFIG['title'],
    'page_icon': '📄',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded',
}
