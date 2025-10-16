from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, crud, auth, deps
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=schemas.UserOut, status_code=201)
def register(register_req: schemas.UserCreate, db: Session = Depends(deps.get_db)):
    if crud.get_user_by_username(db, register_req.username):
        raise HTTPException(status_code=409, detail="Username already registered")
    user = crud.create_user(db, register_req)
    return user

@router.post("/login", response_model=schemas.LoginResponse, status_code=200)
def login(user_in: schemas.UserLogin, db: Session = Depends(deps.get_db)):
    user = crud.authenticate_user(db, user_in.username, user_in.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = auth.create_access_token({"sub": user.username})
    logger.info(f"User {user.username} logged in successfully")
    return schemas.LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=schemas.UserOut.from_orm(user)
    )

@router.get("/debug-token")
def debug_token(token: str = Depends(deps.oauth2_scheme)):
    """
    调试接口：检查token的状态，不进行用户验证
    """
    try:
        payload = auth.verify_token(token)
        if payload is None:
            return {"status": "invalid", "message": "Token verification failed"}
        
        username = payload.get("sub")
        if username is None:
            return {"status": "invalid", "message": "Token missing 'sub' field"}
        
        # 检查是否过期
        if auth.is_token_expired(token):
            return {"status": "expired", "message": "Token has expired", "username": username}
        
        return {
            "status": "valid", 
            "message": "Token is valid", 
            "username": username,
            "payload": payload
        }
    except Exception as e:
        return {"status": "error", "message": f"Error processing token: {str(e)}"}

@router.get("/verify-token", response_model=schemas.UserOut, status_code=200)
def verify_token(current_user: schemas.UserOut = Depends(deps.get_current_user)):
    """
    验证token是否有效，如果有效则返回当前用户信息
    前端可以定期调用此接口来验证token状态
    """
    return current_user

@router.post("/refresh-token", response_model=schemas.LoginResponse, status_code=200)
def refresh_token(current_user: schemas.UserOut = Depends(deps.get_current_user)):
    """
    刷新token，生成新的access_token
    前端可以在token即将过期时调用此接口
    """
    access_token = auth.create_access_token({"sub": current_user.username})
    return schemas.LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=current_user
    )

# 具体路径必须放在通配符路径之前
@router.get("/me", response_model=schemas.UserOut, status_code=200)
def get_current_user_info(current_user: schemas.UserOut = Depends(deps.get_current_user)):
    return current_user

@router.put("/me", response_model=schemas.UserOut, status_code=200)
def update_current_user_info(
    user_update: schemas.UserUpdate,
    current_user: schemas.UserOut = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    update_data = user_update.dict(exclude_unset=True)
    if "username" in update_data:
        if crud.get_user_by_username(db, update_data["username"]):
            raise HTTPException(status_code=409, detail="Username already registered")
        user = crud.get_user(db, current_user.id)
        user.username = update_data["username"]
        db.commit()
        db.refresh(user)
        return user
    return crud.update_user(db, current_user.id, user_update)

@router.put("/me/password", status_code=200)
def change_current_user_password(
    data: schemas.ChangePassword,
    current_user: schemas.UserOut = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    user = crud.get_user(db, current_user.id)
    if not auth.verify_password(data.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    user.hashed_password = auth.get_password_hash(data.new_password)
    db.commit()
    db.refresh(user)
    return {"message": "Password updated successfully"}

# 通配符路径放在最后
@router.get("/{user_id}", response_model=schemas.UserOut, status_code=200)
def get_user_info(
    user_id: str,
    current_user: schemas.UserOut = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    if current_user.id != user_id and "admin" not in [role.name for role in current_user.roles]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=schemas.UserOut, status_code=200)
def update_user_info(
    user_id: str,
    user_update: schemas.UserUpdate,
    current_user: schemas.UserOut = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    if current_user.id != user_id and "admin" not in [role.name for role in current_user.roles]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    update_data = user_update.dict(exclude_unset=True)
    if "username" in update_data:
        if crud.get_user_by_username(db, update_data["username"]):
            raise HTTPException(status_code=409, detail="Username already registered")
        user.username = update_data["username"]
        db.commit()
        db.refresh(user)
    return user

@router.put("/{user_id}/password", status_code=200)
def change_password(
    user_id: str,
    data: schemas.ChangePassword,
    current_user: schemas.UserOut = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    if current_user.id != user_id and "admin" not in [role.name for role in current_user.roles]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if "admin" not in [role.name for role in current_user.roles]:
        if not auth.verify_password(data.old_password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Old password is incorrect")
    user.hashed_password = auth.get_password_hash(data.new_password)
    db.commit()
    db.refresh(user)
    return {"message": "Password updated successfully"}

# 管理员接口 - 用户管理
@router.get("/admin/users", response_model=schemas.UserListResponse, status_code=200)
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: schemas.UserOut = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db)
):
    """管理员获取所有用户列表"""
    result = crud.get_users_with_pagination(db, skip=skip, limit=limit)
    return result

@router.post("/admin/users", response_model=schemas.UserOut, status_code=201)
def create_user_by_admin(
    user_data: schemas.AdminUserCreate,
    current_user: schemas.UserOut = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db)
):
    """管理员创建新用户"""
    if crud.get_user_by_username(db, user_data.username):
        raise HTTPException(status_code=409, detail="Username already registered")
    
    user = crud.create_user_by_admin(db, user_data)
    return user

@router.get("/admin/users/{user_id}", response_model=schemas.UserOut, status_code=200)
def get_user_by_admin(
    user_id: str,
    current_user: schemas.UserOut = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db)
):
    """管理员获取指定用户信息"""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/admin/users/{user_id}", response_model=schemas.UserOut, status_code=200)
def update_user_by_admin(
    user_id: str,
    user_update: schemas.AdminUserUpdate,
    current_user: schemas.UserOut = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db)
):
    """管理员更新用户信息"""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 检查用户名是否已存在（如果要更新用户名）
    if user_update.username and user_update.username != user.username:
        if crud.get_user_by_username(db, user_update.username):
            raise HTTPException(status_code=409, detail="Username already registered")
    
    updated_user = crud.update_user_by_admin(db, user_id, user_update)
    return updated_user

@router.delete("/admin/users/{user_id}", status_code=200)
def delete_user_by_admin(
    user_id: str,
    current_user: schemas.UserOut = Depends(deps.get_current_admin_user),
    db: Session = Depends(deps.get_db)
):
    """管理员删除用户"""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 防止管理员删除自己
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    deleted_user = crud.delete_user(db, user_id)
    return {"message": f"User {deleted_user.username} deleted successfully"}

