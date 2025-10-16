from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional
import secrets
import os

# 从环境变量获取密钥，如果没有则使用默认值（生产环境必须设置）
SECRET_KEY = os.getenv("SECRET_KEY", "YOUR_SECRET_KEY_CHANGE_ME_IN_PRODUCTION")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 12  # 12小时，更长的token有效期

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def is_token_expired(token: str) -> bool:
    """检查token是否已过期"""
    payload = verify_token(token)
    if payload is None:
        return True
    exp = payload.get("exp")
    if exp is None:
        return True
    return datetime.utcnow() > datetime.fromtimestamp(exp)

def generate_verification_code() -> str:
    return secrets.token_urlsafe(16)

def generate_reset_token() -> str:
    return secrets.token_urlsafe(32)