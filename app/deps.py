from .database import SessionLocal
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from . import auth, crud, schemas

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")  # 注意tokenUrl要和你的登录接口一致

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)) -> schemas.UserOut:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = auth.verify_token(token)
    if payload is None:
        raise credentials_exception
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    user = crud.get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user

def get_current_admin_user(current_user: schemas.UserOut = Depends(get_current_user)) -> schemas.UserOut:
    """检查当前用户是否为管理员"""
    admin_roles = ["admin", "administrator"]
    user_roles = [role.name for role in current_user.roles]
    
    if not any(role in admin_roles for role in user_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin role required."
        )
    return current_user
