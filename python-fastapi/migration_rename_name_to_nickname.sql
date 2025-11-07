-- ============================================
-- 数据库迁移脚本：更新 users 表结构
-- 1. 将 name 字段改为 nickname
-- 2. 添加 username 字段
-- 3. 移除 password 字段的唯一约束
-- ============================================
-- ⚠️ 执行前请备份数据库！
-- ⚠️ 如果有现有数据，需要先为每个用户生成 username
-- ============================================

-- 步骤1：检查现有表结构
-- DESCRIBE users;
-- SHOW CREATE TABLE users;

-- 步骤2：添加 username 字段（如果不存在）
-- 如果表中有现有数据，先添加为可空字段，然后更新数据，最后改为非空
-- 如果表是空的，可以直接添加为 NOT NULL
-- 注意：如果 username 字段已存在，此语句会报错，可以跳过
ALTER TABLE users 
ADD COLUMN `username` VARCHAR(50) NULL UNIQUE COMMENT '用户名，用于登录' 
AFTER `email`;

-- 步骤3：如果有现有数据，需要为每个用户生成 username
-- 根据你的业务逻辑生成 username，这里示例使用 email 前缀 + id 确保唯一性
-- 注意：确保生成的 username 不会重复
-- 如果表是空的，可以跳过此步骤
UPDATE users SET username = CONCAT(SUBSTRING_INDEX(email, '@', 1), '_', id) WHERE username IS NULL;

-- 步骤4：将 username 设置为非空（在所有数据都有 username 后）
-- 如果步骤3没有数据需要更新，可以跳过此步骤，直接使用 NOT NULL 添加字段
ALTER TABLE users 
MODIFY COLUMN `username` VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名，用于登录';

-- 步骤5：如果表中有 name 字段，将其重命名为 nickname
-- 注意：如果 name 字段不存在，此语句会报错，可以跳过
ALTER TABLE users 
CHANGE COLUMN `name` `nickname` VARCHAR(255) NULL COMMENT '昵称，可选，不唯一';

-- 步骤6：为 username 添加索引（如果还没有）
-- MySQL 5.7+ 支持，如果版本较老可能需要手动检查
-- 注意：UNIQUE 约束会自动创建索引，但如果需要额外的普通索引，可以使用此语句
-- ALTER TABLE users ADD INDEX `ix_users_username` (`username`);

-- 步骤7：移除 password 字段的唯一约束（如果存在）
-- 先查看表结构：SHOW CREATE TABLE users;
-- 找到 password 字段上的唯一索引名称，然后删除
-- 例如：ALTER TABLE users DROP INDEX `password`;
-- 或者：ALTER TABLE users DROP INDEX `ix_users_password`;

-- 验证表结构
-- DESCRIBE users;
-- 或
-- SHOW CREATE TABLE users;
