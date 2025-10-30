# PostgreSQL 本地数据库使用指南

快速在本地启动和管理 PostgreSQL 数据库

---

## 🚀 快速开始

### 一键启动 PostgreSQL：

```bash
./start_postgres.sh
```

这个脚本会：
- ✅ 自动创建并启动 PostgreSQL Docker 容器
- ✅ 配置数据库名称、用户和密码
- ✅ 创建持久化数据卷
- ✅ 显示连接信息

### 启动后的输出：

```
数据库信息：
  主机: localhost
  端口: 5432
  数据库: swiftfab
  用户: swiftfab_user
  密码: swiftfab_password

连接字符串：
  DATABASE_URL=postgresql://swiftfab_user:swiftfab_password@localhost:5432/swiftfab
```

---

## 📋 管理命令

使用 `manage_postgres.sh` 脚本管理数据库：

### 基本操作：

```bash
# 查看所有命令
./manage_postgres.sh help

# 启动数据库
./manage_postgres.sh start

# 停止数据库
./manage_postgres.sh stop

# 重启数据库
./manage_postgres.sh restart

# 查看状态
./manage_postgres.sh status

# 查看日志
./manage_postgres.sh logs

# 显示连接信息
./manage_postgres.sh info
```

### 数据库操作：

```bash
# 连接到数据库（进入 psql 命令行）
./manage_postgres.sh connect

# 备份数据库
./manage_postgres.sh backup

# 恢复数据库
./manage_postgres.sh restore backup_file.sql

# 重置数据库（删除所有数据）
./manage_postgres.sh reset

# 删除容器和所有数据
./manage_postgres.sh remove
```

---

## 🔧 配置环境变量

### 方式一：导出到当前会话

```bash
export DATABASE_URL="postgresql://swiftfab_user:swiftfab_password@localhost:5432/swiftfab"
```

### 方式二：添加到 ~/.bashrc 或 ~/.zshrc

```bash
echo 'export DATABASE_URL="postgresql://swiftfab_user:swiftfab_password@localhost:5432/swiftfab"' >> ~/.bashrc
source ~/.bashrc
```

### 方式三：在 run_local.sh 中使用

`run_local.sh` 脚本会自动使用环境变量或提供默认值。

---

## 🎯 与后端集成

### 启动完整开发环境：

```bash
# 1. 启动 PostgreSQL
./start_postgres.sh

# 2. 设置环境变量
export DATABASE_URL="postgresql://swiftfab_user:swiftfab_password@localhost:5432/swiftfab"

# 3. 启动后端服务
./run_local.sh
```

或者一行命令：

```bash
./start_postgres.sh && export DATABASE_URL="postgresql://swiftfab_user:swiftfab_password@localhost:5432/swiftfab" && ./run_local.sh
```

---

## 💾 数据持久化

数据存储在 Docker volume 中，即使删除容器数据也不会丢失：

```bash
# 查看数据卷
docker volume ls | grep swiftfab

# 查看数据卷详情
docker volume inspect swiftfab-postgres-data
```

如果需要完全删除数据：

```bash
./manage_postgres.sh remove  # 会同时删除容器和数据卷
```

---

## 🔍 数据库操作示例

### 连接到数据库：

```bash
./manage_postgres.sh connect
```

### 常用 SQL 命令：

```sql
-- 列出所有表
\dt

-- 查看表结构
\d table_name

-- 查看所有数据库
\l

-- 切换数据库
\c database_name

-- 退出
\q

-- 查询示例
SELECT * FROM quotes;
SELECT * FROM blob_storage;
```

### 使用 Python 连接：

```python
from sqlalchemy import create_engine

DATABASE_URL = "postgresql://swiftfab_user:swiftfab_password@localhost:5432/swiftfab"
engine = create_engine(DATABASE_URL)

# 测试连接
with engine.connect() as conn:
    result = conn.execute("SELECT version();")
    print(result.fetchone())
```

---

## 🐛 故障排查

### 问题：端口 5432 已被占用

```bash
# 查看占用端口的进程
sudo lsof -i :5432

# 或者修改 start_postgres.sh 中的 DB_PORT
DB_PORT="5433"  # 使用不同端口
```

### 问题：容器无法启动

```bash
# 查看容器日志
docker logs swiftfab-postgres

# 删除并重新创建
./manage_postgres.sh remove
./start_postgres.sh
```

### 问题：连接被拒绝

```bash
# 检查容器是否运行
docker ps | grep swiftfab-postgres

# 检查数据库是否就绪
docker exec swiftfab-postgres pg_isready -U swiftfab_user
```

### 问题：忘记密码

默认配置：
- 用户名: `swiftfab_user`
- 密码: `swiftfab_password`
- 数据库: `swiftfab`

如需修改，编辑 `start_postgres.sh` 脚本中的变量。

---

## 📊 数据库配置

### 默认配置：

| 项目 | 值 |
|-----|-----|
| 容器名称 | swiftfab-postgres |
| 数据库名 | swiftfab |
| 用户名 | swiftfab_user |
| 密码 | swiftfab_password |
| 端口 | 5432 |
| PostgreSQL 版本 | 15 |

### 修改配置：

编辑 `start_postgres.sh` 和 `manage_postgres.sh` 文件：

```bash
DB_NAME="your_db_name"
DB_USER="your_username"
DB_PASSWORD="your_password"
DB_PORT="5432"
```

---

## 🔐 安全建议

### 生产环境注意事项：

1. **更改默认密码**
   ```bash
   # 编辑 start_postgres.sh
   DB_PASSWORD="your_secure_password_here"
   ```

2. **限制网络访问**
   - 只在本地开发时使用 localhost
   - 生产环境使用防火墙规则

3. **定期备份**
   ```bash
   # 设置定时备份
   crontab -e
   # 添加: 0 2 * * * /path/to/manage_postgres.sh backup
   ```

---

## 🌐 远程连接（可选）

如果需要从其他机器连接：

```bash
# 运行容器时绑定到所有网络接口
docker run -d \
  --name swiftfab-postgres \
  -e POSTGRES_DB=swiftfab \
  -e POSTGRES_USER=swiftfab_user \
  -e POSTGRES_PASSWORD=swiftfab_password \
  -p 0.0.0.0:5432:5432 \
  postgres:15
```

**⚠️ 警告：** 生产环境不建议这样做，存在安全风险！

---

## 📚 更多资源

- PostgreSQL 官方文档: https://www.postgresql.org/docs/
- Docker PostgreSQL: https://hub.docker.com/_/postgres
- SQLAlchemy 文档: https://docs.sqlalchemy.org/

---

## ✨ 快速参考

```bash
# 完整开发流程
./start_postgres.sh              # 启动数据库
./manage_postgres.sh info        # 查看连接信息
export DATABASE_URL="..."        # 设置环境变量
./run_local.sh                   # 启动后端

# 日常管理
./manage_postgres.sh status      # 检查状态
./manage_postgres.sh logs        # 查看日志
./manage_postgres.sh backup      # 备份数据
./manage_postgres.sh connect     # 连接数据库

# 清理
./manage_postgres.sh stop        # 停止
./manage_postgres.sh remove      # 完全删除
```


