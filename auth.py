from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from bson import ObjectId
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_HOURS
from database import users_collection

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    # Ensure password is a string
    if isinstance(plain_password, bytes):
        plain_password = plain_password.decode('utf-8')
    
    # Handle bcrypt 72-byte limit
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # Convert hashed_password to bytes if it's a string
    if isinstance(hashed_password, str):
        hashed_password_bytes = hashed_password.encode('utf-8')
    else:
        hashed_password_bytes = hashed_password
    
    # Use bcrypt directly for verification
    try:
        return bcrypt.checkpw(password_bytes, hashed_password_bytes)
    except Exception:
        # Fallback to passlib if bcrypt fails
        return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password - handles bcrypt's 72-byte limit"""
    # Ensure password is a string
    if isinstance(password, bytes):
        password = password.decode('utf-8')
    
    # Convert to bytes to check length
    password_bytes = password.encode('utf-8')
    
    # Truncate to 72 bytes if necessary (bcrypt limitation)
    # CRITICAL: bcrypt will fail if password > 72 bytes
    if len(password_bytes) > 72:
        # Truncate bytes to exactly 72 bytes
        password_bytes = password_bytes[:72]
        # Decode back to string, handling potential incomplete UTF-8 sequences
        password = password_bytes.decode('utf-8', errors='ignore')
    
    # Use bcrypt directly with bytes to ensure proper handling
    # Generate salt and hash
    salt = bcrypt.gensalt()
    # Ensure password_bytes is exactly <= 72 bytes
    password_bytes_final = password.encode('utf-8')
    if len(password_bytes_final) > 72:
        password_bytes_final = password_bytes_final[:72]
    
    # Hash using bcrypt directly
    hashed = bcrypt.hashpw(password_bytes_final, salt)
    
    # Return as string (passlib format: $2b$...)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get the current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise credentials_exception
    return user

