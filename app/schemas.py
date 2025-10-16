from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
import uuid

class PermissionBase(BaseModel):
    name: str
    description: Optional[str] = None

class PermissionCreate(PermissionBase):
    pass

class Permission(PermissionBase):
    id: int
    created_time: datetime

    class Config:
        from_attributes = True

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    permissions: List[int] = []

class Role(RoleBase):
    id: int
    created_time: datetime
    permissions: List[Permission] = []

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None

class UserOut(UserBase):
    id: str
    is_active: bool
    created_time: datetime
    roles: List[Role] = []

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserOut

class ChangePassword(BaseModel):
    old_password: str
    new_password: str

class UserListResponse(BaseModel):
    users: List[UserOut]
    total: int
    skip: int
    limit: int

class AdminUserCreate(UserCreate):
    """管理员创建用户时的请求模型"""
    roles: List[int] = []  # 角色ID列表

class AdminUserUpdate(BaseModel):
    """管理员更新用户时的请求模型"""
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    roles: Optional[List[int]] = None