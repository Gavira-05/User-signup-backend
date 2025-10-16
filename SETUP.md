# 项目设置说明

## 环境要求

- Python 3.8+
- FastAPI
- SQLAlchemy
- 其他依赖见 `requirements.txt`

## 安装依赖
#### 方法一：使用 pip（传统方式）
```bash
pip install -r requirements.txt
```

#### 方法二：使用 uv（推荐，更快）
```bash
uv sync
```

## 运行项目

```bash
# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 16666
```


## 使用说明

### 自动生成API文档

1. **手动生成**：
   ```bash
   python generate_openai_json.py
   ```
   这会生成两个文件：
   - `openapi.json` - 标准OpenAPI格式
   - `openai.json` - AI友好格式

2. **自动生成**（推荐）：
   - 在Windows上，每次 `git push` 时会自动运行 `pre-push.bat`
   - 脚本会自动生成最新的API文档并提交到仓库


### 生成脚本失败
如果遇到导入错误，请确保：
1. 已安装所有依赖：`pip install -r requirements.txt`/`uv sync`
2. 在项目根目录运行脚本
3. Python路径正确

### 文件生成失败
检查：
1. 项目代码是否有语法错误
2. FastAPI应用是否能正常启动
3. 文件写入权限 

### 服务地址
- 服务地址: `http://localhost:16666`
- API文档: `http://localhost:16666/docs`
- 健康检查: `http://localhost:16666/health`
