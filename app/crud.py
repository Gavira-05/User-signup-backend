from sqlalchemy.orm import Session
from . import models, schemas, auth
from datetime import datetime, timedelta
from typing import Optional, List

def get_user(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        hashed_password=hashed_password
    )
    # 查找user角色并赋予
    user_role = db.query(models.Role).filter_by(name="user").first()
    if user_role:
        db_user.roles.append(user_role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not auth.verify_password(password, user.hashed_password):
        return False
    return user

def verify_user(db: Session, user_id: str):
    user = get_user(db, user_id)
    if user:
        user.is_active = True
        db.commit()
        db.refresh(user)
    return user



def update_user(db: Session, user_id: str, user_update: schemas.UserUpdate):
    user = get_user(db, user_id)
    if not user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = auth.get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: str):
    """删除用户"""
    user = get_user(db, user_id)
    if not user:
        return None
    
    db.delete(user)
    db.commit()
    return user

def get_users_with_pagination(db: Session, skip: int = 0, limit: int = 100):
    """获取用户列表，支持分页"""
    total = db.query(models.User).count()
    users = db.query(models.User).offset(skip).limit(limit).all()
    return {"users": users, "total": total, "skip": skip, "limit": limit}

def create_user_by_admin(db: Session, user: schemas.AdminUserCreate):
    """管理员创建用户"""
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        hashed_password=hashed_password
    )
    
    # 添加指定的角色
    if user.roles:
        for role_id in user.roles:
            role = get_role(db, role_id)
            if role:
                db_user.roles.append(role)
    else:
        # 默认添加user角色
        user_role = db.query(models.Role).filter_by(name="user").first()
        if user_role:
            db_user.roles.append(user_role)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_by_admin(db: Session, user_id: str, user_update: schemas.AdminUserUpdate):
    """管理员更新用户"""
    user = get_user(db, user_id)
    if not user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    
    # 处理密码更新
    if "password" in update_data:
        update_data["hashed_password"] = auth.get_password_hash(update_data.pop("password"))
    
    # 处理角色更新
    if "roles" in update_data:
        user.roles.clear()
        for role_id in update_data.pop("roles"):
            role = get_role(db, role_id)
            if role:
                user.roles.append(role)
    
    # 更新其他字段
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user

# 角色和权限相关的CRUD操作
def create_role(db: Session, role: schemas.RoleCreate):
    db_role = models.Role(
        name=role.name,
        description=role.description
    )
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def get_role(db: Session, role_id: int):
    return db.query(models.Role).filter(models.Role.id == role_id).first()

def get_roles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Role).offset(skip).limit(limit).all()

def create_permission(db: Session, permission: schemas.PermissionCreate):
    db_permission = models.Permission(
        name=permission.name,
        description=permission.description
    )
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission

def get_permission(db: Session, permission_id: int):
    return db.query(models.Permission).filter(models.Permission.id == permission_id).first()

def get_permissions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Permission).offset(skip).limit(limit).all()
