# 数据迁移指南

本指南说明如何迁移 MySQL、Redis、MinIO 的数据。

## 脚本说明

### 1. `backup-data.sh` - 备份脚本
在当前服务器上备份所有数据。

### 2. `restore-data.sh` - 恢复脚本
在新服务器上恢复备份的数据。

### 3. `migrate-data.sh` - 完整迁移脚本
交互式脚本，包含备份、传输、恢复的完整流程。

## 使用方法

### 方法一：使用完整迁移脚本（推荐）

```bash
bash migrate-data.sh
```

然后按照提示选择：
- 选项 1: 仅备份数据
- 选项 2: 仅恢复数据
- 选项 3: 完整迁移流程

### 方法二：手动执行备份和恢复

#### 步骤 1: 在源服务器备份数据

```bash
bash backup-data.sh
```

备份文件将保存在 `./backups/YYYYMMDD_HHMMSS/` 目录下，包含：
- `mysql_backup.sql.gz` - MySQL 数据库备份
- `redis_dump.rdb` - Redis 数据备份
- `minio_data.tar.gz` - MinIO 数据备份
- `backup_info.txt` - 备份信息

#### 步骤 2: 传输备份文件到新服务器

使用 `scp` 或 `rsync` 传输备份目录：

```bash
# 使用 scp
scp -r ./backups/20250109_123456 user@new-server:/path/to/speed-knowledge-server/backups/

# 或使用 rsync
rsync -avz ./backups/20250109_123456 user@new-server:/path/to/speed-knowledge-server/backups/
```

或者压缩后传输：

```bash
cd backups
tar czf 20250109_123456.tar.gz 20250109_123456/
scp 20250109_123456.tar.gz user@new-server:/path/to/speed-knowledge-server/backups/
# 在新服务器上解压
tar xzf 20250109_123456.tar.gz
```

#### 步骤 3: 在新服务器恢复数据

确保新服务器上已经：
1. 安装了 Docker 和 Docker Compose
2. 创建了 `.env` 文件（包含数据库密码等配置）
3. 启动了 Docker Compose 服务（至少启动一次以创建容器）

```bash
bash restore-data.sh ./backups/20250109_123456
```

## 注意事项

### MySQL
- 备份使用 `mysqldump`，支持事务一致性备份
- 恢复前确保数据库已创建
- 如果数据库不存在，需要先创建：
  ```bash
  docker exec -it speed-knowledge-db mysql -uroot -p -e "CREATE DATABASE IF NOT EXISTS speed-knowledge;"
  ```

### Redis
- 备份使用 `BGSAVE` 创建 RDB 快照
- 恢复时需要停止 Redis 服务，复制文件后重启
- 如果 Redis 有持久化配置，确保配置正确

### MinIO
- MinIO 数据存储在 Docker 命名卷中
- 如果直接复制失败，可以手动备份卷：
  ```bash
  # 备份卷
  docker run --rm \
    -v speed-knowledge-server_minio-data:/data \
    -v $(pwd)/backup:/backup \
    alpine tar czf /backup/minio_data.tar.gz -C /data .
  
  # 恢复卷
  docker run --rm \
    -v speed-knowledge-server_minio-data:/data \
    -v $(pwd)/backup:/backup \
    alpine sh -c "cd /data && rm -rf * && tar xzf /backup/minio_data.tar.gz"
  ```

## 环境变量

脚本会从 `.env` 文件读取以下配置（如果存在）：
- `MYSQL_ROOT_PASSWORD` - MySQL root 密码
- `MYSQL_DATABASE` - MySQL 数据库名
- `MYSQL_PORT` - MySQL 端口
- `REDIS_PORT` - Redis 端口
- `MINIO_PORT` - MinIO 端口

如果没有 `.env` 文件，将使用默认值。

## 故障排除

### 问题：容器未运行
**解决**：先启动 Docker Compose 服务
```bash
docker-compose up -d
```

### 问题：权限错误
**解决**：确保脚本有执行权限
```bash
chmod +x backup-data.sh restore-data.sh migrate-data.sh
```

### 问题：MySQL 恢复失败
**解决**：
1. 检查数据库是否存在
2. 检查 root 密码是否正确
3. 检查 SQL 文件是否完整

### 问题：MinIO 数据无法复制
**解决**：使用 Docker 卷备份方法（见上方 MinIO 注意事项）

## 验证迁移

恢复完成后，建议验证数据：

```bash
# 检查 MySQL
docker exec -it speed-knowledge-db mysql -uroot -p -e "USE speed-knowledge; SHOW TABLES;"

# 检查 Redis
docker exec -it speed-knowledge-redis redis-cli DBSIZE

# 检查 MinIO（通过 Web 控制台访问 http://localhost:9090）
```

## 备份文件大小

备份文件大小取决于数据量：
- MySQL: 通常几 MB 到几 GB
- Redis: 通常几 MB 到几百 MB
- MinIO: 取决于存储的文件大小

建议定期清理旧备份以节省空间。

