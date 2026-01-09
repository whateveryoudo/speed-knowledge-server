#!/bin/bash

# 数据迁移脚本（完整流程）
# 包含备份和恢复的完整流程，适用于迁移到新服务器

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}    数据迁移脚本${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "此脚本将帮助您迁移 MySQL、Redis、MinIO 数据"
echo ""
echo "请选择操作:"
echo "1) 备份数据（在当前服务器）"
echo "2) 恢复数据（在新服务器）"
echo "3) 完整迁移（备份 + 传输提示）"
read -p "请输入选项 (1/2/3): " option

case $option in
    1)
        echo -e "${GREEN}执行备份操作...${NC}"
        bash "$(dirname "$0")/backup-data.sh"
        ;;
    2)
        read -p "请输入备份目录路径: " backup_path
        bash "$(dirname "$0")/restore-data.sh" "$backup_path"
        ;;
    3)
        echo -e "${GREEN}执行完整迁移流程...${NC}"
        
        # 步骤1: 备份
        echo -e "${YELLOW}[步骤 1/3] 备份数据...${NC}"
        bash "$(dirname "$0")/backup-data.sh"
        
        # 获取最新备份目录
        LATEST_BACKUP=$(ls -td ./backups/*/ 2>/dev/null | head -1)
        if [ -z "$LATEST_BACKUP" ]; then
            echo -e "${RED}错误: 未找到备份目录${NC}"
            exit 1
        fi
        
        LATEST_BACKUP=$(echo "$LATEST_BACKUP" | sed 's:/*$::')
        
        echo -e "${GREEN}✓ 备份完成: ${LATEST_BACKUP}${NC}"
        echo ""
        
        # 步骤2: 传输提示
        echo -e "${YELLOW}[步骤 2/3] 传输备份文件到新服务器${NC}"
        echo -e "${BLUE}请使用以下方法之一将备份文件传输到新服务器:${NC}"
        echo ""
        echo "方法1: 使用 scp"
        echo "  scp -r ${LATEST_BACKUP} user@new-server:/path/to/speed-knowledge-server/"
        echo ""
        echo "方法2: 使用 rsync"
        echo "  rsync -avz ${LATEST_BACKUP} user@new-server:/path/to/speed-knowledge-server/backups/"
        echo ""
        echo "方法3: 压缩后传输"
        BACKUP_NAME=$(basename "$LATEST_BACKUP")
        echo "  cd backups && tar czf ${BACKUP_NAME}.tar.gz ${BACKUP_NAME}/"
        echo "  scp ${BACKUP_NAME}.tar.gz user@new-server:/path/to/speed-knowledge-server/backups/"
        echo "  # 在新服务器上解压: tar xzf ${BACKUP_NAME}.tar.gz"
        echo ""
        read -p "传输完成后，按 Enter 继续..."
        
        # 步骤3: 恢复
        echo -e "${YELLOW}[步骤 3/3] 在新服务器上恢复数据${NC}"
        echo -e "${BLUE}在新服务器上运行以下命令:${NC}"
        echo "  cd /path/to/speed-knowledge-server"
        echo "  bash restore-data.sh ${LATEST_BACKUP}"
        echo ""
        echo -e "${GREEN}迁移流程说明完成！${NC}"
        ;;
    *)
        echo -e "${RED}无效选项${NC}"
        exit 1
        ;;
esac

