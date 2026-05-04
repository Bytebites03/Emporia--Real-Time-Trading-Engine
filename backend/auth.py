# auth.py
import jwt
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional
from pydantic import BaseModel, EmailStr
import os

from er_database import db

SECRET_KEY = os.getenv('SECRET_KEY', 'your-super-secret-key-change-this')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    confirm_password: str

class UserLogin(BaseModel):
    username: str
    password: str

class AuthManager:
    def __init__(self):
        pass
    
    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.hash_password(plain_password) == hashed_password
    
    def create_user(self, username: str, email: str, password: str) -> tuple:
        existing = db.get_user(username=username)
        if existing:
            return None, "Username already exists"
        
        existing_email = db.get_user(email=email)
        if existing_email:
            return None, "Email already registered"
        
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        password_hash = self.hash_password(password)
        
        success = db.create_user(user_id, username, email, password_hash)
        
        if success:
            user = db.get_user(user_id=user_id)
            return user, "User created successfully"
        return None, "Failed to create user"
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        user = db.get_user(username=username)
        if user and self.verify_password(password, user['password_hash']):
            db.update_last_login(user['user_id'])
            return user
        return None
    
    def create_access_token(self, user: Dict) -> str:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {
            "sub": user['username'],
            "user_id": user['user_id'],
            "exp": expire,
            "iat": datetime.utcnow()
        }
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    def verify_token(self, token: str) -> Optional[Dict]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return {"username": payload.get("sub"), "user_id": payload.get("user_id")}
        except jwt.PyJWTError:
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        return db.get_user(user_id=user_id)
    
    def update_user_balance(self, user_id: str, cash_delta: float, crypto_delta: float):
        db.update_user_balance(user_id, cash_delta, crypto_delta)

auth_manager = AuthManager()