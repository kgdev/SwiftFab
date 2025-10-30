# SwiftFab 本地开发环境指南

完整的本地开发环境设置，包括 Frontend、Backend 和 Database

---

## 🚀 快速开始（推荐）

### 一键启动完整开发环境：

```bash
./start_dev.sh
```

这个脚本会自动：
- ✅ 启动 PostgreSQL 数据库
- ✅ 启动 Backend API (端口 8000)
- ✅ 启动 Frontend React 应用 (端口 3000)
- ✅ 配置所有必要的环境变量
- ✅ 安装所有依赖

启动后访问：
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

---

## 📋 管理命令

使用 `manage_dev.sh` 管理开发环境：

```bash
# 查看所有命令
./manage_dev.sh help

# 启动完整环境
./manage_dev.sh start

# 停止所有服务
./manage_dev.sh stop

# 重启所有服务
./manage_dev.sh restart

# 查看状态
./manage_dev.sh status

# 查看日志
./manage_dev.sh logs              # 所有日志
./manage_dev.sh logs backend      # Backend 日志
./manage_dev.sh logs frontend     # Frontend 日志

# 单独启动
./manage_dev.sh backend           # 仅 Backend
./manage_dev.sh frontend          # 仅 Frontend
```

---

## 🔧 分步启动（手动方式）

如果需要更细粒度的控制：

### 步骤 1: 启动 PostgreSQL

```bash
./start_postgres.sh
```

### 步骤 2: 启动 Backend

```bash
./run_local.sh
```

### 步骤 3: 启动 Frontend

```bash
./start_frontend.sh
```

---

## 🐳 方式一：使用 Docker（仅 Backend）

这是最接近 Railway 生产环境的方式，包含完整的 FreeCAD 支持。

### 步骤：

```bash
# 1. 构建 Docker 镜像
cd /home/kgdev/SwiftFab
docker build -t swiftfab-backend .

# 2. 运行容器
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://swiftfab_user:swiftfab_password@host.docker.internal:5432/swiftfab" \
  -e PORT=8000 \
  --name swiftfab-backend \
  swiftfab-backend

# 3. 查看日志
docker logs -f swiftfab-backend

# 4. 测试健康检查
curl http://localhost:8000/api/health

# 5. 停止容器
docker stop swiftfab-backend

# 6. 删除容器
docker rm swiftfab-backend
```

---

## 💻 方式二：直接使用 Python + Node.js

### 快速启动（使用脚本）：

```bash
# 完整环境（推荐）
./start_dev.sh

# 或单独启动
./start_postgres.sh  # 数据库
./run_local.sh       # Backend
./start_frontend.sh  # Frontend
```

### Frontend 配置：

Frontend 使用 React + TypeScript，配置文件在 `frontend/.env`：

```bash
# Frontend 端口
PORT=3000

# Backend API 地址
REACT_APP_API_BASE_URL=http://localhost:8000

# Shopify 配置（可选）
# REACT_APP_SHOPIFY_STORE_DOMAIN=your-shop.myshopify.com
# REACT_APP_SHOPIFY_STOREFRONT_ACCESS_TOKEN=your-token
```

### Backend 配置：

```bash
# 设置数据库 URL
export DATABASE_URL="postgresql://swiftfab_user:swiftfab_password@localhost:5432/swiftfab"

# 运行 Backend
./run_local.sh
```

Backend 配置文件在 `backend/config.json`：

```json
{
  "app": {
    "port": 8000,
    "host": "0.0.0.0"
  },
  "database": {
    "url": "postgresql://..."
  }
}
```

### 手动启动步骤：

```bash
# 1. 创建并激活虚拟环境
python3 -m venv venv
source venv/bin/activate

# 2. 安装依赖
pip install -r backend/requirements.txt

# 3. 设置环境变量
export PORT=8000
export DATABASE_URL="postgresql://user:password@localhost:5432/swiftfab"

# 4. 启动服务器
python3 backend/main.py
```

---

## 环境变量配置

### 必需的环境变量：

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/swiftfab
```

### 可选的环境变量：

```bash
PORT=8000                    # 服务器端口（默认：8000）
HOST=0.0.0.0                # 服务器主机（默认：0.0.0.0）

# Shopify 集成（如果需要）
SHOPIFY_SHOP_DOMAIN=your-shop.myshopify.com
SHOPIFY_CLIENT_ID=your_client_id
SHOPIFY_CLIENT_SECRET=your_client_secret
SHOPIFY_API_VERSION=2025-07

# 安全配置
SECURITY_ADMIN_KEY=swiftfab_admin_2024
```

---

## API 端点测试

### 健康检查：
```bash
curl http://localhost:8000/api/health
```

### 获取报价列表：
```bash
curl http://localhost:8000/api/quotes
```

### 上传 STEP 文件：
```bash
curl -X POST http://localhost:8000/api/quotes \
  -F "file=@path/to/your/file.step" \
  -F "customer_name=Test Customer" \
  -F "customer_email=test@example.com"
```

---

## 数据库设置

### 使用 PostgreSQL（推荐）：

```bash
# 安装 PostgreSQL
sudo apt install postgresql postgresql-contrib

# 创建数据库
sudo -u postgres psql
CREATE DATABASE swiftfab;
CREATE USER swiftfab_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE swiftfab TO swiftfab_user;
\q

# 设置连接字符串
export DATABASE_URL="postgresql://swiftfab_user:your_password@localhost:5432/swiftfab"
```

### 或使用 Docker PostgreSQL：

```bash
docker run -d \
  --name swiftfab-postgres \
  -e POSTGRES_DB=swiftfab \
  -e POSTGRES_USER=swiftfab_user \
  -e POSTGRES_PASSWORD=your_password \
  -p 5432:5432 \
  postgres:15
```

---

## FreeCAD 支持（可选）

如果需要完整的 STEP 文件解析功能，需要安装 FreeCAD：

### Ubuntu/Debian：
```bash
sudo apt install freecad freecad-python3
```

### 设置 FreeCAD 环境变量：
```bash
export FREECAD_USER_HOME=/tmp/freecad
export QT_QPA_PLATFORM=offscreen
export PYTHONPATH="/usr/lib/freecad-python3/lib:/usr/lib/freecad/lib:$PYTHONPATH"
```

---

## 故障排查

### 问题：找不到 CSV 文件
确保 `data/` 目录存在且包含以下文件：
- `final_material_parameters.csv`
- `final_finish_parameters.csv`

### 问题：数据库连接失败
检查 DATABASE_URL 是否正确，确保 PostgreSQL 正在运行

### 问题：端口已被占用
更改端口：`export PORT=8001`

---

## 与 Railway 的对应关系

| Railway 配置 | 本地等效 |
|-------------|---------|
| Dockerfile 构建 | `docker build -t swiftfab-backend .` |
| 启动命令 | `python3 backend/main.py` |
| 健康检查 | `GET /api/health` |
| PORT 环境变量 | `export PORT=8000` |
| DATABASE_URL | 需要本地 PostgreSQL |

