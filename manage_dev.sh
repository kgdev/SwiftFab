#!/bin/bash
# 开发环境管理脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
BACKEND_PID_FILE="$LOG_DIR/backend.pid"
FRONTEND_PID_FILE="$LOG_DIR/frontend.pid"

show_help() {
    echo "SwiftFab 开发环境管理工具"
    echo ""
    echo "用法: ./manage_dev.sh [命令]"
    echo ""
    echo "命令："
    echo "  start       启动完整开发环境 (PostgreSQL + Backend + Frontend)"
    echo "  stop        停止所有服务"
    echo "  restart     重启所有服务"
    echo "  status      查看服务状态"
    echo "  logs        查看日志"
    echo "  backend     仅启动 Backend"
    echo "  frontend    仅启动 Frontend"
    echo "  help        显示此帮助"
    echo ""
}

check_service() {
    local service_name=$1
    local pid_file=$2
    local port=$3
    
    if [ -f "$pid_file" ]; then
        PID=$(cat "$pid_file")
        if ps -p $PID > /dev/null 2>&1; then
            echo "✓ $service_name 运行中 (PID: $PID, 端口: $port)"
            return 0
        else
            echo "✗ $service_name 已停止 (进程不存在)"
            rm -f "$pid_file"
            return 1
        fi
    else
        echo "✗ $service_name 未运行"
        return 1
    fi
}

stop_service() {
    local service_name=$1
    local pid_file=$2
    
    if [ -f "$pid_file" ]; then
        PID=$(cat "$pid_file")
        if ps -p $PID > /dev/null 2>&1; then
            echo "停止 $service_name (PID: $PID)..."
            kill $PID 2>/dev/null
            pkill -P $PID 2>/dev/null
            sleep 2
            if ps -p $PID > /dev/null 2>&1; then
                echo "强制停止 $service_name..."
                kill -9 $PID 2>/dev/null
            fi
            echo "✓ $service_name 已停止"
        fi
        rm -f "$pid_file"
    else
        echo "✗ $service_name 未运行"
    fi
}

case "$1" in
    start)
        echo "启动完整开发环境..."
        ./start_dev.sh
        ;;
    
    stop)
        echo "停止所有服务..."
        stop_service "Frontend" "$FRONTEND_PID_FILE"
        stop_service "Backend" "$BACKEND_PID_FILE"
        ./manage_postgres.sh stop
        echo "✓ 所有服务已停止"
        ;;
    
    restart)
        echo "重启所有服务..."
        $0 stop
        sleep 2
        $0 start
        ;;
    
    status)
        echo "======================================"
        echo "服务状态"
        echo "======================================"
        
        # PostgreSQL
        if command -v docker &> /dev/null; then
            if docker ps --format '{{.Names}}' | grep -q "swiftfab-postgres"; then
                echo "✓ PostgreSQL 运行中 (端口: 5432)"
            else
                echo "✗ PostgreSQL 未运行"
            fi
        fi
        
        # Backend
        check_service "Backend" "$BACKEND_PID_FILE" "8000"
        
        # Frontend
        check_service "Frontend" "$FRONTEND_PID_FILE" "3000"
        
        echo ""
        echo "服务地址:"
        echo "  Frontend:  http://localhost:3000"
        echo "  Backend:   http://localhost:8000"
        echo "  API Docs:  http://localhost:8000/docs"
        ;;
    
    logs)
        if [ -z "$2" ]; then
            echo "查看所有日志..."
            tail -f "$LOG_DIR/backend.log" "$LOG_DIR/frontend.log" 2>/dev/null
        elif [ "$2" = "backend" ]; then
            tail -f "$LOG_DIR/backend.log" 2>/dev/null
        elif [ "$2" = "frontend" ]; then
            tail -f "$LOG_DIR/frontend.log" 2>/dev/null
        else
            echo "用法: ./manage_dev.sh logs [backend|frontend]"
        fi
        ;;
    
    backend)
        echo "启动 Backend..."
        ./run_local.sh
        ;;
    
    frontend)
        echo "启动 Frontend..."
        ./start_frontend.sh
        ;;
    
    help|--help|-h|"")
        show_help
        ;;
    
    *)
        echo "未知命令: $1"
        echo "运行 './manage_dev.sh help' 查看帮助"
        exit 1
        ;;
esac

