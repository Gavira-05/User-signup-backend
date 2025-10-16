@echo off
REM Git pre-push hook for Windows to automatically generate API documentation

echo 🔄 正在生成API文档文件...

REM 运行生成脚本
python generate_openai_json.py

REM 检查脚本是否成功运行
if %ERRORLEVEL% EQU 0 (
    echo ✅ API文档生成成功
    
    REM 将生成的文件添加到当前提交
    git add openapi.json
    git add openai.json
    
    REM 如果有变化，创建一个新的提交
    git diff --cached --quiet
    if %ERRORLEVEL% NEQ 0 (
        git commit -m "自动更新API文档文件 (openapi.json + openai.json)"
        echo ✅ 已提交更新的API文档文件
    ) else (
        echo ℹ️  API文档文件无变化
    )
) else (
    echo ❌ API文档生成失败
    exit /b 1
) 