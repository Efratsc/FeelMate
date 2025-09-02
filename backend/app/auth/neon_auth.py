import os
import psycopg2
from psycopg2.extras import RealDictCursor
import hashlib
import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

class NeonAuth:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        if not self.db_url:
            raise ValueError("DATABASE_URL environment variable is required")
    
    def _get_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.db_url)
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def sign_up(self, email: str, password: str, name: str) -> Dict[str, Any]:
        """Register a new user"""
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Check if user already exists
                cur.execute("SELECT id FROM users WHERE email = %s", (email,))
                if cur.fetchone():
                    raise ValueError("User already exists")
                
                # Create new user
                user_id = str(uuid.uuid4())
                password_hash = self._hash_password(password)
                
                cur.execute("""
                    INSERT INTO users (id, email, name, password_hash, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                """, (user_id, email, name, password_hash, datetime.now()))
                
                conn.commit()
                
                return {
                    "success": True,
                    "user": {
                        "id": user_id,
                        "email": email,
                        "name": name
                    }
                }
        finally:
            conn.close()
    
    def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate a user"""
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                password_hash = self._hash_password(password)
                
                cur.execute("""
                    SELECT id, email, name FROM users 
                    WHERE email = %s AND password_hash = %s
                """, (email, password_hash))
                
                user = cur.fetchone()
                if not user:
                    raise ValueError("Invalid email or password")
                
                return {
                    "success": True,
                    "user": {
                        "id": user['id'],
                        "email": user['email'],
                        "name": user['name']
                    }
                }
        finally:
            conn.close()
    
    def get_user(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT id, email, name FROM users WHERE email = %s", (email,))
                user = cur.fetchone()
                
                if user:
                    return {
                        "id": user['id'],
                        "email": user['email'],
                        "name": user['name']
                    }
                return None
        finally:
            conn.close()
    
    def create_session(self, user_id: str) -> str:
        """Create a session for a user"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                session_id = str(uuid.uuid4())
                expires_at = datetime.now() + timedelta(days=7)
                
                cur.execute("""
                    INSERT INTO sessions (id, user_id, expires_at, created_at)
                    VALUES (%s, %s, %s, %s)
                """, (session_id, user_id, expires_at, datetime.now()))
                
                conn.commit()
                return session_id
        finally:
            conn.close()
    
    def validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Validate a session and return user info"""
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT u.id, u.email, u.name 
                    FROM sessions s 
                    JOIN users u ON s.user_id = u.id 
                    WHERE s.id = %s AND s.expires_at > %s
                """, (session_id, datetime.now()))
                
                user = cur.fetchone()
                if user:
                    return {
                        "id": user['id'],
                        "email": user['email'],
                        "name": user['name']
                    }
                return None
        finally:
            conn.close()

# Global instance
neon_auth_manager = NeonAuth()
