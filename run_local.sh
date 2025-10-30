#!/bin/bash
# 本地运行 SwiftFab 后端脚本

echo "===================="
echo "SwiftFab 本地运行脚本"
echo "===================="

# 设置环境变量
export PORT=8000
export HOST=0.0.0.0
export DATABASE_URL="${DATABASE_URL:-postgresql://user:password@localhost:5432/swiftfab}"
export PYTHONUNBUFFERED=1

# 如果需要FreeCAD，设置相关环境变量
if command -v freecad &> /dev/null; then
    export FREECAD_USER_HOME=/tmp/freecad
    mkdir -p $FREECAD_USER_HOME
    export QT_QPA_PLATFORM=offscreen
    echo "✓ FreeCAD 已找到"
else
    echo "⚠ FreeCAD 未安装 (部分功能可能不可用)"
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装 Python 依赖..."
pip install -r backend/requirements.txt

# 运行应用
echo "===================="
echo "启动服务器..."
echo "端口: $PORT"
echo "数据库: $DATABASE_URL"
echo "===================="

python3 backend/main.py

