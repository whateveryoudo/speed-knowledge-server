-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- 主机： speed-editor-db
-- 生成日期： 2025-12-23 12:12:45
-- 服务器版本： 8.4.5
-- PHP 版本： 8.2.27

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 数据库： `speed-knowledge`
--

-- --------------------------------------------------------

--
-- 表的结构 `alembic_version`
--

CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- 转存表中的数据 `alembic_version`
--

INSERT INTO `alembic_version` (`version_num`) VALUES
('9c74ee41b8ab');

-- --------------------------------------------------------

--
-- 表的结构 `attachment`
--

CREATE TABLE `attachment` (
  `id` varchar(36) NOT NULL COMMENT '主键',
  `file_name` varchar(255) DEFAULT NULL COMMENT '附件名称',
  `file_type` varchar(20) DEFAULT NULL COMMENT '附件类型',
  `object_name` varchar(255) NOT NULL COMMENT '文件的唯一标识路径',
  `file_size` bigint DEFAULT NULL COMMENT '附件大小',
  `bucket_name` varchar(255) NOT NULL COMMENT 'bucket名',
  `user_id` int NOT NULL COMMENT '上传者',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- 转存表中的数据 `attachment`
--

INSERT INTO `attachment` (`id`, `file_name`, `file_type`, `object_name`, `file_size`, `bucket_name`, `user_id`, `created_at`, `updated_at`) VALUES
('0567a480-0f34-4ab8-9e5d-6ab99dfcd191', 'default_cover.png', 'image/png', '2/e7527ac1-418b-4a9c-84b8-12333096c1c8_default_cover.png', 3962, 'speed-knowledge', 2, '2025-11-19 18:45:52', '2025-11-19 18:45:52'),
('1068a1cc-1a1c-4e63-87a9-109c214e0916', 'default_cover.png', 'image/png', '2/01f90544-19ee-4d8f-99e7-7d3f74b0cce1_default_cover.png', 3962, 'speed-knowledge', 2, '2025-11-21 18:30:22', '2025-11-21 18:30:22'),
('270c312f-f8f4-496b-b2b5-4974333beb0a', 'default_cover.png', 'image/png', '2/40f02c42-5817-4d30-af5a-d63ca05ef2ad_default_cover.png', 3962, 'speed-knowledge', 2, '2025-11-21 18:42:20', '2025-11-21 18:42:20'),
('2c675f90-9891-4ae3-997e-6c3df558c4cc', 'default_cover.png', 'image/png', '2/6ded7c31-2be6-444a-b4fe-a76ada7f8137_default_cover.png', 3962, 'speed-knowledge', 2, '2025-11-21 18:51:56', '2025-11-21 18:51:56'),
('37be7f05-431b-4f4f-a15c-756531fb887d', 'default_cover.png', 'image/png', '2/b0691942-f14e-4103-a609-bf12e118cbe9_default_cover.png', 3962, 'speed-knowledge', 2, '2025-11-21 18:13:06', '2025-11-21 18:13:06'),
('3b684737-8d18-42f5-9f6e-5628023c06de', 'default_cover.png', 'image/png', '2/aaf43e7d-53cf-43ac-baa7-6956a6ed5a43_default_cover.png', 3962, 'speed-knowledge', 2, '2025-11-21 18:40:32', '2025-11-21 18:40:32'),
('53e43f41-8480-46b9-a2be-652269ad1499', 'default_cover.png', 'image/png', '2/6d27197f-9038-4f98-bedd-e42aec2e8842_default_cover.png', 3962, 'speed-knowledge', 2, '2025-11-21 18:25:07', '2025-11-21 18:25:07'),
('7a8e847a-30c4-4820-8ad4-26011b4d85a2', 'A_IvwES5EwvsEAAAAAAAAAAABkARQnAQ.png', 'image/png', '2/f5127dbb-8eb3-4ed6-95f3-4ce2067ba3fc_A_IvwES5EwvsEAAAAAAAAAAABkARQnAQ.png', 3962, 'speed-knowledge', 2, '2025-11-19 18:36:45', '2025-11-19 18:36:45'),
('c8120f07-4cc1-463e-9119-eface352cd82', 'default_cover.png', 'image/png', '2/20df2ccd-d338-4cc8-8ad4-e919b19a27a8_default_cover.png', 3962, 'speed-knowledge', 2, '2025-11-21 18:46:27', '2025-11-21 18:46:27'),
('d1fa32b7-8730-44a4-806e-e509dce13829', 'default_cover.png', 'image/png', '2/dda33992-aa13-4517-a37c-fa5cb91c89d0_default_cover.png', 3962, 'speed-knowledge', 2, '2025-11-21 17:57:13', '2025-11-21 17:57:13');

-- --------------------------------------------------------

--
-- 表的结构 `document_base`
--

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
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- 转存表中的数据 `document_base`
--

INSERT INTO `document_base` (`id`, `user_id`, `knowledge_id`, `name`, `slug`, `type`, `is_public`, `content_updated_at`, `created_at`, `updated_at`) VALUES
('67f61a75-64fa-438a-a3a0-b33f0866ff8a', 2, '26156ca3-602e-451f-a0d4-141259997aed', 'ykx测试文档1newaa2', 'OAqWnfE0syyDzgUG', 'word', 0, NULL, '2025-12-06 17:00:39', '2025-12-06 17:00:39');

-- --------------------------------------------------------

--
-- 表的结构 `document_content`
--

CREATE TABLE `document_content` (
  `id` varchar(36) NOT NULL COMMENT '主键',
  `document_id` varchar(36) NOT NULL COMMENT '所属文档',
  `content` blob NOT NULL COMMENT '文档内容(为协同编辑的的二进制数据)',
  `content_updated_at` datetime DEFAULT NULL COMMENT '内容最近更新时间',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- 转存表中的数据 `document_content`
--

INSERT INTO `document_content` (`id`, `document_id`, `content`, `content_updated_at`, `created_at`, `updated_at`) VALUES
('f9a31723-3370-4eef-83c5-fd00f97957b7', '67f61a75-64fa-438a-a3a0-b33f0866ff8a', 0x030192bf8fa40d0084ece7e0af070e013210ece7e0af070084b887a8a5042715796b78e6b58be8af95e69687e6a1a3316e6577616181ece7e0af070c0281b887a8a5040f0884ece7e0af071606e68891e69da581ece7e0af07180584ece7e0af071d06e6b58be8af9581ece7e0af071f0384ece7e0af072203e4b88b81ece7e0af07230984ece7e0af072c06e8bf99e698af81ece7e0af072e0784ece7e0af073506e4b880e7af8781ece7e0af07370584ece7e0af073c06e69687e6a1a387b887a8a5040103097061726167726170682800ece7e0af073f06696e64656e74017d0008b887a8a5040007010764656661756c7403057469746c6587b887a8a5040003097061726167726170680700b887a8a50401060100b887a8a50402012800b887a8a5040106696e64656e74017d0081b887a8a504030b0700b887a8a50400060100b887a8a504101702ece7e0af07060d0a1905200324092f073805b887a8a504030301050b1117, '2025-12-16 17:41:25', '2025-12-06 17:00:39', '2025-12-16 17:41:25');

-- --------------------------------------------------------

--
-- 表的结构 `document_node`
--

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
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- 转存表中的数据 `document_node`
--

INSERT INTO `document_node` (`id`, `type`, `title`, `parent_id`, `first_child_id`, `document_id`, `prev_id`, `next_id`, `knowledge_id`, `created_at`, `updated_at`) VALUES
('2b6108bd-5259-401d-9728-578e19128014', 'DOC', 'ykx测试文档1newaa2', NULL, NULL, '67f61a75-64fa-438a-a3a0-b33f0866ff8a', NULL, NULL, '26156ca3-602e-451f-a0d4-141259997aed', '2025-12-06 17:00:39', '2025-12-06 17:00:39');

-- --------------------------------------------------------

--
-- 表的结构 `knowledge_base`
--

CREATE TABLE `knowledge_base` (
  `id` varchar(36) NOT NULL COMMENT '主键',
  `user_id` int NOT NULL COMMENT '所属用户',
  `name` varchar(128) NOT NULL COMMENT '知识库名称',
  `slug` varchar(64) NOT NULL COMMENT '知识库短链',
  `description` varchar(512) DEFAULT NULL COMMENT '简介',
  `cover_url` json DEFAULT NULL COMMENT '封面图信息',
  `is_public` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否公开',
  `items_count` int UNSIGNED NOT NULL DEFAULT '0' COMMENT '文档数量',
  `content_updated_at` datetime DEFAULT NULL COMMENT '内容最近更新时间',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `group_id` varchar(36) NOT NULL COMMENT '所属分组',
  `icon` varchar(20) NOT NULL COMMENT '知识库图标'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- 转存表中的数据 `knowledge_base`
--

INSERT INTO `knowledge_base` (`id`, `user_id`, `name`, `slug`, `description`, `cover_url`, `is_public`, `items_count`, `content_updated_at`, `created_at`, `updated_at`, `group_id`, `icon`) VALUES
('26156ca3-602e-451f-a0d4-141259997aed', 2, 'ykx测试知识库1', '4onWfw', '啊啊', '{\"id\": \"0567a480-0f34-4ab8-9e5d-6ab99dfcd191\", \"fileName\": \"default_cover.png\", \"fileSize\": 3962, \"fileType\": \"image/png\"}', 0, 0, NULL, '2025-11-21 20:08:31', '2025-11-21 20:08:31', '5c75553f-2f64-4b48-a55a-9736b8d6c746', 'icon-book-0'),
('98b18a48-eee0-4888-806c-9a90bf49ac89', 2, 'ykx测试知识库2', 'Zn8m5T', '不错额', '{\"id\": \"0567a480-0f34-4ab8-9e5d-6ab99dfcd191\", \"fileName\": \"default_cover.png\", \"fileSize\": 3962, \"fileType\": \"image/png\"}', 0, 0, NULL, '2025-11-21 20:26:38', '2025-11-21 20:26:38', '5c75553f-2f64-4b48-a55a-9736b8d6c746', 'icon-book-3'),
('eaf6c137-ad56-4784-80f8-0f5c968467bd', 2, 'ykx测试知识库3', 'PXUTKW', '不不不', '{\"id\": \"0567a480-0f34-4ab8-9e5d-6ab99dfcd191\", \"fileName\": \"default_cover.png\", \"fileSize\": 3962, \"fileType\": \"image/png\"}', 0, 0, NULL, '2025-11-21 20:33:59', '2025-11-21 20:33:59', '5c75553f-2f64-4b48-a55a-9736b8d6c746', 'icon-book-9');

-- --------------------------------------------------------

--
-- 表的结构 `knowledge_collaborator`
--

CREATE TABLE `knowledge_collaborator` (
  `id` varchar(36) NOT NULL COMMENT '主键',
  `knowledge_id` varchar(36) NOT NULL COMMENT '所属知识库',
  `user_id` int NOT NULL COMMENT '所属用户',
  `role` varchar(10) NOT NULL COMMENT '角色',
  `status` int NOT NULL COMMENT '状态',
  `source` int NOT NULL COMMENT '来源',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- 表的结构 `knowledge_group`
--

CREATE TABLE `knowledge_group` (
  `id` varchar(36) NOT NULL COMMENT '分组ID',
  `user_id` int DEFAULT NULL COMMENT '用户ID',
  `group_name` varchar(255) DEFAULT NULL COMMENT '分组名称',
  `order_index` int DEFAULT '0' COMMENT '排序索引',
  `is_default` tinyint(1) DEFAULT NULL COMMENT '是否默认分组',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  `display_config` json DEFAULT NULL COMMENT '显示配置'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- 转存表中的数据 `knowledge_group`
--

INSERT INTO `knowledge_group` (`id`, `user_id`, `group_name`, `order_index`, `is_default`, `created_at`, `updated_at`, `display_config`) VALUES
('51df5499-93ac-4843-aaf5-2bc0223ceec2', 3, '我的知识库', 0, 1, '2025-12-16 17:44:45', '2025-12-16 17:44:45', '{\"type\": \"card\", \"style\": \"detail\", \"doc_order_type\": 1, \"show_knowledge_icon\": true, \"show_knowledge_description\": true}'),
('5c75553f-2f64-4b48-a55a-9736b8d6c746', 2, '我的知识库', 0, 1, '2025-11-19 11:49:57', '2025-11-19 11:49:57', '{\"type\": \"card\", \"style\": \"detail\", \"doc_order_type\": 1, \"show_knowledge_icon\": true, \"show_knowledge_description\": true}');

-- --------------------------------------------------------

--
-- 表的结构 `knowledge_invitation`
--

CREATE TABLE `knowledge_invitation` (
  `id` varchar(36) NOT NULL COMMENT '主键',
  `knowledge_id` varchar(36) NOT NULL COMMENT '所属知识库',
  `inviter_id` int DEFAULT NULL COMMENT '被邀请用户id',
  `token` varchar(45) NOT NULL COMMENT '邀请链接token',
  `role` int NOT NULL COMMENT '角色',
  `need_approval` int DEFAULT NULL COMMENT '是否需要审批:0-否,1-是',
  `status` int NOT NULL COMMENT '状态:1-正常,2-已撤销',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- 转存表中的数据 `knowledge_invitation`
--

INSERT INTO `knowledge_invitation` (`id`, `knowledge_id`, `inviter_id`, `token`, `role`, `need_approval`, `status`, `created_at`, `updated_at`) VALUES
('02ed06aa-fb78-43dd-879d-fa22ab739f94', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'mn21oUDH6pceMCBK', 1, 0, 1, '2025-12-21 19:04:04', '2025-12-21 19:04:04'),
('0b3a0ee0-c2a3-4213-8b5f-ee2c034ceb78', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'uj2wQ6zqTINBF5qe', 1, 0, 1, '2025-12-21 16:49:17', '2025-12-21 16:49:17'),
('11e716a8-4ca2-476c-b355-021fef0b935b', '26156ca3-602e-451f-a0d4-141259997aed', NULL, '3Z3V4jhHzqPxvwoW', 1, 0, 1, '2025-12-21 18:25:43', '2025-12-21 18:25:43'),
('131e906c-6f54-4059-ba3e-2f233d336ff9', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'Al5oLLkbc2RcaJpy', 1, 0, 1, '2025-12-21 17:20:34', '2025-12-21 17:20:34'),
('15471087-1e34-4e22-94f6-e63dae338774', '26156ca3-602e-451f-a0d4-141259997aed', NULL, '1XoJZOs0Fe5cRqQc', 1, 0, 1, '2025-12-21 16:04:00', '2025-12-21 16:04:00'),
('1dfce06c-ef9a-4cc6-bcf3-6d6ef845c56e', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'C6cwJ6STp53ex92N', 1, 0, 1, '2025-12-21 16:14:53', '2025-12-21 16:14:53'),
('1ea8b83d-dea0-423f-9cf2-1ad4506ad718', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'vZPC7EgR5HHKTIor', 1, 0, 1, '2025-12-21 19:05:10', '2025-12-21 19:05:10'),
('20d489b0-c59b-4dc6-a389-c368cc7528af', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'IZxxb5NdK1xOYABt', 1, 0, 1, '2025-12-21 18:41:57', '2025-12-21 18:41:57'),
('24465817-50ac-4a12-b563-cd8f21d1eb95', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'yBKbf3Hz0KQHpcZj', 1, 0, 1, '2025-12-21 17:29:31', '2025-12-21 17:29:31'),
('25cce32d-b439-4ccb-9a94-5e4b237e2c2e', '26156ca3-602e-451f-a0d4-141259997aed', NULL, '5LYqFmcMJ0VDEBIV', 1, 0, 1, '2025-12-21 18:47:03', '2025-12-21 18:47:03'),
('2888e824-5967-431e-9aa9-0b007be13a35', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'MOcV0usqNm9r3HL1', 1, 0, 1, '2025-12-21 19:17:57', '2025-12-21 19:17:57'),
('298c9f2a-30c1-486f-a269-2ccd27640102', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'UlBmu3KLlTxzysww', 1, 0, 1, '2025-12-21 18:05:38', '2025-12-21 18:05:38'),
('29b65501-7809-448b-9acc-f39ed57c609a', '26156ca3-602e-451f-a0d4-141259997aed', NULL, '8uTkFsmrMbKvNpwx', 1, 0, 1, '2025-12-21 16:41:26', '2025-12-21 16:41:26'),
('2e26db1c-a5c2-40d6-a847-4689d7677c9f', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'fK2uzw0atCU46jGU', 1, 0, 1, '2025-12-21 18:48:40', '2025-12-21 18:48:40'),
('37cf90ab-0c73-4e2b-beb3-f750969faf39', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'hANoiK8NTTUkSHcq', 1, 0, 1, '2025-12-21 19:27:17', '2025-12-21 19:27:17'),
('38c81703-cc43-40e4-a40c-3b51acce7c05', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'pEKHbSWjvsTwoiQZ', 1, 0, 1, '2025-12-21 19:25:36', '2025-12-21 19:25:36'),
('38cfd746-a0fd-4ed6-af80-41bbd4939610', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'sEnEY7PlQ1tERbxC', 1, 0, 1, '2025-12-21 18:45:36', '2025-12-21 18:45:36'),
('3e4a1a72-196f-4a50-9839-3ca18141ace5', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'PrmPBCmJhgmgtCQC', 1, 0, 1, '2025-12-21 17:47:49', '2025-12-21 17:47:49'),
('45384d4d-1de1-4133-92cd-d19e58626180', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'tQPScqyQmSIbp0Fo', 1, 0, 1, '2025-12-21 18:10:43', '2025-12-21 18:10:43'),
('49ab856c-f088-4fa4-9080-c5e21edd2225', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'qs6nqY39Y8Yx6OER', 1, 0, 1, '2025-12-21 19:25:41', '2025-12-21 19:25:41'),
('4a85a1f5-7ba4-4a7c-956d-ea1b38ca72a9', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'VpIRf3g9INm8CYod', 1, 0, 1, '2025-12-21 19:25:56', '2025-12-21 19:25:56'),
('4b7cf7c3-73dc-4a3d-a6e8-563f455c36f3', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'uF5nRVuf8zvdteMt', 1, 0, 1, '2025-12-21 19:12:48', '2025-12-21 19:12:48'),
('4ba09173-6776-4b5d-a56b-1d6684c036a7', '26156ca3-602e-451f-a0d4-141259997aed', NULL, '1iSPOPxV7JglvQjI', 1, 0, 1, '2025-12-23 17:40:49', '2025-12-23 17:40:49'),
('4baee8ee-43c8-496d-aefd-fa0c5d638765', '26156ca3-602e-451f-a0d4-141259997aed', NULL, '9QTVuGrksmsoxyim', 1, 0, 1, '2025-12-21 19:25:29', '2025-12-21 19:25:29'),
('4cf3b74e-848b-48ad-8558-44887006c4a4', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'K5CY18XlHbZVKeWe', 1, 0, 1, '2025-12-21 18:47:51', '2025-12-21 18:47:51'),
('51ff4cc8-9fd9-4296-a31f-20365b37f788', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'wO0fSQRXmfasQjyz', 1, 0, 1, '2025-12-21 19:25:47', '2025-12-21 19:25:47'),
('533a4388-197e-4b07-b08e-d325c13d61fc', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'AE5f5Qa505X8W0CQ', 1, 0, 1, '2025-12-21 19:27:46', '2025-12-21 19:27:46'),
('5d78684f-e737-444a-a838-39c725694275', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'fJRV4f5xpHbcKloi', 1, 0, 1, '2025-12-21 16:39:10', '2025-12-21 16:39:10'),
('630f1dc7-8dc9-415a-950f-7cec87327116', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'hxSmRWmG4SG0Krnt', 1, 0, 1, '2025-12-21 19:18:04', '2025-12-21 19:18:04'),
('672fe3ce-bbaa-4446-a7c8-a80b05bb8f34', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'p7tUwTt5sMNgz0q1', 1, 0, 1, '2025-12-21 17:26:42', '2025-12-21 17:26:42'),
('6969f940-7b42-441c-a6e7-5389274119a0', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'k5TUG9I8mcyDWuHp', 1, 0, 1, '2025-12-21 19:25:46', '2025-12-21 19:25:46'),
('6f9a9a0d-3f8d-48d1-b0f9-6d6e7938be95', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'UCcK0YSVSjDpSQ0z', 1, 0, 1, '2025-12-21 19:27:23', '2025-12-21 19:27:23'),
('7716173f-1159-4dc8-8b0b-4bf7e4b0be8b', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'vlFa8T5FkCouNabG', 1, 0, 1, '2025-12-21 18:51:21', '2025-12-21 18:51:21'),
('7dcc1958-9cda-477a-bac1-8453eba6bd19', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'IfU8UbCBEAStrOdV', 1, 0, 1, '2025-12-21 18:58:40', '2025-12-21 18:58:40'),
('7e33c71e-6a84-4b2a-bbc5-a5dd4ac5341e', '26156ca3-602e-451f-a0d4-141259997aed', NULL, '1wpHnXRE4e9nRM9O', 1, 0, 1, '2025-12-21 16:24:07', '2025-12-21 16:24:07'),
('7f1420aa-388a-4cd2-94b3-3f9946cb1efd', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'qjZkCZExPems7BGg', 1, 0, 1, '2025-12-21 18:44:51', '2025-12-21 18:44:51'),
('82637d3f-e39e-40e8-9fa7-9e7212ce71e9', '26156ca3-602e-451f-a0d4-141259997aed', NULL, '7RsEByguNF9UT9BC', 1, 0, 1, '2025-12-19 17:14:25', '2025-12-19 17:14:25'),
('8ebad88c-4365-494f-ad53-c1c7178107bc', '26156ca3-602e-451f-a0d4-141259997aed', NULL, '2FxE7x2CiOFdigxS', 1, 0, 1, '2025-12-21 19:04:58', '2025-12-21 19:04:58'),
('9214498d-2887-42b6-b003-9a07c8845ba6', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'A5AVn9GwYF9KkIJa', 1, 0, 1, '2025-12-21 19:05:23', '2025-12-21 19:05:23'),
('95977e6a-ba2e-431a-95c9-415ca5a9f268', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'Js7Ez1jFiXiwoLAD', 1, 0, 1, '2025-12-21 19:25:33', '2025-12-21 19:25:33'),
('9b6f6745-1b7c-4ef8-9873-b25d0b32e4b7', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'A10R7RWk0s4ovDVy', 1, 0, 1, '2025-12-21 18:49:29', '2025-12-21 18:49:29'),
('a216e6df-198a-4687-aa02-b5d314c04aa4', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'fqQjluOGomXJOZZY', 1, 0, 1, '2025-12-21 19:15:15', '2025-12-21 19:15:15'),
('a39ecb85-937f-47aa-9752-eb114d4c6c16', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'w7v2H2DXPWarrLY9', 1, 0, 1, '2025-12-21 16:18:48', '2025-12-21 16:18:48'),
('a50ad2bc-1c5a-408b-857d-ab32bc5cb709', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'X54FtbPbOamiBE0L', 1, 0, 1, '2025-12-21 17:20:38', '2025-12-21 17:20:38'),
('a8d772a9-cee9-40c8-b1f6-c11fb602fffd', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'Q5Ng1p2AHDPOHG6c', 1, 0, 1, '2025-12-21 19:05:15', '2025-12-21 19:05:15'),
('ac0dbb90-65be-45c7-9686-694b370926cd', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'AYzocJd5iJL2Kbpd', 1, 0, 1, '2025-12-21 16:40:34', '2025-12-21 16:40:34'),
('b60efecf-6603-4019-b624-fe19d21f722a', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'AvqhqhknROvcP5Rt', 1, 0, 1, '2025-12-21 18:41:01', '2025-12-21 18:41:01'),
('b8f7a8e1-28d9-4c66-a630-15e8a15546a4', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'iNKtnQ5zqbermrLi', 1, 0, 1, '2025-12-21 18:54:16', '2025-12-21 18:54:16'),
('c05eb9ba-edbc-4e5f-906d-d55ca450312f', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'TYn8vT6MVZguIjjf', 1, 0, 1, '2025-12-21 19:18:31', '2025-12-21 19:18:31'),
('c3e95985-f501-46d3-a460-673dda39ebaf', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'XebZWPfSirf19lTe', 1, 0, 1, '2025-12-21 16:41:35', '2025-12-21 16:41:35'),
('c9741905-31de-459a-bc16-700482fa640c', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'HMg5TVLeWGfiLvcF', 1, 0, 1, '2025-12-21 16:21:50', '2025-12-21 16:21:50'),
('c9e4b210-2fe1-4228-9b60-30320dfa5c70', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'ms4k3Hwq5qrvu5Eq', 1, 0, 1, '2025-12-21 16:46:02', '2025-12-21 16:46:02'),
('d06f08d8-401a-4364-8330-bee66d6cbbb6', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'l3K5mR8Rc0YWMp5a', 1, 0, 1, '2025-12-21 16:14:50', '2025-12-21 16:14:50'),
('d6c2eed3-8f2c-470c-bfee-f3837c43a195', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'jlBarG0ue1cfwsHH', 1, 0, 1, '2025-12-21 18:48:57', '2025-12-21 18:48:57'),
('e3b1c099-95a3-434d-8f40-a315ceb34f08', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'y95Ynr0jLuOAfrxf', 1, 0, 1, '2025-12-21 19:18:06', '2025-12-21 19:18:06'),
('e4a46715-38af-4e83-a33a-eb8f49fe8a95', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'CLiTZjIXsIl0i5Bp', 1, 0, 1, '2025-12-21 16:45:53', '2025-12-21 16:45:53'),
('e8318ddf-7750-419b-80a6-b1ac80e8c5b2', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'ILoslFVRAXOzhGj7', 1, 0, 1, '2025-12-19 19:17:59', '2025-12-19 19:17:59'),
('ee0188eb-5588-4acc-a940-28fdaf3a1021', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'V1r0agSSkECH4l1g', 1, 0, 1, '2025-12-21 19:27:18', '2025-12-21 19:27:18'),
('f4f39726-25e8-4960-9826-ac59538b2f18', '26156ca3-602e-451f-a0d4-141259997aed', NULL, '1Zf8OltIXMZgvxxQ', 1, 0, 1, '2025-12-21 17:26:05', '2025-12-21 17:26:05'),
('f628a72e-a5fa-46a0-9daa-79f45a7589fb', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'NlOAOAJqO3TP99Ma', 1, 0, 1, '2025-12-21 19:25:39', '2025-12-21 19:25:39'),
('f72cdc88-fe4d-40e0-9c0e-f0b281c8b161', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'YZo6kqkFXKw8zDHS', 1, 0, 1, '2025-12-21 19:05:06', '2025-12-21 19:05:06'),
('f787468a-0396-4ab8-ab5f-5323aba68396', '26156ca3-602e-451f-a0d4-141259997aed', NULL, 'YhDhZn7Aom3OyYfi', 1, 0, 1, '2025-12-21 19:27:40', '2025-12-21 19:27:40'),
('f7b0086e-7a89-46ad-b91c-42189f877a74', '26156ca3-602e-451f-a0d4-141259997aed', NULL, '2WHs0lHcVQTHYV47', 1, 0, 1, '2025-12-19 18:18:30', '2025-12-19 18:18:30'),
('fde708b0-c583-4ffe-b8b1-beaaa19bf8f4', '26156ca3-602e-451f-a0d4-141259997aed', NULL, '7PnuInZbO4h3OJLz', 1, 0, 1, '2025-12-20 15:41:52', '2025-12-20 15:41:52');

-- --------------------------------------------------------

--
-- 表的结构 `users`
--

CREATE TABLE `users` (
  `id` int NOT NULL,
  `email` varchar(255) NOT NULL,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `nickname` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- 转存表中的数据 `users`
--

INSERT INTO `users` (`id`, `email`, `username`, `password`, `nickname`, `created_at`, `updated_at`) VALUES
(2, '15982819091@163.com', 'ykx_test1', '$2b$12$3YfnIszucX7Df/.P305dnuZrrTfNl2RF1Tal1aWck5Lyr1teJqxQy', '游开兴测试1', '2025-11-11 12:16:32', '2025-11-11 12:16:32'),
(3, '1358645278@qq.com', 'ykx_test2', '$2b$12$WrWkgeZoHyZPpleYTCqnIu1ERl1F1APIZuIdlcyJ4LQONTb9.KMVO', '游开兴测试2', '2025-12-16 17:44:45', '2025-12-16 17:44:45');

--
-- 转储表的索引
--

--
-- 表的索引 `alembic_version`
--
ALTER TABLE `alembic_version`
  ADD PRIMARY KEY (`version_num`);

--
-- 表的索引 `attachment`
--
ALTER TABLE `attachment`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ix_attachment_file_name` (`file_name`),
  ADD KEY `ix_attachment_id` (`id`),
  ADD KEY `ix_attachment_user_id` (`user_id`);

--
-- 表的索引 `document_base`
--
ALTER TABLE `document_base`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ix_document_base_id` (`id`),
  ADD KEY `ix_document_base_knowledge_id` (`knowledge_id`),
  ADD KEY `ix_document_base_user_id` (`user_id`);

--
-- 表的索引 `document_content`
--
ALTER TABLE `document_content`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ix_document_content_document_id` (`document_id`),
  ADD KEY `ix_document_content_id` (`id`);

--
-- 表的索引 `document_node`
--
ALTER TABLE `document_node`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ix_document_node_document_id` (`document_id`),
  ADD KEY `ix_document_node_first_child_id` (`first_child_id`),
  ADD KEY `ix_document_node_id` (`id`),
  ADD KEY `ix_document_node_knowledge_id` (`knowledge_id`),
  ADD KEY `ix_document_node_next_id` (`next_id`),
  ADD KEY `ix_document_node_parent_id` (`parent_id`),
  ADD KEY `ix_document_node_prev_id` (`prev_id`);

--
-- 表的索引 `knowledge_base`
--
ALTER TABLE `knowledge_base`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ix_knowledge_base_group_id` (`group_id`),
  ADD KEY `ix_knowledge_base_id` (`id`),
  ADD KEY `ix_knowledge_base_user_id` (`user_id`);

--
-- 表的索引 `knowledge_collaborator`
--
ALTER TABLE `knowledge_collaborator`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ix_knowledge_collaborator_id` (`id`),
  ADD KEY `ix_knowledge_collaborator_knowledge_id` (`knowledge_id`),
  ADD KEY `ix_knowledge_collaborator_user_id` (`user_id`);

--
-- 表的索引 `knowledge_group`
--
ALTER TABLE `knowledge_group`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ix_knowledge_group_group_name` (`group_name`),
  ADD KEY `ix_knowledge_group_id` (`id`),
  ADD KEY `ix_knowledge_group_user_id` (`user_id`);

--
-- 表的索引 `knowledge_invitation`
--
ALTER TABLE `knowledge_invitation`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `token` (`token`),
  ADD KEY `ix_knowledge_invitation_id` (`id`),
  ADD KEY `ix_knowledge_invitation_inviter_id` (`inviter_id`),
  ADD KEY `ix_knowledge_invitation_knowledge_id` (`knowledge_id`);

--
-- 表的索引 `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ix_users_email` (`email`),
  ADD UNIQUE KEY `ix_users_username` (`username`),
  ADD KEY `ix_users_id` (`id`);

--
-- 在导出的表使用AUTO_INCREMENT
--

--
-- 使用表AUTO_INCREMENT `users`
--
ALTER TABLE `users`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- 限制导出的表
--

--
-- 限制表 `document_base`
--
ALTER TABLE `document_base`
  ADD CONSTRAINT `document_base_ibfk_1` FOREIGN KEY (`knowledge_id`) REFERENCES `knowledge_base` (`id`) ON DELETE CASCADE;

--
-- 限制表 `document_content`
--
ALTER TABLE `document_content`
  ADD CONSTRAINT `document_content_ibfk_1` FOREIGN KEY (`document_id`) REFERENCES `document_base` (`id`) ON DELETE CASCADE;

--
-- 限制表 `document_node`
--
ALTER TABLE `document_node`
  ADD CONSTRAINT `document_node_ibfk_1` FOREIGN KEY (`document_id`) REFERENCES `document_base` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `document_node_ibfk_2` FOREIGN KEY (`first_child_id`) REFERENCES `document_node` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `document_node_ibfk_3` FOREIGN KEY (`knowledge_id`) REFERENCES `knowledge_base` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `document_node_ibfk_4` FOREIGN KEY (`next_id`) REFERENCES `document_node` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `document_node_ibfk_5` FOREIGN KEY (`parent_id`) REFERENCES `document_node` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `document_node_ibfk_6` FOREIGN KEY (`prev_id`) REFERENCES `document_node` (`id`) ON DELETE CASCADE;

--
-- 限制表 `knowledge_base`
--
ALTER TABLE `knowledge_base`
  ADD CONSTRAINT `knowledge_base_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `knowledge_group` (`id`) ON DELETE CASCADE;

--
-- 限制表 `knowledge_collaborator`
--
ALTER TABLE `knowledge_collaborator`
  ADD CONSTRAINT `knowledge_collaborator_ibfk_1` FOREIGN KEY (`knowledge_id`) REFERENCES `knowledge_base` (`id`) ON DELETE CASCADE;

--
-- 限制表 `knowledge_invitation`
--
ALTER TABLE `knowledge_invitation`
  ADD CONSTRAINT `knowledge_invitation_ibfk_1` FOREIGN KEY (`knowledge_id`) REFERENCES `knowledge_base` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
