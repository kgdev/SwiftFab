#!/bin/bash
# PostgreSQL 本地快速启动脚本

echo "======================================"
echo "PostgreSQL 本地数据库启动脚本"
echo "======================================"

# 数据库配置
DB_NAME="swiftfab"
DB_USER="swiftfab_user"
DB_PASSWORD="swiftfab_password"
DB_PORT="5432"
CONTAINER_NAME="swiftfab-postgres"

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    echo "Ubuntu/Debian: sudo apt install docker.io"
    exit 1
fi

# 检查容器是否已存在
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "容器已存在，检查状态..."
    
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        echo "✓ PostgreSQL 已在运行"
        echo ""
        echo "数据库信息："
        echo "  主机: localhost"
        echo "  端口: $DB_PORT"
        echo "  数据库: $DB_NAME"
        echo "  用户: $DB_USER"
        echo "  密码: $DB_PASSWORD"
        echo ""
        echo "连接字符串："
        echo "  postgresql://${DB_USER}:${DB_PASSWORD}@localhost:${DB_PORT}/${DB_NAME}"
        exit 0
    else
        echo "启动已有容器..."
        docker start $CONTAINER_NAME
        sleep 2
        echo "✓ PostgreSQL 已启动"
    fi
else
    echo "创建新的 PostgreSQL 容器..."
    docker run -d \
      --name $CONTAINER_NAME \
      -e POSTGRES_DB=$DB_NAME \
      -e POSTGRES_USER=$DB_USER \
      -e POSTGRES_PASSWORD=$DB_PASSWORD \
      -p $DB_PORT:5432 \
      -v swiftfab-postgres-data:/var/lib/postgresql/data \
      postgres:15
    
    if [ $? -eq 0 ]; then
        echo "✓ PostgreSQL 容器创建成功"
        echo "等待数据库初始化..."
        sleep 5
    else
        echo "❌ 创建容器失败"
        exit 1
    fi
fi

# 检查数据库是否可用
echo "检查数据库连接..."
for i in {1..10}; do
    if docker exec $CONTAINER_NAME pg_isready -U $DB_USER > /dev/null 2>&1; then
        echo "✓ 数据库已就绪"
        break
    fi
    echo "等待数据库启动... ($i/10)"
    sleep 2
done

echo ""
echo "======================================"
echo "PostgreSQL 启动成功！"
echo "======================================"
echo ""
echo "数据库信息："
echo "  主机: localhost"
echo "  端口: $DB_PORT"
echo "  数据库: $DB_NAME"
echo "  用户: $DB_USER"
echo "  密码: $DB_PASSWORD"
echo ""
echo "连接字符串："
echo "  DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@localhost:${DB_PORT}/${DB_NAME}"
echo ""
echo "导出环境变量："
echo "  export DATABASE_URL=\"postgresql://${DB_USER}:${DB_PASSWORD}@localhost:${DB_PORT}/${DB_NAME}\""
echo ""
echo "常用命令："
echo "  查看日志: docker logs -f $CONTAINER_NAME"
echo "  停止数据库: docker stop $CONTAINER_NAME"
echo "  启动数据库: docker start $CONTAINER_NAME"
echo "  连接数据库: docker exec -it $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME"
echo "  删除容器: docker stop $CONTAINER_NAME && docker rm $CONTAINER_NAME"
echo ""


