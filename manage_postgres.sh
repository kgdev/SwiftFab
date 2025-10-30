#!/bin/bash
# PostgreSQL 数据库管理脚本

CONTAINER_NAME="swiftfab-postgres"
DB_NAME="swiftfab"
DB_USER="swiftfab_user"
DB_PASSWORD="swiftfab_password"

show_help() {
    echo "PostgreSQL 数据库管理工具"
    echo ""
    echo "用法: ./manage_postgres.sh [命令]"
    echo ""
    echo "命令："
    echo "  start       启动数据库"
    echo "  stop        停止数据库"
    echo "  restart     重启数据库"
    echo "  status      查看状态"
    echo "  logs        查看日志"
    echo "  connect     连接到数据库"
    echo "  backup      备份数据库"
    echo "  restore     恢复数据库"
    echo "  reset       重置数据库（删除所有数据）"
    echo "  remove      删除容器和数据"
    echo "  info        显示连接信息"
    echo "  help        显示此帮助"
    echo ""
}

show_info() {
    echo "======================================"
    echo "数据库连接信息"
    echo "======================================"
    echo "主机: localhost"
    echo "端口: 5432"
    echo "数据库: $DB_NAME"
    echo "用户: $DB_USER"
    echo "密码: $DB_PASSWORD"
    echo ""
    echo "连接字符串:"
    echo "postgresql://${DB_USER}:${DB_PASSWORD}@localhost:5432/${DB_NAME}"
    echo ""
    echo "环境变量设置:"
    echo "export DATABASE_URL=\"postgresql://${DB_USER}:${DB_PASSWORD}@localhost:5432/${DB_NAME}\""
    echo ""
}

check_container() {
    if ! docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        echo "❌ 容器不存在，请先运行: ./start_postgres.sh"
        exit 1
    fi
}

case "$1" in
    start)
        ./start_postgres.sh
        ;;
    
    stop)
        check_container
        echo "停止数据库..."
        docker stop $CONTAINER_NAME
        echo "✓ 数据库已停止"
        ;;
    
    restart)
        check_container
        echo "重启数据库..."
        docker restart $CONTAINER_NAME
        echo "✓ 数据库已重启"
        ;;
    
    status)
        check_container
        if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
            echo "✓ PostgreSQL 正在运行"
            docker exec $CONTAINER_NAME pg_isready -U $DB_USER
        else
            echo "✗ PostgreSQL 已停止"
        fi
        ;;
    
    logs)
        check_container
        docker logs -f $CONTAINER_NAME
        ;;
    
    connect)
        check_container
        echo "连接到数据库..."
        docker exec -it $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME
        ;;
    
    backup)
        check_container
        BACKUP_FILE="backup_${DB_NAME}_$(date +%Y%m%d_%H%M%S).sql"
        echo "备份数据库到 $BACKUP_FILE..."
        docker exec $CONTAINER_NAME pg_dump -U $DB_USER $DB_NAME > $BACKUP_FILE
        echo "✓ 备份完成: $BACKUP_FILE"
        ;;
    
    restore)
        check_container
        if [ -z "$2" ]; then
            echo "用法: ./manage_postgres.sh restore <backup_file.sql>"
            exit 1
        fi
        echo "恢复数据库从 $2..."
        cat "$2" | docker exec -i $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME
        echo "✓ 恢复完成"
        ;;
    
    reset)
        check_container
        read -p "⚠️  确定要重置数据库吗？所有数据将被删除！(yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            echo "重置数据库..."
            docker exec $CONTAINER_NAME psql -U $DB_USER -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"
            docker exec $CONTAINER_NAME psql -U $DB_USER -d postgres -c "CREATE DATABASE $DB_NAME;"
            echo "✓ 数据库已重置"
        else
            echo "操作已取消"
        fi
        ;;
    
    remove)
        read -p "⚠️  确定要删除容器和所有数据吗？(yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            echo "删除容器和数据..."
            docker stop $CONTAINER_NAME 2>/dev/null
            docker rm $CONTAINER_NAME 2>/dev/null
            docker volume rm swiftfab-postgres-data 2>/dev/null
            echo "✓ 已删除"
        else
            echo "操作已取消"
        fi
        ;;
    
    info)
        show_info
        ;;
    
    help|--help|-h|"")
        show_help
        ;;
    
    *)
        echo "未知命令: $1"
        echo "运行 './manage_postgres.sh help' 查看帮助"
        exit 1
        ;;
esac


