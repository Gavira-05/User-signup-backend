#!/usr/bin/env python3
"""
自动生成openapi.json文件的脚本
使用FastAPI的OpenAPI工具根据实际项目接口自动生成
"""

import json
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from fastapi.openapi.utils import get_openapi
    from app.main import app
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保已安装所有依赖: pip install -r requirements.txt")
    sys.exit(1)

def generate_openapi_json():
    """使用FastAPI的OpenAPI工具生成API文档"""
    
    try:
        # 获取OpenAPI规范
        openapi_schema = get_openapi(
            title="Attack Monitor Backend API",
            version="1.0.0",
            description="攻击监控系统后端API接口",
            routes=app.routes,
        )
        
        # 添加自定义信息
        openapi_schema["info"]["x-generated-at"] = datetime.now().isoformat()
        openapi_schema["info"]["x-description"] = "此文件由FastAPI自动生成，用于AI生成前端代码"
        
        # 添加自定义标签说明
        openapi_schema["tags"] = [
            {
                "name": "users",
                "description": "用户管理相关接口，包括注册、登录、信息管理等"
            }
        ]
        
        # 添加安全方案说明
        if "components" not in openapi_schema:
            openapi_schema["components"] = {}
        
        if "securitySchemes" not in openapi_schema["components"]:
            openapi_schema["components"]["securitySchemes"] = {}
        
        openapi_schema["components"]["securitySchemes"]["bearerAuth"] = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT Bearer Token认证"
        }
        
        # 为需要认证的接口添加安全要求
        for path, path_item in openapi_schema["paths"].items():
            for method, operation in path_item.items():
                if method.lower() in ["get", "put", "delete"] and path != "/users/register" and path != "/users/login":
                    if "security" not in operation:
                        operation["security"] = [{"bearerAuth": []}]
        
        # 写入文件
        with open('openapi.json', 'w', encoding='utf-8') as f:
            json.dump(openapi_schema, f, ensure_ascii=False, indent=2)
        
        print("✅ openapi.json 文件已自动生成")
        print(f"📊 包含 {len(openapi_schema['paths'])} 个接口路径")
        print(f"📝 生成时间: {openapi_schema['info']['x-generated-at']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        return False

def generate_ai_friendly_json():
    """生成AI友好的格式，基于OpenAPI规范但更易于AI理解"""
    
    try:
        # 首先获取OpenAPI规范
        openapi_schema = get_openapi(
            title="Attack Monitor Backend API",
            version="1.0.0",
            description="攻击监控系统后端API接口",
            routes=app.routes,
        )
        
        # 转换为AI友好的格式
        ai_friendly_data = {
            "api_info": {
                "title": openapi_schema["info"]["title"],
                "description": openapi_schema["info"]["description"],
                "version": openapi_schema["info"]["version"],
                "base_url": "http://localhost:8000",
                "generated_at": datetime.now().isoformat(),
                "generated_by": "FastAPI OpenAPI Utils"
            },
            "authentication": {
                "type": "Bearer Token",
                "description": "大部分接口需要在请求头中包含Authorization: Bearer <access_token>"
            },
            "endpoints": [],
            "data_models": {},
            "error_responses": {
                "400": "Bad Request - 请求参数错误",
                "401": "Unauthorized - 未授权访问",
                "403": "Forbidden - 权限不足",
                "404": "Not Found - 资源不存在",
                "409": "Conflict - 资源冲突（如用户名已存在）",
                "500": "Internal Server Error - 服务器内部错误"
            },
            "usage_examples": {
                "login": {
                    "description": "用户登录示例",
                    "curl": "curl -X POST 'http://localhost:8000/users/login' -H 'Content-Type: application/json' -d '{\"username\": \"testuser\", \"password\": \"password123\"}'",
                    "javascript": "fetch('http://localhost:8000/users/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username: 'testuser', password: 'password123' }) })"
                },
                "get_user_info": {
                    "description": "获取用户信息示例",
                    "curl": "curl -X GET 'http://localhost:8000/users/me' -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'",
                    "javascript": "fetch('http://localhost:8000/users/me', { headers: { 'Authorization': 'Bearer YOUR_ACCESS_TOKEN' } })"
                }
            }
        }
        
        # 转换路径为端点
        for path, path_item in openapi_schema["paths"].items():
            for method, operation in path_item.items():
                if method.lower() in ["get", "post", "put", "delete"]:
                    endpoint = {
                        "path": path,
                        "method": method.upper(),
                        "description": operation.get("summary", operation.get("description", "")),
                        "tags": operation.get("tags", [])
                    }
                    
                    # 添加请求体
                    if "requestBody" in operation:
                        if "content" in operation["requestBody"]:
                            for content_type, content in operation["requestBody"]["content"].items():
                                if "schema" in content:
                                    endpoint["request_body"] = content["schema"]
                                    break
                    
                    # 添加响应
                    if "responses" in operation:
                        endpoint["responses"] = {}
                        for status_code, response in operation["responses"].items():
                            endpoint["responses"][status_code] = {
                                "description": response.get("description", ""),
                                "content": response.get("content", {})
                            }
                    
                    # 添加安全要求
                    if "security" in operation:
                        endpoint["security"] = operation["security"]
                    
                    ai_friendly_data["endpoints"].append(endpoint)
        
        # 转换数据模型
        if "components" in openapi_schema and "schemas" in openapi_schema["components"]:
            for schema_name, schema in openapi_schema["components"]["schemas"].items():
                ai_friendly_data["data_models"][schema_name] = schema
        
        # 写入AI友好的文件
        with open('openai.json', 'w', encoding='utf-8') as f:
            json.dump(ai_friendly_data, f, ensure_ascii=False, indent=2)
        
        print("✅ openai.json 文件已生成（AI友好格式）")
        print(f"📊 包含 {len(ai_friendly_data['endpoints'])} 个接口")
        print(f"📝 生成时间: {ai_friendly_data['api_info']['generated_at']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        return False

if __name__ == "__main__":
    print("🔄 正在生成API文档...")
    
    # 生成标准OpenAPI格式
    success1 = generate_openapi_json()
    
    # 生成AI友好格式
    success2 = generate_ai_friendly_json()
    
    if success1 and success2:
        print("\n🎉 所有文件生成成功！")
        print("📁 openapi.json - 标准OpenAPI格式")
        print("📁 openai.json - AI友好格式")
    else:
        print("\n❌ 部分文件生成失败")
        sys.exit(1) 