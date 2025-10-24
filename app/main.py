from fastapi import FastAPI
from .database import Base, engine, SessionLocal
from .routers import users
from . import crud, schemas, auth
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.exceptions import HTTPException

Base.metadata.create_all(bind=engine)

# 初始化角色
with SessionLocal() as db:
    for role_name, desc in [("user", "普通用户"), ("admin", "管理员")]:
        if not db.query(crud.models.Role).filter_by(name=role_name).first():
            crud.create_role(db, schemas.RoleCreate(name=role_name, description=desc))

# 初始化默认权限
def init_default_permissions():
    with SessionLocal() as db:
        # 创建默认权限
        default_permissions = [
            ("user_read", "查看用户信息"),
            ("user_write", "修改用户信息"),
            ("user_delete", "删除用户"),
            ("admin", "系统管理权限")
        ]
        
        for perm_name, perm_desc in default_permissions:
            if not db.query(crud.models.Permission).filter_by(name=perm_name).first():
                crud.create_permission(db, schemas.PermissionCreate(name=perm_name, description=perm_desc))
        
        # 为admin角色分配所有权限
        admin_role = db.query(crud.models.Role).filter_by(name="admin").first()
        if admin_role:
            all_permissions = db.query(crud.models.Permission).all()
            for permission in all_permissions:
                if permission not in admin_role.permissions:
                    admin_role.permissions.append(permission)
            db.commit()
        
        print("默认权限初始化完成")

# 创建默认管理员用户
def create_admin_user():
    with SessionLocal() as db:
        # 检查是否已存在admin用户
        admin_user = crud.get_user_by_username(db, "admin")
        
        if not admin_user:
            # 创建admin角色（如果不存在）
            admin_role = db.query(crud.models.Role).filter_by(name="admin").first()
            if not admin_role:
                admin_role = crud.create_role(db, schemas.RoleCreate(name="admin", description="系统管理员"))
            
            # 创建admin用户
            admin_user_create = schemas.AdminUserCreate(
                username="admin",
                password="admin123",  # 默认密码，生产环境应该修改
                roles=[admin_role.id]
            )
            
            admin_user = crud.create_user_by_admin(db, admin_user_create)
            print(f"已创建默认管理员用户: {admin_user.username}")
            print("默认密码: admin123")
            print("请在首次登录后修改密码！")
        else:
            print("管理员用户已存在，跳过创建")

# 初始化默认权限
init_default_permissions()

# 创建默认管理员用户
create_admin_user()

app = FastAPI(title="Attack Monitor Backend")

app.include_router(users.router)

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )
