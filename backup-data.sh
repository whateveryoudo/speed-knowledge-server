#!/bin/bash

# 数据备份脚本
# 用于备份 MySQL、Redis、MinIO 的数据

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="${BACKUP_DIR}/${TIMESTAMP}"

# 从 .env 文件读取配置（如果存在）
if [ -f .env ]; then
    source .env
fi

# 默认值
MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD:-change_me}
MYSQL_DATABASE=${MYSQL_DATABASE:-speed-knowledge}

# 自动检测容器名称（优先使用 docker-compose 定义的名称，如果不存在则查找运行中的容器）
MYSQL_CONTAINER=$(docker ps --format "{{.Names}}" | grep -E "mysql|db" | grep -v phpmyadmin | head -1 || echo "speed-knowledge-db")
REDIS_CONTAINER=$(docker ps --format "{{.Names}}" | grep -E "redis" | grep -v redisinsight | head -1 || echo "speed-knowledge-redis")
MINIO_CONTAINER=$(docker ps --format "{{.Names}}" | grep -iE "minio|mystifying" | head -1 || echo "speed-knowledge-minio")

# 如果未设置密码，尝试从容器环境变量中读取
if [ -z "${MYSQL_ROOT_PASSWORD}" ] || [ "${MYSQL_ROOT_PASSWORD}" = "change_me" ]; then
    if [ -n "${MYSQL_CONTAINER}" ] && docker ps | grep -q "${MYSQL_CONTAINER}"; then
        MYSQL_ROOT_PASSWORD=$(docker inspect "${MYSQL_CONTAINER}" 2>/dev/null | grep -i "MYSQL_ROOT_PASSWORD" | head -1 | cut -d'=' -f2 | tr -d '",' || echo "")
        if [ -n "${MYSQL_ROOT_PASSWORD}" ]; then
            echo -e "${GREEN}从容器环境变量读取 MySQL 密码${NC}"
        fi
    fi
fi

# 如果仍然没有密码，提示用户输入
if [ -z "${MYSQL_ROOT_PASSWORD}" ] || [ "${MYSQL_ROOT_PASSWORD}" = "change_me" ]; then
    read -sp "请输入 MySQL root 密码（留空使用默认值 change_me）: " MYSQL_PASSWORD_INPUT
    echo ""
    MYSQL_ROOT_PASSWORD=${MYSQL_PASSWORD_INPUT:-change_me}
fi

echo -e "${YELLOW}检测到的容器:${NC}"
echo -e "${YELLOW}  MySQL: ${MYSQL_CONTAINER}${NC}"
echo -e "${YELLOW}  Redis: ${REDIS_CONTAINER}${NC}"
echo -e "${YELLOW}  MinIO: ${MINIO_CONTAINER}${NC}"
echo ""

echo -e "${GREEN}开始备份数据...${NC}"
echo -e "${YELLOW}备份目录: ${BACKUP_PATH}${NC}"

# 创建备份目录
mkdir -p "${BACKUP_PATH}"

# 1. 备份 MySQL
echo -e "${GREEN}[1/3] 备份 MySQL 数据...${NC}"
if docker ps | grep -q "${MYSQL_CONTAINER}"; then
    docker exec "${MYSQL_CONTAINER}" mysqldump \
        -uroot \
        -p"${MYSQL_ROOT_PASSWORD}" \
        --single-transaction \
        --routines \
        --triggers \
        "${MYSQL_DATABASE}" > "${BACKUP_PATH}/mysql_backup.sql"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ MySQL 备份完成: ${BACKUP_PATH}/mysql_backup.sql${NC}"
        # 压缩 SQL 文件
        gzip -f "${BACKUP_PATH}/mysql_backup.sql"
        echo -e "${GREEN}✓ MySQL 备份已压缩${NC}"
    else
        echo -e "${RED}✗ MySQL 备份失败${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠ MySQL 容器未运行，跳过备份${NC}"
fi

# 2. 备份 Redis（已禁用）
# echo -e "${GREEN}[2/3] 备份 Redis 数据...${NC}"
echo -e "${YELLOW}[2/3] 跳过 Redis 备份（已禁用）${NC}"

# 3. 备份 MinIO
echo -e "${GREEN}[2/2] 备份 MinIO 数据...${NC}"
if docker ps | grep -q "${MINIO_CONTAINER}"; then
    # 方法1: 尝试直接复制（如果容器内数据可访问）
    docker cp "${MINIO_CONTAINER}:/data" "${BACKUP_PATH}/minio_data" 2>/dev/null && {
        echo "压缩 MinIO 数据（这可能需要一些时间）..."
        tar czf "${BACKUP_PATH}/minio_data.tar.gz" -C "${BACKUP_PATH}" minio_data
        rm -rf "${BACKUP_PATH}/minio_data"
        echo -e "${GREEN}✓ MinIO 备份完成（方法1）${NC}"
    } || {
        # 方法2: 使用 Docker 卷直接备份（推荐）
        echo "使用 Docker 卷备份 MinIO 数据..."
        # 尝试多种方式获取卷名称
        VOLUME_NAME=$(docker inspect "${MINIO_CONTAINER}" 2>/dev/null | grep -A 10 '"Mounts"' | grep '"Name"' | head -1 | awk -F'"' '{print $4}' || echo "")
        
        # 如果没找到命名卷，尝试查找所有可能的卷
        if [ -z "${VOLUME_NAME}" ]; then
            VOLUME_NAME=$(docker volume ls --format "{{.Name}}" | grep -iE "minio|data" | head -1 || echo "")
        fi
        
        # 如果还是没找到，尝试使用默认名称
        if [ -z "${VOLUME_NAME}" ]; then
            VOLUME_NAME="speed-knowledge-server_minio-data"
        fi
        
        # 检查卷是否存在
        if docker volume inspect "${VOLUME_NAME}" >/dev/null 2>&1; then
            docker run --rm \
                -v "${VOLUME_NAME}:/data:ro" \
                -v "$(pwd)/${BACKUP_PATH}:/backup" \
                alpine sh -c "cd /data && tar czf /backup/minio_data.tar.gz ." 2>/dev/null && {
                echo -e "${GREEN}✓ MinIO 备份完成（Docker 卷: ${VOLUME_NAME}）${NC}"
            } || {
                echo -e "${YELLOW}⚠ MinIO 卷备份失败，尝试直接复制容器数据${NC}"
                # 再次尝试直接复制
                docker cp "${MINIO_CONTAINER}:/data" "${BACKUP_PATH}/minio_data" 2>/dev/null && {
                    tar czf "${BACKUP_PATH}/minio_data.tar.gz" -C "${BACKUP_PATH}" minio_data
                    rm -rf "${BACKUP_PATH}/minio_data"
                    echo -e "${GREEN}✓ MinIO 备份完成（容器复制）${NC}"
                } || {
                    echo -e "${YELLOW}⚠ MinIO 备份失败，请手动备份${NC}"
                    echo -e "${YELLOW}手动备份命令:${NC}"
                    echo -e "${YELLOW}docker run --rm -v ${VOLUME_NAME}:/data:ro -v \$(pwd)/${BACKUP_PATH}:/backup alpine tar czf /backup/minio_data.tar.gz -C /data .${NC}"
                }
            }
        else
            echo -e "${YELLOW}⚠ MinIO 卷不存在，尝试直接复制容器数据${NC}"
            docker cp "${MINIO_CONTAINER}:/data" "${BACKUP_PATH}/minio_data" 2>/dev/null && {
                tar czf "${BACKUP_PATH}/minio_data.tar.gz" -C "${BACKUP_PATH}" minio_data
                rm -rf "${BACKUP_PATH}/minio_data"
                echo -e "${GREEN}✓ MinIO 备份完成（容器复制）${NC}"
            } || {
                echo -e "${YELLOW}⚠ 无法备份 MinIO 数据${NC}"
            }
        fi
    }
else
    # 即使容器未运行，也尝试备份卷
    echo "MinIO 容器未运行，尝试直接备份 Docker 卷..."
    VOLUME_NAME="speed-knowledge-server_minio-data"
    docker volume inspect "${VOLUME_NAME}" >/dev/null 2>&1 && {
        docker run --rm \
            -v "${VOLUME_NAME}:/data:ro" \
            -v "$(pwd)/${BACKUP_PATH}:/backup" \
            alpine sh -c "cd /data && tar czf /backup/minio_data.tar.gz ." 2>/dev/null && {
            echo -e "${GREEN}✓ MinIO 备份完成（Docker 卷）${NC}"
        } || {
            echo -e "${YELLOW}⚠ 无法备份 MinIO 数据${NC}"
        }
    } || {
        echo -e "${YELLOW}⚠ MinIO 卷不存在，跳过备份${NC}"
    }
fi

# 创建备份信息文件
cat > "${BACKUP_PATH}/backup_info.txt" << EOF
备份时间: $(date)
MySQL 数据库: ${MYSQL_DATABASE}
备份路径: ${BACKUP_PATH}

恢复说明:
1. MySQL: 使用 restore-data.sh 脚本或手动导入 mysql_backup.sql.gz
2. Redis: 已跳过备份（Redis 数据通常可以重新生成）
3. MinIO: 解压 minio_data.tar.gz 到新容器的 /data 目录
EOF

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}备份完成！${NC}"
echo -e "${GREEN}备份位置: ${BACKUP_PATH}${NC}"
echo -e "${GREEN}========================================${NC}"

# 显示备份文件大小
echo -e "${YELLOW}备份文件大小:${NC}"
du -sh "${BACKUP_PATH}"/* 2>/dev/null || true

