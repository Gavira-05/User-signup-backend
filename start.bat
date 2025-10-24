@echo off
echo 正在启动用户注册后端服务...

echo 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python环境，请先安装Python
    pause
    exit /b 1
)

echo 检查依赖...
pip show fastapi >nul 2>&1
if %errorlevel% neq 0 (
    echo 安装项目依赖...
    pip install -r requirements.txt
)

echo 启动服务...
uvicorn app.main:app --reload --host 0.0.0.0 --port 16666

pause