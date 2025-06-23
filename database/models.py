import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
import hashlib
import json

class DatabaseManager:
    def __init__(self, db_path: str = "ldb_database.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(100),
                role VARCHAR(20) DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Document extraction history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS extraction_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                filename VARCHAR(255) NOT NULL,
                file_size INTEGER,
                document_type VARCHAR(50),
                extraction_status VARCHAR(20) DEFAULT 'pending',
                extracted_data TEXT,
                processing_time REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Activity logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action VARCHAR(100) NOT NULL,
                details TEXT,
                ip_address VARCHAR(45),
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # System settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_key VARCHAR(100) UNIQUE NOT NULL,
                setting_value TEXT,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Insert default admin user if not exists
        self.create_default_admin()
    
    def create_default_admin(self):
        """Create default admin user"""
        try:
            admin_exists = self.get_user_by_username("admin")
            if not admin_exists:
                self.create_user(
                    username="admin",
                    email="admin@ldb.local",
                    password="admin123",
                    full_name="System Administrator",
                    role="admin"
                )
        except Exception as e:
            print(f"Error creating default admin: {e}")
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username: str, email: str, password: str, 
                   full_name: str = "", role: str = "user") -> bool:
        """Create new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, full_name, role)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, email, password_hash, full_name, role))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                SELECT id, username, email, full_name, role, is_active
                FROM users 
                WHERE username = ? AND password_hash = ? AND is_active = 1
            ''', (username, password_hash))
            
            user = cursor.fetchone()
            
            if user:
                # Update last login
                cursor.execute('''
                    UPDATE users SET last_login = CURRENT_TIMESTAMP 
                    WHERE id = ?
                ''', (user[0],))
                conn.commit()
                
                user_data = {
                    'id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'full_name': user[3],
                    'role': user[4],
                    'is_active': user[5]
                }
                conn.close()
                return user_data
            
            conn.close()
            return None
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, email, full_name, role, created_at, last_login, is_active
                FROM users WHERE username = ?
            ''', (username,))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                return {
                    'id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'full_name': user[3],
                    'role': user[4],
                    'created_at': user[5],
                    'last_login': user[6],
                    'is_active': user[7]
                }
            return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def log_extraction(self, user_id: int, filename: str, file_size: int,
                      document_type: str, extracted_data: Dict, 
                      processing_time: float, status: str = "completed") -> int:
        """Log document extraction"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO extraction_history 
                (user_id, filename, file_size, document_type, extraction_status, 
                 extracted_data, processing_time)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, filename, file_size, document_type, status,
                  json.dumps(extracted_data), processing_time))
            
            extraction_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return extraction_id
        except Exception as e:
            print(f"Error logging extraction: {e}")
            return 0
    
    def get_extraction_history(self, user_id: Optional[int] = None, 
                             limit: int = 100) -> List[Dict]:
        """Get extraction history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if user_id:
                cursor.execute('''
                    SELECT eh.*, u.username 
                    FROM extraction_history eh
                    JOIN users u ON eh.user_id = u.id
                    WHERE eh.user_id = ?
                    ORDER BY eh.created_at DESC
                    LIMIT ?
                ''', (user_id, limit))
            else:
                cursor.execute('''
                    SELECT eh.*, u.username 
                    FROM extraction_history eh
                    JOIN users u ON eh.user_id = u.id
                    ORDER BY eh.created_at DESC
                    LIMIT ?
                ''', (limit,))
            
            history = cursor.fetchall()
            conn.close()
            
            return [{
                'id': row[0],
                'user_id': row[1],
                'filename': row[2],
                'file_size': row[3],
                'document_type': row[4],
                'extraction_status': row[5],
                'extracted_data': json.loads(row[6]) if row[6] else {},
                'processing_time': row[7],
                'created_at': row[8],
                'updated_at': row[9],
                'username': row[10]
            } for row in history]
        except Exception as e:
            print(f"Error getting extraction history: {e}")
            return []
    
    def log_activity(self, user_id: Optional[int], action: str, 
                    details: str = "", ip_address: str = "", 
                    user_agent: str = ""):
        """Log user activity"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO activity_logs (user_id, action, details, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, action, details, ip_address, user_agent))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error logging activity: {e}")
    
    def get_activity_logs(self, user_id: Optional[int] = None, 
                         limit: int = 100) -> List[Dict]:
        """Get activity logs"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if user_id:
                cursor.execute('''
                    SELECT al.*, u.username 
                    FROM activity_logs al
                    LEFT JOIN users u ON al.user_id = u.id
                    WHERE al.user_id = ?
                    ORDER BY al.created_at DESC
                    LIMIT ?
                ''', (user_id, limit))
            else:
                cursor.execute('''
                    SELECT al.*, u.username 
                    FROM activity_logs al
                    LEFT JOIN users u ON al.user_id = u.id
                    ORDER BY al.created_at DESC
                    LIMIT ?
                ''', (limit,))
            
            logs = cursor.fetchall()
            conn.close()
            
            return [{
                'id': row[0],
                'user_id': row[1],
                'action': row[2],
                'details': row[3],
                'ip_address': row[4],
                'user_agent': row[5],
                'created_at': row[6],
                'username': row[7] if row[7] else 'System'
            } for row in logs]
        except Exception as e:
            print(f"Error getting activity logs: {e}")
            return []
    
    def get_dashboard_stats(self, user_id: Optional[int] = None) -> Dict:
        """Get dashboard statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            stats = {}
            
            # Total extractions
            if user_id:
                cursor.execute('SELECT COUNT(*) FROM extraction_history WHERE user_id = ?', (user_id,))
            else:
                cursor.execute('SELECT COUNT(*) FROM extraction_history')
            stats['total_extractions'] = cursor.fetchone()[0]
            
            # Successful extractions
            if user_id:
                cursor.execute('''SELECT COUNT(*) FROM extraction_history 
                                WHERE user_id = ? AND extraction_status = "completed"''', (user_id,))
            else:
                cursor.execute('SELECT COUNT(*) FROM extraction_history WHERE extraction_status = "completed"')
            stats['successful_extractions'] = cursor.fetchone()[0]
            
            # Total users (admin only)
            if not user_id:
                cursor.execute('SELECT COUNT(*) FROM users WHERE is_active = 1')
                stats['total_users'] = cursor.fetchone()[0]
            
            # Recent activity count
            if user_id:
                cursor.execute('''SELECT COUNT(*) FROM activity_logs 
                                WHERE user_id = ? AND created_at >= datetime('now', '-7 days')''', (user_id,))
            else:
                cursor.execute("SELECT COUNT(*) FROM activity_logs WHERE created_at >= datetime('now', '-7 days')")
            stats['recent_activities'] = cursor.fetchone()[0]
            
            conn.close()
            return stats
        except Exception as e:
            print(f"Error getting dashboard stats: {e}")
            return {}
