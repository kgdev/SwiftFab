# SwiftFab 本地运行指南

根据 Railway 配置在本地运行后端服务

## 方式一：使用 Docker（推荐）

这是最接近 Railway 生产环境的方式，包含完整的 FreeCAD 支持。

### 步骤：

```bash
# 1. 构建 Docker 镜像
cd /home/kgdev/SwiftFab
docker build -t swiftfab-backend .

# 2. 运行容器
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:password@host.docker.internal:5432/swiftfab" \
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

## 方式二：直接使用 Python

### 快速启动（使用脚本）：

```bash
# 设置数据库 URL（必需）
export DATABASE_URL="postgresql://user:password@localhost:5432/swiftfab"

# 运行启动脚本
./run_local.sh
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

