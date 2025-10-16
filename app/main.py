from fastapi import FastAPI
from .database import Base, engine, SessionLocal
from .routers import users
from . import crud, schemas
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.exceptions import HTTPException

Base.metadata.create_all(bind=engine)

# 初始化角色
with SessionLocal() as db:
    for role_name, desc in [("user", "普通用户"), ("admin", "管理员")]:
        if not db.query(crud.models.Role).filter_by(name=role_name).first():
            crud.create_role(db, schemas.RoleCreate(name=role_name, description=desc))

app = FastAPI(title="Attack Monitor Backend")

app.include_router(users.router)

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )
