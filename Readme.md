# 用户相关接口文档

---

## 用户身份说明
- 系统有两种用户身份：
  - 普通用户（user）：注册后默认身份，拥有基础操作权限。
  - 管理员（admin）：拥有更高权限，可进行用户管理等操作。
- 用户的身份通过`roles`字段体现，例如：`["user"]`或`["admin"]`。

## 字段说明
- `id`：用户唯一标识符，使用UUID格式的字符串。
- `is_active`：用户账号是否激活，若为false则无法登录（如被封禁）。
- `roles`：用户身份列表，包含`user`和/或`admin`。

---

## 用户注册与登录说明

### 注册
- 只需提供用户名和密码即可注册。

### 登录
- 只需用户名和密码。
- 登录成功后直接返回 access token。

### 用户信息修改
- 只允许修改用户名和密码。


---

## 1. 用户注册

- **接口路径**：`POST /users/register`
- **请求体**（JSON）：
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **成功返回**（201）：
  ```json
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "string",
    "is_active": true,
    "created_time": "2024-01-01T00:00:00",
    "roles": ["user"]
  }
  ```
- **失败返回**（409）：
  ```json
  {
    "message": "Username already registered"
  }
  ```
- **说明**：注册新用户只需提供用户名和密码。

---

## 2. 用户登录

- **接口路径**：`POST /users/login`
- **请求体**（JSON）：
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **成功返回**（200）：
  ```json
  {
    "access_token": "string",
    "token_type": "bearer",
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "username": "string",
      "is_active": true,
      "created_time": "2024-01-01T00:00:00",
      "roles": ["user"]
    }
  }
  ```
- **失败返回**（401）：
  ```json
  {
    "message": "Invalid credentials"
  }
  ```
- **说明**：登录时使用用户名和密码进行验证，登录成功返回访问令牌和用户信息。

---

## 3. Token验证

- **接口路径**：`GET /users/verify-token`
- **请求头**：
  ```
  Authorization: Bearer <access_token>
  ```
- **成功返回**（200）：
  ```json
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "string",
    "is_active": true,
    "created_time": "2024-01-01T00:00:00",
    "roles": ["user"]
  }
  ```
- **失败返回**（401）：
  ```json
  {
    "message": "Could not validate credentials"
  }
  ```
- **说明**：验证token是否有效，如果有效则返回当前用户信息。前端可以定期调用此接口来验证token状态。

---

## 4. Token刷新

- **接口路径**：`POST /users/refresh-token`
- **请求头**：
  ```
  Authorization: Bearer <access_token>
  ```
- **成功返回**（200）：
  ```json
  {
    "access_token": "string",
    "token_type": "bearer",
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "username": "string",
      "is_active": true,
      "created_time": "2024-01-01T00:00:00",
      "roles": ["user"]
    }
  }
  ```
- **失败返回**（401）：
  ```json
  {
    "message": "Could not validate credentials"
  }
  ```
- **说明**：刷新token，生成新的access_token。前端可以在token即将过期时调用此接口。

---

## 5. 获取指定用户信息

- **接口路径**：`GET /users/{user_id}`
- **请求头**：
  ```
  Authorization: Bearer <access_token>
  ```
- **成功返回**（200）：
  ```json
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "string",
    "is_active": true,
    "created_time": "2024-01-01T00:00:00",
    "roles": ["user", "admin"]
  }
  ```
- **失败返回**（403）：
  ```json
  {
    "message": "Not enough permissions"
  }
  ```
- **失败返回**（404）：
  ```json
  {
    "message": "User not found"
  }
  ```
- **说明**：获取指定用户的信息。用户只能查看自己的信息，管理员可以查看所有用户信息。

---

## 6. 修改指定用户信息

- **接口路径**：`PUT /users/{user_id}`
- **请求头**：
  ```
  Authorization: Bearer <access_token>
  ```
- **请求体**（JSON，可选字段）：
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **成功返回**（200）：
  ```json
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "string",
    "is_active": true,
    "created_time": "2024-01-01T00:00:00",
    "roles": ["user"]
  }
  ```
- **失败返回**（403）：
  ```json
  {
    "message": "Not enough permissions"
  }
  ```
- **失败返回**（404）：
  ```json
  {
    "message": "User not found"
  }
  ```
- **说明**：修改指定用户的信息。用户只能修改自己的信息，管理员可以修改所有用户信息。

---

## 7. 修改指定用户密码

- **接口路径**：`PUT /users/{user_id}/password`
- **请求头**：
  ```
  Authorization: Bearer <access_token>
  ```
- **请求体**（JSON）：
  ```json
  {
    "old_password": "string",
    "new_password": "string"
  }
  ```
- **成功返回**（200）：
  ```json
  {
    "message": "Password updated successfully"
  }
  ```
- **失败返回**（403）：
  ```json
  {
    "message": "Not enough permissions"
  }
  ```
- **失败返回**（404）：
  ```json
  {
    "message": "User not found"
  }
  ```
- **失败返回**（400）：
  ```json
  {
    "message": "Old password is incorrect"
  }
  ```
- **说明**：修改指定用户的密码。用户只能修改自己的密码，管理员可以修改所有用户密码。管理员修改密码不需要验证旧密码。

---

## 8. 获取当前用户信息

- **接口路径**：`GET /users/me`
- **请求头**：
  ```
  Authorization: Bearer <access_token>
  ```
- **成功返回**（200）：
  ```json
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "string",
    "is_active": true,
    "created_time": "2024-01-01T00:00:00",
    "roles": ["user", "admin"]
  }
  ```
- **说明**：获取当前登录用户的信息，`roles`字段反映用户身份。

---

## 9. 修改当前用户信息

- **接口路径**：`PUT /users/me`
- **请求头**：
  ```
  Authorization: Bearer <access_token>
  ```
- **请求体**（JSON，可选字段）：
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **成功返回**（200）：
  ```json
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "string",
    "is_active": true,
    "created_time": "2024-01-01T00:00:00",
    "roles": ["user"]
  }
  ```
- **说明**：只允许修改用户名和密码。

---

## 10. 修改当前用户密码

- **接口路径**：`PUT /users/me/password`
- **请求头**：
  ```
  Authorization: Bearer <access_token>
  ```
- **请求体**（JSON）：
  ```json
  {
    "old_password": "string",
    "new_password": "string"
  }
  ```
- **成功返回**（200）：
  ```json
  {
    "message": "Password updated successfully"
  }
  ```
- **失败返回**（400）：
  ```json
  {
    "message": "Old password is incorrect"
  }
  ```
- **说明**：需要输入旧密码和新密码。

--- 