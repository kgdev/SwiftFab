#!/bin/bash
# 本地运行 SwiftFab 后端脚本

echo "===================="
echo "SwiftFab 本地运行脚本"
echo "===================="

# 设置环境变量
export PORT=8000
export HOST=0.0.0.0
export DATABASE_URL="${DATABASE_URL:-postgresql://swiftfab_user:swiftfab_password@localhost:5432/swiftfab}"
export PYTHONUNBUFFERED=1

# 检查 PostgreSQL 是否运行
echo "检查 PostgreSQL 数据库..."
if command -v docker &> /dev/null; then
    if docker ps --format '{{.Names}}' | grep -q "swiftfab-postgres"; then
        echo "✓ PostgreSQL 数据库正在运行"
    else
        echo "⚠️  PostgreSQL 数据库未运行"
        echo "请运行: ./start_postgres.sh"
        read -p "是否现在启动 PostgreSQL? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ./start_postgres.sh
        else
            echo "警告: 没有数据库，应用可能无法正常工作"
        fi
    fi
else
    echo "⚠️  Docker 未安装，无法自动检查 PostgreSQL"
fi
echo ""

# 如果需要FreeCAD，设置相关环境变量
# Note: Now using CADQuery instead of FreeCAD
echo "✓ Using CADQuery for STEP parsing (no FreeCAD needed)"

# 检查 UV 是否安装
if ! command -v uv &> /dev/null; then
    echo "UV 未安装，正在安装..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# 使用 UV 安装依赖
echo "使用 UV 安装 Python 依赖..."
cd backend
uv pip install -r requirements.txt --system
cd ..

# 运行应用
echo "===================="
echo "启动服务器..."
echo "端口: $PORT"
echo "数据库: $DATABASE_URL"
echo "===================="

uv run python3 backend/main.py

