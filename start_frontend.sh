#!/bin/bash
# 启动 Frontend 开发服务器

echo "======================================"
echo "SwiftFab Frontend 启动脚本"
echo "======================================"

# 进入 frontend 目录
cd "$(dirname "$0")/frontend" || exit 1

# 设置环境变量
export PORT=${PORT:-3000}
export REACT_APP_API_BASE_URL=${REACT_APP_API_BASE_URL:-http://localhost:8000}

echo ""
echo "配置信息："
echo "  Frontend 端口: $PORT"
echo "  Backend API: $REACT_APP_API_BASE_URL"
echo ""

# 检查 node_modules 是否存在
if [ ! -d "node_modules" ]; then
    echo "首次运行，安装依赖..."
    echo "这可能需要几分钟时间..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
    echo "✓ 依赖安装完成"
    echo ""
fi

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "创建 .env 文件..."
    cat > .env << EOF
# Frontend 配置
PORT=$PORT
REACT_APP_API_BASE_URL=$REACT_APP_API_BASE_URL

# Shopify 配置（可选）
# REACT_APP_SHOPIFY_STORE_DOMAIN=your-shop.myshopify.com
# REACT_APP_SHOPIFY_STOREFRONT_ACCESS_TOKEN=your-token
EOF
    echo "✓ 已创建 .env 文件"
    echo ""
fi

echo "======================================"
echo "启动 React 开发服务器..."
echo "======================================"
echo ""
echo "访问地址: http://localhost:$PORT"
echo ""
echo "提示："
echo "  - 按 Ctrl+C 停止服务器"
echo "  - 修改代码会自动重新加载"
echo "  - 确保 Backend 已在 $REACT_APP_API_BASE_URL 运行"
echo ""

# 启动开发服务器
npm start

