-- MySQL dump 10.13  Distrib 8.4.5, for Linux (aarch64)
--
-- Host: localhost    Database: speed-knowledge
-- ------------------------------------------------------
-- Server version	8.4.5

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `attachment`
--

DROP TABLE IF EXISTS `attachment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `attachment` (
  `id` varchar(36) NOT NULL COMMENT '主键',
  `file_name` varchar(255) DEFAULT NULL COMMENT '附件名称',
  `file_type` varchar(255) DEFAULT NULL COMMENT '附件类型',
  `object_name` varchar(255) NOT NULL COMMENT '文件的唯一标识路径',
  `file_size` bigint DEFAULT NULL COMMENT '附件大小',
  `bucket_name` varchar(255) NOT NULL COMMENT 'bucket名',
  `user_id` int NOT NULL COMMENT '上传者',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `ix_attachment_file_name` (`file_name`),
  KEY `ix_attachment_id` (`id`),
  KEY `ix_attachment_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `chat_message`
--

DROP TABLE IF EXISTS `chat_message`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `chat_message` (
  `id` varchar(36) NOT NULL COMMENT '消息id',
  `session_id` varchar(36) DEFAULT NULL COMMENT '会话id',
  `content` text NOT NULL COMMENT '消息内容',
  `role` varchar(20) NOT NULL COMMENT '消息角色',
  `type` varchar(20) NOT NULL COMMENT '消息类型',
  `created_at` datetime DEFAULT NULL COMMENT '创建时间',
  `updated_at` datetime DEFAULT NULL COMMENT '更新时间',
  `link_question` varchar(255) DEFAULT NULL COMMENT '关联问题(用于重新生成答案)',
  `suggestions` json DEFAULT NULL COMMENT '建议列表',
  PRIMARY KEY (`id`),
  KEY `ix_chat_message_id` (`id`),
  KEY `ix_chat_message_session_id` (`session_id`),
  CONSTRAINT `chat_message_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `chat_session` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `chat_session`
--

DROP TABLE IF EXISTS `chat_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `chat_session` (
  `id` varchar(36) NOT NULL COMMENT '会话id',
  `user_id` int DEFAULT NULL COMMENT '用户id',
  `title` varchar(255) NOT NULL COMMENT '会话标题',
  `status` varchar(20) NOT NULL COMMENT '会话状态',
  `last_message_preview` varchar(100) DEFAULT NULL COMMENT '最后一条消息预览(通常用来做摘要)',
  `created_at` datetime DEFAULT NULL COMMENT '创建时间',
  `updated_at` datetime DEFAULT NULL COMMENT '更新时间',
  `deleted_at` datetime DEFAULT NULL COMMENT '删除时间(NULL表示未删除)',
  PRIMARY KEY (`id`),
  KEY `ix_chat_session_id` (`id`),
  KEY `ix_chat_session_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `collaborator`
--

DROP TABLE IF EXISTS `collaborator`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `collaborator` (
  `id` varchar(36) NOT NULL COMMENT '主键',
  `knowledge_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '所属知识库',
  `document_id` varchar(36) DEFAULT NULL COMMENT '所属文档',
  `user_id` int NOT NULL COMMENT '所属用户',
  `role` int NOT NULL COMMENT '角色',
  `target_type` varchar(30) NOT NULL COMMENT '目标类型:知识库/文档',
  `status` int NOT NULL COMMENT '状态',
  `source` int NOT NULL COMMENT '来源',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `ix_collaborator_id` (`id`),
  KEY `ix_collaborator_knowledge_id` (`knowledge_id`),
  KEY `ix_collaborator_user_id` (`user_id`),
  KEY `ix_collaborator_document_id` (`document_id`),
  CONSTRAINT `collaborator_ibfk_1` FOREIGN KEY (`knowledge_id`) REFERENCES `knowledge_base` (`id`) ON DELETE CASCADE,
  CONSTRAINT `collaborator_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `collaborator_ibfk_3` FOREIGN KEY (`document_id`) REFERENCES `document_base` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `collect`
--

DROP TABLE IF EXISTS `collect`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `collect` (
  `id` varchar(36) NOT NULL,
  `user_id` int NOT NULL COMMENT '用户ID',
  `resource_type` varchar(20) NOT NULL COMMENT '资源类型',
  `knowledge_id` varchar(36) DEFAULT NULL COMMENT '知识库ID',
  `document_id` varchar(36) DEFAULT NULL COMMENT '文档ID',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uix_user_knowledge_document` (`user_id`,`knowledge_id`,`document_id`),
  KEY `ix_collect_document_id` (`document_id`),
  KEY `ix_collect_knowledge_id` (`knowledge_id`),
  KEY `ix_collect_user_id` (`user_id`),
  CONSTRAINT `collect_ibfk_1` FOREIGN KEY (`document_id`) REFERENCES `document_base` (`id`) ON DELETE CASCADE,
  CONSTRAINT `collect_ibfk_2` FOREIGN KEY (`knowledge_id`) REFERENCES `knowledge_base` (`id`) ON DELETE CASCADE,
  CONSTRAINT `collect_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `document_base`
--

DROP TABLE IF EXISTS `document_base`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `document_base` (
  `id` varchar(36) NOT NULL COMMENT '主键',
  `user_id` int NOT NULL COMMENT '所属用户',
  `knowledge_id` varchar(36) NOT NULL COMMENT '所属知识库',
  `name` varchar(128) NOT NULL COMMENT '文档名称',
  `slug` varchar(64) NOT NULL COMMENT '文档短链',
  `type` varchar(10) NOT NULL COMMENT '文档类型',
  `is_public` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否公开',
  `content_updated_at` datetime DEFAULT NULL COMMENT '内容最近更新时间',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  `view_count` int NOT NULL COMMENT '浏览次数',
  `deleted_at` datetime DEFAULT NULL COMMENT '删除时间(NULL表示未删除)',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_knowledge_id_document_slug` (`knowledge_id`,`slug`),
  KEY `ix_document_base_id` (`id`),
  KEY `ix_document_base_knowledge_id` (`knowledge_id`),
  KEY `ix_document_base_user_id` (`user_id`),
  CONSTRAINT `document_base_ibfk_1` FOREIGN KEY (`knowledge_id`) REFERENCES `knowledge_base` (`id`) ON DELETE CASCADE,
  CONSTRAINT `document_base_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `document_content`
--

DROP TABLE IF EXISTS `document_content`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `document_content` (
  `id` varchar(36) NOT NULL COMMENT '主键',
  `document_id` varchar(36) NOT NULL COMMENT '所属文档',
  `content` longblob NOT NULL COMMENT '文档内容(为协同编辑的的二进制数据)',
  `content_updated_at` datetime DEFAULT NULL COMMENT '内容最近更新时间',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  `node_json` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '文档内容(为协同编辑的的二进制json数据)',
  PRIMARY KEY (`id`),
  KEY `ix_document_content_document_id` (`document_id`),
  KEY `ix_document_content_id` (`id`),
  CONSTRAINT `document_content_ibfk_1` FOREIGN KEY (`document_id`) REFERENCES `document_base` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `document_edit_history`
--

DROP TABLE IF EXISTS `document_edit_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `document_edit_history` (
  `id` varchar(36) NOT NULL,
  `document_id` varchar(36) NOT NULL COMMENT '所属文档',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  `edited_user_id` int NOT NULL COMMENT '编辑的用户',
  `edited_datetime` datetime DEFAULT NULL COMMENT '编辑时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_document_id_edited_user_id` (`document_id`,`edited_user_id`),
  KEY `ix_document_edit_history_document_id` (`document_id`),
  KEY `ix_document_edit_history_edited_user_id` (`edited_user_id`),
  CONSTRAINT `document_edit_history_ibfk_2` FOREIGN KEY (`edited_user_id`) REFERENCES `user` (`id`),
  CONSTRAINT `document_edit_history_ibfk_3` FOREIGN KEY (`document_id`) REFERENCES `document_base` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `document_node`
--

DROP TABLE IF EXISTS `document_node`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `document_node` (
  `id` varchar(36) NOT NULL COMMENT '主键',
  `type` varchar(10) NOT NULL COMMENT '节点类型',
  `title` varchar(128) NOT NULL COMMENT '节点标题',
  `parent_id` varchar(36) DEFAULT NULL COMMENT '父节点ID',
  `first_child_id` varchar(36) DEFAULT NULL COMMENT '第一个子节点ID',
  `document_id` varchar(36) DEFAULT NULL COMMENT '所属文档ID',
  `prev_id` varchar(36) DEFAULT NULL COMMENT '前一个节点ID',
  `next_id` varchar(36) DEFAULT NULL COMMENT '下一个节点ID',
  `knowledge_id` varchar(36) DEFAULT NULL COMMENT '所属知识库ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted_at` datetime DEFAULT NULL COMMENT '删除时间(NULL表示未删除)',
  PRIMARY KEY (`id`),
  KEY `ix_document_node_document_id` (`document_id`),
  KEY `ix_document_node_first_child_id` (`first_child_id`),
  KEY `ix_document_node_id` (`id`),
  KEY `ix_document_node_knowledge_id` (`knowledge_id`),
  KEY `ix_document_node_next_id` (`next_id`),
  KEY `ix_document_node_parent_id` (`parent_id`),
  KEY `ix_document_node_prev_id` (`prev_id`),
  CONSTRAINT `document_node_ibfk_1` FOREIGN KEY (`document_id`) REFERENCES `document_base` (`id`) ON DELETE CASCADE,
  CONSTRAINT `document_node_ibfk_2` FOREIGN KEY (`first_child_id`) REFERENCES `document_node` (`id`) ON DELETE CASCADE,
  CONSTRAINT `document_node_ibfk_4` FOREIGN KEY (`next_id`) REFERENCES `document_node` (`id`) ON DELETE CASCADE,
  CONSTRAINT `document_node_ibfk_5` FOREIGN KEY (`parent_id`) REFERENCES `document_node` (`id`) ON DELETE CASCADE,
  CONSTRAINT `document_node_ibfk_6` FOREIGN KEY (`prev_id`) REFERENCES `document_node` (`id`) ON DELETE CASCADE,
  CONSTRAINT `document_node_ibfk_7` FOREIGN KEY (`knowledge_id`) REFERENCES `knowledge_base` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `document_view_history`
--

DROP TABLE IF EXISTS `document_view_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `document_view_history` (
  `id` varchar(36) NOT NULL,
  `document_id` varchar(36) NOT NULL COMMENT '所属文档',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  `viewed_user_id` int NOT NULL COMMENT '浏览的用户',
  `viewed_datetime` datetime DEFAULT NULL COMMENT '浏览时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_document_id_viewed_user_id` (`document_id`,`viewed_user_id`),
  KEY `ix_document_view_history_document_id` (`document_id`),
  KEY `ix_document_view_history_viewed_user_id` (`viewed_user_id`),
  CONSTRAINT `document_view_history_ibfk_2` FOREIGN KEY (`viewed_user_id`) REFERENCES `user` (`id`),
  CONSTRAINT `document_view_history_ibfk_3` FOREIGN KEY (`document_id`) REFERENCES `document_base` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `invitation`
--

DROP TABLE IF EXISTS `invitation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `invitation` (
  `id` varchar(36) NOT NULL COMMENT '主键',
  `knowledge_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '所属知识库',
  `document_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '所属文档',
  `token` varchar(45) NOT NULL COMMENT '邀请链接token',
  `role` int NOT NULL COMMENT '角色',
  `invitate_type` varchar(20) NOT NULL COMMENT '邀请来源:knowledge-知识库,document-文档',
  `need_approval` int DEFAULT NULL COMMENT '是否需要审批:0-否,1-是',
  `status` int NOT NULL COMMENT '状态:1-正常,2-已撤销',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  `invitate_user_id` int NOT NULL COMMENT '邀请人（发起邀请的人）',
  PRIMARY KEY (`id`),
  UNIQUE KEY `token` (`token`),
  KEY `ix_invitation_id` (`id`),
  KEY `ix_invitation_knowledge_id` (`knowledge_id`),
  KEY `ix_invitation_document_id` (`document_id`),
  KEY `ix_invitation_invitate_user_id` (`invitate_user_id`),
  CONSTRAINT `fk_document_id` FOREIGN KEY (`document_id`) REFERENCES `document_base` (`id`) ON DELETE CASCADE,
  CONSTRAINT `invitation_ibfk_1` FOREIGN KEY (`knowledge_id`) REFERENCES `knowledge_base` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `knowledge_base`
--

DROP TABLE IF EXISTS `knowledge_base`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `knowledge_base` (
  `id` varchar(36) NOT NULL COMMENT '主键',
  `user_id` int NOT NULL COMMENT '所属用户',
  `name` varchar(128) NOT NULL COMMENT '知识库名称',
  `slug` varchar(64) NOT NULL COMMENT '知识库短链',
  `description` varchar(512) DEFAULT NULL COMMENT '简介',
  `cover_url` json DEFAULT NULL COMMENT '封面图信息',
  `is_public` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否公开',
  `content_updated_at` datetime DEFAULT NULL COMMENT '内容最近更新时间',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `icon` varchar(20) NOT NULL COMMENT '知识库图标',
  `enable_catalog` tinyint(1) NOT NULL DEFAULT '1' COMMENT '是否启用目录',
  `layout` varchar(20) NOT NULL COMMENT '布局',
  `sort` varchar(20) NOT NULL COMMENT '排序',
  `enable_custom_body` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否启用自定义模块',
  `enable_user_feed` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否显示协同人员',
  `deleted_at` datetime DEFAULT NULL COMMENT '删除时间(NULL表示未删除)',
  `team_id` varchar(36) NOT NULL COMMENT '所属团队',
  `space_id` varchar(36) NOT NULL COMMENT '所属空间（冗余字段）',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_knowledge_slug` (`slug`),
  UNIQUE KEY `ix_knowledge_base_slug` (`slug`),
  KEY `ix_knowledge_base_id` (`id`),
  KEY `ix_knowledge_base_user_id` (`user_id`),
  KEY `ix_knowledge_base_space_id` (`space_id`),
  KEY `ix_knowledge_base_team_id` (`team_id`),
  CONSTRAINT `knowledge_base_ibfk_2` FOREIGN KEY (`team_id`) REFERENCES `team` (`id`) ON DELETE CASCADE,
  CONSTRAINT `knowledge_base_ibfk_3` FOREIGN KEY (`space_id`) REFERENCES `space` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `knowledge_common_pin`
--

DROP TABLE IF EXISTS `knowledge_common_pin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `knowledge_common_pin` (
  `id` varchar(36) NOT NULL COMMENT '主键',
  `knowledge_id` varchar(36) DEFAULT NULL COMMENT '知识库ID',
  `user_id` int DEFAULT NULL COMMENT '用户ID',
  `order_index` int DEFAULT NULL COMMENT '排序索引',
  `created_at` datetime DEFAULT NULL COMMENT '创建时间',
  `updated_at` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uix_user_knowledge` (`user_id`,`knowledge_id`),
  KEY `ix_knowledge_common_pin_id` (`id`),
  KEY `ix_knowledge_common_pin_knowledge_id` (`knowledge_id`),
  KEY `ix_knowledge_common_pin_user_id` (`user_id`),
  CONSTRAINT `knowledge_common_pin_ibfk_1` FOREIGN KEY (`knowledge_id`) REFERENCES `knowledge_base` (`id`),
  CONSTRAINT `knowledge_common_pin_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `knowledge_daily_stats`
--

DROP TABLE IF EXISTS `knowledge_daily_stats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `knowledge_daily_stats` (
  `id` varchar(36) NOT NULL,
  `knowledge_id` varchar(36) NOT NULL,
  `stats_date` date NOT NULL,
  `word_count` int NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uix_knowledge_id_stats_date` (`knowledge_id`,`stats_date`),
  KEY `idx_knowledge_id` (`knowledge_id`),
  KEY `idx_stats_date` (`stats_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `knowledge_group`
--

DROP TABLE IF EXISTS `knowledge_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `knowledge_group` (
  `id` varchar(36) NOT NULL COMMENT '分组ID',
  `user_id` int DEFAULT NULL COMMENT '用户ID',
  `group_name` varchar(255) DEFAULT NULL COMMENT '分组名称',
  `order_index` int DEFAULT '0' COMMENT '排序索引',
  `is_default` tinyint(1) DEFAULT NULL COMMENT '是否默认分组',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  `display_config` json DEFAULT NULL COMMENT '显示配置',
  `deleted_at` datetime DEFAULT NULL COMMENT '删除时间(NULL表示未删除)',
  PRIMARY KEY (`id`),
  KEY `ix_knowledge_group_group_name` (`group_name`),
  KEY `ix_knowledge_group_id` (`id`),
  KEY `ix_knowledge_group_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `knowledge_group_relation`
--

DROP TABLE IF EXISTS `knowledge_group_relation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `knowledge_group_relation` (
  `id` varchar(36) NOT NULL,
  `knowledge_id` varchar(36) DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  `group_id` varchar(36) DEFAULT NULL,
  `order_index` int DEFAULT '0' COMMENT '排序索引',
  `created_at` datetime DEFAULT NULL COMMENT '创建时间',
  `updated_at` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uix_group_knowledge` (`group_id`,`knowledge_id`),
  UNIQUE KEY `uix_user_knowledge` (`user_id`,`knowledge_id`),
  KEY `knowledge_id` (`knowledge_id`),
  CONSTRAINT `knowledge_group_relation_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `knowledge_group` (`id`),
  CONSTRAINT `knowledge_group_relation_ibfk_2` FOREIGN KEY (`knowledge_id`) REFERENCES `knowledge_base` (`id`),
  CONSTRAINT `knowledge_group_relation_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `notification`
--

DROP TABLE IF EXISTS `notification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notification` (
  `id` varchar(36) NOT NULL COMMENT '通知id',
  `biz_type` varchar(20) NOT NULL COMMENT '业务类型',
  `biz_id` varchar(128) DEFAULT NULL COMMENT '业务id(用于幂等性)',
  `read_at` datetime DEFAULT NULL COMMENT '已读时间',
  `payload` json DEFAULT NULL COMMENT '负载(扩展数据，携带到跳转链接的参数)',
  `created_at` datetime DEFAULT NULL COMMENT '创建时间',
  `updated_at` datetime DEFAULT NULL COMMENT '更新时间',
  `actor_user_id` int DEFAULT NULL COMMENT '发起者用户id',
  `mentioned_user_id` int DEFAULT NULL COMMENT '被提及用户id',
  `list_type` varchar(20) NOT NULL COMMENT '列表类型(用于分组展示)',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uix_mentioned_user_id_biz_type_biz_id` (`mentioned_user_id`,`biz_type`,`biz_id`),
  KEY `ix_notification_biz_id` (`biz_id`),
  KEY `ix_notification_id` (`id`),
  KEY `idx_mentioned_user_id_created_at` (`mentioned_user_id`,`created_at`),
  KEY `idx_mentioned_user_id_read_at` (`mentioned_user_id`,`read_at`),
  KEY `ix_notification_actor_user_id` (`actor_user_id`),
  KEY `ix_notification_mentioned_user_id` (`mentioned_user_id`),
  CONSTRAINT `notification_ibfk_1` FOREIGN KEY (`actor_user_id`) REFERENCES `user` (`id`),
  CONSTRAINT `notification_ibfk_2` FOREIGN KEY (`mentioned_user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `permission_abilities`
--

DROP TABLE IF EXISTS `permission_abilities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `permission_abilities` (
  `id` varchar(36) NOT NULL,
  `permission_group_id` varchar(36) NOT NULL COMMENT '权限组ID',
  `ability_key` varchar(30) NOT NULL COMMENT '能力键',
  `enable` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否启用',
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT (now()),
  PRIMARY KEY (`id`),
  KEY `permission_group_id` (`permission_group_id`),
  CONSTRAINT `permission_abilities_ibfk_1` FOREIGN KEY (`permission_group_id`) REFERENCES `permission_groups` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `permission_groups`
--

DROP TABLE IF EXISTS `permission_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `permission_groups` (
  `id` varchar(36) NOT NULL,
  `name` varchar(100) NOT NULL COMMENT '权限组名称',
  `role` int NOT NULL COMMENT '角色',
  `target_type` varchar(30) NOT NULL COMMENT '目标类型(knowledge/document)',
  `target_id` varchar(36) NOT NULL COMMENT '目标ID(知识库/文档ID)',
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT (now()),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `space`
--

DROP TABLE IF EXISTS `space`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `space` (
  `id` varchar(36) NOT NULL,
  `type` enum('PERSONAL','TEAM') NOT NULL COMMENT '空间类型',
  `domain` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '空间域名,也用于标识访问(可选,个人类型可不传入domin)',
  `name` varchar(64) NOT NULL COMMENT '空间名称',
  `owner_id` int NOT NULL COMMENT '空间所有者ID',
  `contact_email` varchar(255) NOT NULL COMMENT '联系邮箱,用于接收通知',
  `icon` json DEFAULT NULL COMMENT '封面图信息',
  `description` varchar(512) NOT NULL COMMENT '空间描述',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted_at` datetime DEFAULT NULL COMMENT '删除时间(NULL表示未删除)',
  PRIMARY KEY (`id`),
  UNIQUE KEY `domain` (`domain`),
  KEY `owner_id` (`owner_id`),
  CONSTRAINT `space_ibfk_1` FOREIGN KEY (`owner_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `space_dept`
--

DROP TABLE IF EXISTS `space_dept`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `space_dept` (
  `id` varchar(36) NOT NULL,
  `space_id` varchar(36) NOT NULL COMMENT '所属空间ID',
  `name` varchar(30) NOT NULL COMMENT '部门名称',
  `order` int NOT NULL COMMENT '排序',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted_at` datetime DEFAULT NULL COMMENT '删除时间(NULL表示未删除)',
  PRIMARY KEY (`id`),
  KEY `space_id` (`space_id`),
  CONSTRAINT `space_dept_ibfk_1` FOREIGN KEY (`space_id`) REFERENCES `space` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `space_member`
--

DROP TABLE IF EXISTS `space_member`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `space_member` (
  `id` varchar(36) NOT NULL,
  `space_id` varchar(36) NOT NULL COMMENT '空间ID',
  `user_id` int NOT NULL COMMENT '用户ID',
  `role` enum('OWNER','ADMIN','MEMBER','EXTERNAL') NOT NULL COMMENT '角色',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted_at` datetime DEFAULT NULL COMMENT '删除时间(NULL表示未删除)',
  PRIMARY KEY (`id`),
  KEY `space_id` (`space_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `space_member_ibfk_1` FOREIGN KEY (`space_id`) REFERENCES `space` (`id`) ON DELETE CASCADE,
  CONSTRAINT `space_member_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `team`
--

DROP TABLE IF EXISTS `team`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `team` (
  `id` varchar(36) NOT NULL,
  `name` varchar(30) NOT NULL COMMENT '团队名称',
  `icon` varchar(20) DEFAULT NULL COMMENT '团队图标(团队则为类型，个人则存放的是url链接)',
  `slug` varchar(64) NOT NULL COMMENT '团队标识(用于访问知识库的时候携带)',
  `space_id` varchar(36) NOT NULL COMMENT '空间ID',
  `description` varchar(512) DEFAULT NULL COMMENT '团队简介',
  `visibility` enum('PUBLIC','PRIVATE') NOT NULL COMMENT '团队可见性(公开给空间所有成员)',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_default` tinyint(1) NOT NULL COMMENT '是否为默认团队',
  `owner_id` int NOT NULL COMMENT '团队所有者ID',
  `joined_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '加入时间',
  `deleted_at` datetime DEFAULT NULL COMMENT '删除时间(NULL表示未删除)',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_team_slug` (`slug`),
  KEY `owner_id` (`owner_id`),
  KEY `space_id` (`space_id`),
  CONSTRAINT `team_ibfk_1` FOREIGN KEY (`owner_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `team_ibfk_2` FOREIGN KEY (`space_id`) REFERENCES `space` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `team_member`
--

DROP TABLE IF EXISTS `team_member`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `team_member` (
  `id` varchar(36) NOT NULL,
  `team_id` varchar(36) NOT NULL COMMENT '团队ID',
  `user_id` int NOT NULL COMMENT '用户ID',
  `role` enum('OWNER','ADMIN','MEMBER','EXTERNAL') NOT NULL COMMENT '角色',
  `dept_id` varchar(36) DEFAULT NULL COMMENT '部门ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `dept_id` (`dept_id`),
  KEY `team_id` (`team_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `team_member_ibfk_1` FOREIGN KEY (`dept_id`) REFERENCES `space_dept` (`id`) ON DELETE CASCADE,
  CONSTRAINT `team_member_ibfk_2` FOREIGN KEY (`team_id`) REFERENCES `team` (`id`) ON DELETE CASCADE,
  CONSTRAINT `team_member_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `nickname` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `deleted_at` datetime DEFAULT NULL COMMENT '删除时间(NULL表示未删除)',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_user_email` (`email`),
  UNIQUE KEY `ix_user_username` (`username`),
  KEY `ix_user_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `v_permission_ability`
--

DROP TABLE IF EXISTS `v_permission_ability`;
/*!50001 DROP VIEW IF EXISTS `v_permission_ability`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_permission_ability` AS SELECT 
 1 AS `id`,
 1 AS `permission_group_id`,
 1 AS `ability_key`,
 1 AS `enable`,
 1 AS `created_at`,
 1 AS `updated_at`,
 1 AS `group_name`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `vector_sync`
--

DROP TABLE IF EXISTS `vector_sync`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `vector_sync` (
  `document_id` varchar(36) NOT NULL COMMENT '文档ID(这里用于主键)',
  `last_content_updated_at` datetime(3) NOT NULL COMMENT '最后一次内容更新时间',
  `next_run_at` datetime(3) NOT NULL COMMENT '下次运行时间(定时任务调度)',
  `locked_at` datetime(3) DEFAULT NULL COMMENT '锁定时间',
  `lock_token` varchar(36) DEFAULT NULL COMMENT '锁定令牌',
  `updated_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '更新时间',
  `knowledge_id` varchar(36) DEFAULT NULL COMMENT '所属知识库ID',
  PRIMARY KEY (`document_id`),
  KEY `ix_vector_sync_document_id` (`document_id`),
  KEY `ix_vector_sync_next_run_at` (`next_run_at`),
  KEY `ix_vector_sync_knowledge_id` (`knowledge_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping routines for database 'speed-knowledge'
--

--
-- Final view structure for view `v_permission_ability`
--

/*!50001 DROP VIEW IF EXISTS `v_permission_ability`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_unicode_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `v_permission_ability` AS select `pa`.`id` AS `id`,`pa`.`permission_group_id` AS `permission_group_id`,`pa`.`ability_key` AS `ability_key`,`pa`.`enable` AS `enable`,`pa`.`created_at` AS `created_at`,`pa`.`updated_at` AS `updated_at`,`pg`.`name` AS `group_name` from (`permission_abilities` `pa` join `permission_groups` `pg` on((`pa`.`permission_group_id` = `pg`.`id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-06-26 13:19:31
