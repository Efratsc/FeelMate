import json
import os
import hashlib
import uuid
from typing import Optional, Dict, Any
from pathlib import Path

class SimpleAuth:
    def __init__(self, users_file: str = "users.json"):
        self.users_file = Path(users_file)
        self.users_file.parent.mkdir(exist_ok=True)
        self._load_users()
    
    def _load_users(self):
        """Load users from JSON file"""
        if self.users_file.exists():
            try:
                with open(self.users_file, 'r') as f:
                    self.users = json.load(f)
            except:
                self.users = {}
        else:
            self.users = {}
            self._save_users()
    
    def _save_users(self):
        """Save users to JSON file"""
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def sign_up(self, email: str, password: str, name: str) -> Dict[str, Any]:
        """Register a new user"""
        if email in self.users:
            raise ValueError("User already exists")
        
        user_id = str(uuid.uuid4())
        user_data = {
            "id": user_id,
            "email": email,
            "name": name,
            "password_hash": self._hash_password(password),
            "created_at": str(uuid.uuid1().time)
        }
        
        self.users[email] = user_data
        self._save_users()
        
        return {
            "success": True,
            "user": {
                "id": user_id,
                "email": email,
                "name": name
            }
        }
    
    def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate a user"""
        if email not in self.users:
            raise ValueError("Invalid email or password")
        
        user = self.users[email]
        if user["password_hash"] != self._hash_password(password):
            raise ValueError("Invalid email or password")
        
        return {
            "success": True,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"]
            }
        }
    
    def get_user(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        if email in self.users:
            user = self.users[email]
            return {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"]
            }
        return None
    
    def list_users(self) -> list:
        """List all users (for admin purposes)"""
        return [
            {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "created_at": user["created_at"]
            }
            for user in self.users.values()
        ]

# Global instance
auth_manager = SimpleAuth()
