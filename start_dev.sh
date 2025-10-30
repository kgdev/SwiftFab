#!/bin/bash
# 统一启动脚本 - 启动完整的本地开发环境

echo "========================================="
echo "SwiftFab 完整开发环境启动脚本"
echo "========================================="
echo ""

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志目录
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"

# PID 文件
POSTGRES_PID_FILE="$LOG_DIR/postgres.pid"
BACKEND_PID_FILE="$LOG_DIR/backend.pid"
FRONTEND_PID_FILE="$LOG_DIR/frontend.pid"

# 清理函数
cleanup() {
    echo ""
    echo "========================================="
    echo "停止所有服务..."
    echo "========================================="
    
    # 停止 frontend
    if [ -f "$FRONTEND_PID_FILE" ]; then
        FRONTEND_PID=$(cat "$FRONTEND_PID_FILE")
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            echo "停止 Frontend (PID: $FRONTEND_PID)..."
            kill $FRONTEND_PID 2>/dev/null
            # 也终止子进程
            pkill -P $FRONTEND_PID 2>/dev/null
        fi
        rm -f "$FRONTEND_PID_FILE"
    fi
    
    # 停止 backend
    if [ -f "$BACKEND_PID_FILE" ]; then
        BACKEND_PID=$(cat "$BACKEND_PID_FILE")
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            echo "停止 Backend (PID: $BACKEND_PID)..."
            kill $BACKEND_PID 2>/dev/null
            pkill -P $BACKEND_PID 2>/dev/null
        fi
        rm -f "$BACKEND_PID_FILE"
    fi
    
    echo "✓ 所有服务已停止"
    exit 0
}

# 注册清理函数
trap cleanup SIGINT SIGTERM

# 步骤 1: 启动 PostgreSQL
echo "步骤 1/3: 检查 PostgreSQL 数据库"
echo "-----------------------------------------"
if command -v docker &> /dev/null; then
    if docker ps --format '{{.Names}}' | grep -q "swiftfab-postgres"; then
        echo -e "${GREEN}✓ PostgreSQL 已运行${NC}"
    else
        echo -e "${YELLOW}启动 PostgreSQL...${NC}"
        ./start_postgres.sh
        if [ $? -ne 0 ]; then
            echo -e "${RED}❌ PostgreSQL 启动失败${NC}"
            exit 1
        fi
        echo -e "${GREEN}✓ PostgreSQL 启动成功${NC}"
    fi
else
    echo -e "${RED}❌ Docker 未安装${NC}"
    exit 1
fi
echo ""

# 等待 PostgreSQL 就绪
sleep 2

# 步骤 2: 启动 Backend
echo "步骤 2/3: 启动 Backend API"
echo "-----------------------------------------"
export DATABASE_URL="postgresql://swiftfab_user:swiftfab_password@localhost:5432/swiftfab"
export PORT=8000
export HOST=0.0.0.0

# 检查 UV 是否安装
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}UV 未安装，正在安装...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# 使用 UV 安装依赖
echo "使用 UV 安装 Python 依赖..."
cd backend
uv pip install -r requirements.txt --system
cd ..

# 启动 backend（后台运行）
echo "启动 Backend 服务器 (http://localhost:8000)..."
uv run python3 backend/main.py > "$LOG_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > "$BACKEND_PID_FILE"

# 等待 backend 启动
echo "等待 Backend 就绪..."
for i in {1..30}; do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend 已就绪 (http://localhost:8000)${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Backend 启动超时${NC}"
        echo "查看日志: tail -f $LOG_DIR/backend.log"
        cleanup
        exit 1
    fi
    sleep 1
done
echo ""

# 步骤 3: 启动 Frontend
echo "步骤 3/3: 启动 Frontend"
echo "-----------------------------------------"
cd frontend || exit 1

export PORT=3000
export REACT_APP_API_BASE_URL=http://localhost:8000

# 检查依赖
if [ ! -d "node_modules" ]; then
    echo "安装 Node.js 依赖..."
    npm install
fi

# 创建 .env 文件
cat > .env << EOF
PORT=3000
REACT_APP_API_BASE_URL=http://localhost:8000
EOF

# 启动 frontend（后台运行）
echo "启动 Frontend 服务器 (http://localhost:3000)..."
BROWSER=none npm start > "$LOG_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > "$FRONTEND_PID_FILE"

# 等待 frontend 启动
echo "等待 Frontend 就绪..."
for i in {1..60}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Frontend 已就绪 (http://localhost:3000)${NC}"
        break
    fi
    if [ $i -eq 60 ]; then
        echo -e "${YELLOW}⚠ Frontend 启动时间较长，请稍候...${NC}"
    fi
    sleep 1
done

cd "$SCRIPT_DIR"
echo ""

# 显示状态
echo "========================================="
echo "✓ 开发环境启动完成！"
echo "========================================="
echo ""
echo "服务地址:"
echo "  Frontend:  http://localhost:3000"
echo "  Backend:   http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
echo "  Database:  postgresql://localhost:5432/swiftfab"
echo ""
echo "日志文件:"
echo "  Backend:   tail -f $LOG_DIR/backend.log"
echo "  Frontend:  tail -f $LOG_DIR/frontend.log"
echo ""
echo "管理命令:"
echo "  查看状态:  ./manage_dev.sh status"
echo "  停止所有:  ./manage_dev.sh stop"
echo "  重启所有:  ./manage_dev.sh restart"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo "========================================="
echo ""

# 显示实时日志
echo "显示 Backend 日志 (Ctrl+C 停止所有服务):"
echo "-----------------------------------------"
tail -f "$LOG_DIR/backend.log" "$LOG_DIR/frontend.log"

