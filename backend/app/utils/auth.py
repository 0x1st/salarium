from datetime import datetime, timedelta
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from tortoise.exceptions import DoesNotExist

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import JWT_SECRET, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from ..models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def _truncate_password_utf8(password: str, max_bytes: int = 72) -> str:
    password_bytes = password.encode("utf-8")
    if len(password_bytes) <= max_bytes:
        return password

    truncated_bytes = password_bytes[:max_bytes]
    try:
        return truncated_bytes.decode("utf-8")
    except UnicodeDecodeError:
        for i in range(max_bytes - 1, 0, -1):
            try:
                return password_bytes[:i].decode("utf-8")
            except UnicodeDecodeError:
                continue
    return ""


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Note: We apply the same truncation logic as in hash_password
    to ensure consistency during verification.
    """
    plain_password = _truncate_password_utf8(plain_password, 72)
    
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Note: bcrypt has a maximum password length of 72 bytes. 
    We truncate the password to ensure it doesn't exceed this limit
    while preserving UTF-8 encoding integrity.
    """
    try:
        password = _truncate_password_utf8(password, 72)
        return pwd_context.hash(password)
    except Exception as e:
        print(f"DEBUG: Error in hash_password: {type(e).__name__}: {str(e)}")
        # Fallback: simple truncation
        password = _truncate_password_utf8(password, 72)
        return pwd_context.hash(password)


def create_access_token(subject: dict, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode = {"exp": expire, **subject}
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    try:
        user = await User.get(username=username)
        return user
    except DoesNotExist:
        raise credentials_exception
