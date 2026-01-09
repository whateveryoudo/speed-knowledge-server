#!/bin/bash

# 数据恢复脚本
# 用于恢复 MySQL、Redis、MinIO 的数据

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查参数
if [ $# -eq 0 ]; then
    echo -e "${RED}错误: 请指定备份目录路径${NC}"
    echo "用法: $0 <备份目录路径>"
    echo "示例: $0 ./backups/20250109_123456"
    exit 1
fi

BACKUP_PATH="$1"

if [ ! -d "${BACKUP_PATH}" ]; then
    echo -e "${RED}错误: 备份目录不存在: ${BACKUP_PATH}${NC}"
    exit 1
fi

# 从 .env 文件读取配置（如果存在）
if [ -f .env ]; then
    source .env
fi

# 默认值
MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD:-change_me}
MYSQL_DATABASE=${MYSQL_DATABASE:-speed-knowledge}

# 自动检测容器名称
MYSQL_CONTAINER=$(docker ps --format "{{.Names}}" | grep -E "mysql|db" | grep -v phpmyadmin | head -1 || echo "speed-knowledge-db")
REDIS_CONTAINER=$(docker ps --format "{{.Names}}" | grep -E "redis" | grep -v redisinsight | head -1 || echo "speed-knowledge-redis")
MINIO_CONTAINER=$(docker ps --format "{{.Names}}" | grep -E "minio" | head -1 || echo "speed-knowledge-minio")

echo -e "${YELLOW}检测到的容器:${NC}"
echo -e "${YELLOW}  MySQL: ${MYSQL_CONTAINER}${NC}"
echo -e "${YELLOW}  Redis: ${REDIS_CONTAINER}${NC}"
echo -e "${YELLOW}  MinIO: ${MINIO_CONTAINER}${NC}"
echo ""

echo -e "${GREEN}开始恢复数据...${NC}"
echo -e "${YELLOW}备份目录: ${BACKUP_PATH}${NC}"

# 确认操作
read -p "这将覆盖现有数据，是否继续? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "操作已取消"
    exit 0
fi

# 1. 恢复 MySQL
echo -e "${GREEN}[1/3] 恢复 MySQL 数据...${NC}"
if docker ps | grep -q "${MYSQL_CONTAINER}"; then
    MYSQL_BACKUP="${BACKUP_PATH}/mysql_backup.sql.gz"
    MYSQL_BACKUP_UNCOMPRESSED="${BACKUP_PATH}/mysql_backup.sql"
    
    if [ -f "${MYSQL_BACKUP}" ]; then
        echo "解压 MySQL 备份文件..."
        gunzip -c "${MYSQL_BACKUP}" > "${MYSQL_BACKUP_UNCOMPRESSED}"
        
        echo "导入 MySQL 数据..."
        docker exec -i "${MYSQL_CONTAINER}" mysql \
            -uroot \
            -p"${MYSQL_ROOT_PASSWORD}" \
            "${MYSQL_DATABASE}" < "${MYSQL_BACKUP_UNCOMPRESSED}"
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ MySQL 数据恢复完成${NC}"
            rm -f "${MYSQL_BACKUP_UNCOMPRESSED}"
        else
            echo -e "${RED}✗ MySQL 数据恢复失败${NC}"
            exit 1
        fi
    elif [ -f "${MYSQL_BACKUP_UNCOMPRESSED}" ]; then
        echo "导入 MySQL 数据..."
        docker exec -i "${MYSQL_CONTAINER}" mysql \
            -uroot \
            -p"${MYSQL_ROOT_PASSWORD}" \
            "${MYSQL_DATABASE}" < "${MYSQL_BACKUP_UNCOMPRESSED}"
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ MySQL 数据恢复完成${NC}"
        else
            echo -e "${RED}✗ MySQL 数据恢复失败${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}⚠ 未找到 MySQL 备份文件，跳过恢复${NC}"
    fi
else
    echo -e "${YELLOW}⚠ MySQL 容器未运行，跳过恢复${NC}"
fi

