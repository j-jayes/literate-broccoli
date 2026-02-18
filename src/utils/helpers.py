"""
Utility functions for the lunch ordering system
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Any
from jose import JWTError, jwt
from passlib.context import CryptContext


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password for storing"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def generate_token() -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(32)


def create_access_token(data: dict, secret_key: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm="HS256")
    return encoded_jwt


def verify_token(token: str, secret_key: str) -> Optional[dict]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload
    except JWTError:
        return None


def generate_order_id() -> str:
    """Generate a unique order ID"""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    random_part = secrets.token_hex(4)
    return f"ORD-{timestamp}-{random_part}"


def sanitize_html(text: str) -> str:
    """Basic HTML sanitization"""
    # Simple implementation - use a library like bleach for production
    replacements = {
        '<': '&lt;',
        '>': '&gt;',
        '&': '&amp;',
        '"': '&quot;',
        "'": '&#x27;',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format a number as currency"""
    if currency == "USD":
        return f"${amount:.2f}"
    return f"{amount:.2f} {currency}"


def calculate_order_total(items: list[dict]) -> float:
    """Calculate total price for order items"""
    total = 0.0
    for item in items:
        price = float(item.get('price', 0))
        quantity = int(item.get('quantity', 1))
        total += price * quantity
    return round(total, 2)


class Logger:
    """Simple logger wrapper"""
    
    def __init__(self, name: str):
        self.name = name
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        print(f"[INFO] {self.name}: {message}", kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        print(f"[ERROR] {self.name}: {message}", kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        print(f"[WARNING] {self.name}: {message}", kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        print(f"[DEBUG] {self.name}: {message}", kwargs)


def get_logger(name: str) -> Logger:
    """Get a logger instance"""
    return Logger(name)