# 2. 恢复 Redis
echo -e "${GREEN}[2/3] 恢复 Redis 数据...${NC}"
if docker ps | grep -q "${REDIS_CONTAINER}"; then
    REDIS_BACKUP="${BACKUP_PATH}/redis_dump.rdb"
    REDIS_DATA_DIR="${BACKUP_PATH}/redis_data"
    
    if [ -f "${REDIS_BACKUP}" ]; then
        echo "停止 Redis 服务..."
        docker stop "${REDIS_CONTAINER}" || true
        
        echo "复制 Redis 备份文件..."
        docker cp "${REDIS_BACKUP}" "${REDIS_CONTAINER}:/data/dump.rdb"
        
        echo "启动 Redis 服务..."
        docker start "${REDIS_CONTAINER}"
        
        echo -e "${GREEN}✓ Redis 数据恢复完成${NC}"
    elif [ -d "${REDIS_DATA_DIR}" ]; then
        echo "停止 Redis 服务..."
        docker stop "${REDIS_CONTAINER}" || true
        
        echo "复制 Redis 数据目录..."
        docker cp "${REDIS_DATA_DIR}/." "${REDIS_CONTAINER}:/data/"
        
        echo "启动 Redis 服务..."
        docker start "${REDIS_CONTAINER}"
        
        echo -e "${GREEN}✓ Redis 数据恢复完成${NC}"
    else
        echo -e "${YELLOW}⚠ 未找到 Redis 备份文件，跳过恢复${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Redis 容器未运行，跳过恢复${NC}"
fi

# 3. 恢复 MinIO
echo -e "${GREEN}[3/3] 恢复 MinIO 数据...${NC}"
MINIO_BACKUP="${BACKUP_PATH}/minio_data.tar.gz"
MINIO_DATA_DIR="${BACKUP_PATH}/minio_data"

if [ -f "${MINIO_BACKUP}" ]; then
    echo "停止 MinIO 服务..."
    docker stop "${MINIO_CONTAINER}" 2>/dev/null || true
    
    # 获取卷名称
    VOLUME_NAME=$(docker inspect "${MINIO_CONTAINER}" 2>/dev/null | grep -A 10 "Mounts" | grep "Name" | head -1 | awk -F'"' '{print $4}' || echo "speed-knowledge-server_minio-data")
    
    # 方法1: 使用 Docker 卷直接恢复（推荐）
    echo "使用 Docker 卷恢复 MinIO 数据..."
    docker run --rm \
        -v "${VOLUME_NAME}:/data" \
        -v "$(pwd)/${BACKUP_PATH}:/backup" \
        alpine sh -c "cd /data && rm -rf * && tar xzf /backup/minio_data.tar.gz" 2>/dev/null && {
        echo -e "${GREEN}✓ MinIO 数据恢复完成（Docker 卷）${NC}"
    } || {
        # 方法2: 通过容器复制
        echo "尝试通过容器恢复 MinIO 数据..."
        mkdir -p "${MINIO_DATA_DIR}"
        tar xzf "${MINIO_BACKUP}" -C "${BACKUP_PATH}"
        
        docker cp "${MINIO_DATA_DIR}/." "${MINIO_CONTAINER}:/data/" 2>/dev/null && {
            echo -e "${GREEN}✓ MinIO 数据恢复完成（容器复制）${NC}"
        } || {
            echo -e "${YELLOW}⚠ MinIO 容器未运行，请先启动容器或手动恢复${NC}"
            echo -e "${YELLOW}手动恢复命令:${NC}"
            echo -e "${YELLOW}docker run --rm -v ${VOLUME_NAME}:/data -v \$(pwd)/${BACKUP_PATH}:/backup alpine sh -c 'cd /data && rm -rf * && tar xzf /backup/minio_data.tar.gz'${NC}"
        }
        rm -rf "${MINIO_DATA_DIR}"
    }
    
    echo "启动 MinIO 服务..."
    docker start "${MINIO_CONTAINER}" 2>/dev/null || docker-compose up -d minio 2>/dev/null || true
    
elif [ -d "${MINIO_DATA_DIR}" ]; then
    echo "停止 MinIO 服务..."
    docker stop "${MINIO_CONTAINER}" 2>/dev/null || true
    
    echo "复制 MinIO 数据..."
    docker cp "${MINIO_DATA_DIR}/." "${MINIO_CONTAINER}:/data/" 2>/dev/null || {
        echo -e "${YELLOW}⚠ 无法通过容器复制，请使用 Docker 卷方式${NC}"
    }
    
    echo "启动 MinIO 服务..."
    docker start "${MINIO_CONTAINER}" 2>/dev/null || docker-compose up -d minio 2>/dev/null || true
    
    echo -e "${GREEN}✓ MinIO 数据恢复完成${NC}"
else
    echo -e "${YELLOW}⚠ 未找到 MinIO 备份文件，跳过恢复${NC}"
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}数据恢复完成！${NC}"
echo -e "${GREEN}========================================${NC}"

