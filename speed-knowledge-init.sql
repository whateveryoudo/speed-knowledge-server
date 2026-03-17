-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- 主机： db:3306
-- 生成日期： 2026-03-17 12:11:50
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
('c912439146a8');

-- --------------------------------------------------------

--
-- 表的结构 `attachment`
--

CREATE TABLE `attachment` (
  `id` varchar(36) NOT NULL COMMENT '主键',
  `file_name` varchar(255) DEFAULT NULL COMMENT '附件名称',
  `file_type` varchar(255) DEFAULT NULL COMMENT '附件类型',
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
('034034bf-cf14-4db2-8d32-9b1693f362e2', 'single.png', 'image/png', '2/8c3d6fbd-291e-4d9e-982e-199b1939e19b_single.png', 291794, 'speed-knowledge', 2, '2026-01-12 19:24:38', '2026-01-12 19:24:38'),
('0567a480-0f34-4ab8-9e5d-6ab99dfcd191', 'default_cover.png', 'image/png', '2/e7527ac1-418b-4a9c-84b8-12333096c1c8_default_cover.png', 3962, 'speed-knowledge', 2, '2025-11-19 18:45:52', '2025-11-19 18:45:52'),
('0c27bd96-1e8f-4b4a-812f-06a666c2056e', 'single.png', 'image/png', '2/2564032f-88bb-4a2a-89ec-9db310d8a6e1_single.png', 291794, 'speed-knowledge', 2, '2026-01-12 16:36:16', '2026-01-12 16:36:16'),
('0d9eed9f-cf03-49b1-a6e3-65ea7ccc900b', 'single.png', 'image/png', '2/d37628ac-7ea5-46e7-bc7e-c35517b771e9_single.png', 291794, 'speed-knowledge', 2, '2026-01-12 18:20:17', '2026-01-12 18:20:17'),
('1068a1cc-1a1c-4e63-87a9-109c214e0916', 'default_cover.png', 'image/png', '2/01f90544-19ee-4d8f-99e7-7d3f74b0cce1_default_cover.png', 3962, 'speed-knowledge', 2, '2025-11-21 18:30:22', '2025-11-21 18:30:22'),
('138fdc51-2ebc-4233-8815-6fd8eb491cdd', '缩小图片.png', 'image/png', '2/9b9956f9-a2db-44da-8d47-fdb3297e109b_缩小图片.png', 2233003, 'speed-knowledge', 2, '2026-01-12 19:15:58', '2026-01-12 19:15:58'),
('1abbaa34-ab05-4d6c-8e69-350c74f55d08', '测试22221.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', '2/24ec84ea-3966-40ae-a758-5bbf422c60c5_测试22221.docx', 7133, 'speed-knowledge', 2, '2026-01-13 11:36:11', '2026-01-13 11:36:11'),
('1e8cd0f0-3873-4395-91aa-5f7943b4ecb3', 'single.png', 'image/png', '2/f526e4aa-6f5c-4b45-95e4-2a691fa559d8_single.png', 291794, 'speed-knowledge', 2, '2026-01-12 17:07:48', '2026-01-12 17:07:48'),
('21ae9214-3dd5-43f2-868e-cbf6395a1e1b', '测试22221.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', '2/cba522e1-3bfc-49cd-8973-49e685f0f459_测试22221.docx', 7133, 'speed-knowledge', 2, '2026-01-13 11:06:53', '2026-01-13 11:06:53'),
('270c312f-f8f4-496b-b2b5-4974333beb0a', 'default_cover.png', 'image/png', '2/40f02c42-5817-4d30-af5a-d63ca05ef2ad_default_cover.png', 3962, 'speed-knowledge', 2, '2025-11-21 18:42:20', '2025-11-21 18:42:20'),
('2c675f90-9891-4ae3-997e-6c3df558c4cc', 'default_cover.png', 'image/png', '2/6ded7c31-2be6-444a-b4fe-a76ada7f8137_default_cover.png', 3962, 'speed-knowledge', 2, '2025-11-21 18:51:56', '2025-11-21 18:51:56'),
('308b26a7-6234-4e50-9d43-255226d22222', '测试22221.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', '2/3db6dfe6-f4ca-4660-9b08-42f09c282f5c_测试22221.docx', 7133, 'speed-knowledge', 2, '2026-01-13 11:40:35', '2026-01-13 11:40:35'),
('30dabff8-561f-4af2-9f5a-17bb1ef5597f', 'single.png', 'image/png', '2/e2564247-8344-4978-9138-0c0962bb5909_single.png', 291794, 'speed-knowledge', 2, '2026-01-12 18:47:35', '2026-01-12 18:47:35'),
('363ef12c-e040-45bf-b079-06f4922a49b6', 'single.png', 'image/png', '2/b0201c4b-0a5c-48dc-978d-c6914d73a6ba_single.png', 291794, 'speed-knowledge', 2, '2026-01-12 19:12:44', '2026-01-12 19:12:44'),
('37be7f05-431b-4f4f-a15c-756531fb887d', 'default_cover.png', 'image/png', '2/b0691942-f14e-4103-a609-bf12e118cbe9_default_cover.png', 3962, 'speed-knowledge', 2, '2025-11-21 18:13:06', '2025-11-21 18:13:06'),
('3825e8d2-1382-4a58-b97d-633b9daa42cc', '测试22221.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', '2/d58b3652-5f2f-4d8c-8000-74e2709b07c5_测试22221.docx', 7133, 'speed-knowledge', 2, '2026-01-13 14:28:27', '2026-01-13 14:28:27'),
('3b684737-8d18-42f5-9f6e-5628023c06de', 'default_cover.png', 'image/png', '2/aaf43e7d-53cf-43ac-baa7-6956a6ed5a43_default_cover.png', 3962, 'speed-knowledge', 2, '2025-11-21 18:40:32', '2025-11-21 18:40:32'),
('3ee4015c-969a-462d-acd6-b21e633046eb', '1e0b31efe30812e13c14f692776ddc5e.mp4', 'video/mp4', '2/289ffc9b-a910-4a56-a8f0-458ba5f2d2d3_1e0b31efe30812e13c14f692776ddc5e.mp4', 1172539, 'speed-knowledge', 2, '2026-01-13 16:55:23', '2026-01-13 16:55:23'),
('428b172c-e8ae-4e2d-ab3e-0549da487839', 'single.png', 'image/png', '2/a6291261-5820-4d1e-af20-626683946aa5_single.png', 291794, 'speed-knowledge', 2, '2026-01-12 20:34:33', '2026-01-12 20:34:33'),
('4e09d180-568b-4440-8ca8-379ce9ac1f08', 'single.png', 'image/png', '2/6f245e0d-ec00-4fab-b9ee-1ff37a74ca4b_single.png', 291794, 'speed-knowledge', 2, '2026-01-13 16:28:41', '2026-01-13 16:28:41'),
('53e43f41-8480-46b9-a2be-652269ad1499', 'default_cover.png', 'image/png', '2/6d27197f-9038-4f98-bedd-e42aec2e8842_default_cover.png', 3962, 'speed-knowledge', 2, '2025-11-21 18:25:07', '2025-11-21 18:25:07'),
('5b6258f5-6ba7-4989-90ca-28067b13c94b', '测试22221.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', '2/cf598d78-b0f8-4c2a-903e-0b430322a29e_测试22221.docx', 7133, 'speed-knowledge', 2, '2026-01-13 11:29:34', '2026-01-13 11:29:34'),
('61a7884c-b14d-441a-b213-bd45adb29b32', 'single.png', 'image/png', '2/88c69898-8084-4536-8bae-f245ae03e371_single.png', 291794, 'speed-knowledge', 2, '2026-01-12 19:14:28', '2026-01-12 19:14:28'),
('65ae1180-bde1-4386-9d5d-230ca3b3b8c3', 'single.png', 'image/png', '2/9933ac5e-5d26-4dc0-8a51-6e2ab6932a6e_single.png', 291794, 'speed-knowledge', 2, '2026-01-15 18:46:00', '2026-01-15 18:46:00'),
('6684b18b-1fea-4ff1-96f1-d52b33a2afa9', 'single.png', 'image/png', '2/92d78a33-f968-4f9a-81ec-7053cc215eb5_single.png', 291794, 'speed-knowledge', 2, '2026-01-12 16:48:51', '2026-01-12 16:48:51'),
('6fdec3c9-5881-464f-90c7-107520e94725', 'single.png', 'image/png', '2/1de77d48-103f-4c60-94c7-64fbc5a00012_single.png', 291794, 'speed-knowledge', 2, '2026-01-12 20:49:42', '2026-01-12 20:49:42'),
('7110403a-0f7e-4282-bed0-962395c6f2cc', 'single.png', 'image/png', '2/c2270460-5bc8-4079-a3ad-46539525332d_single.png', 291794, 'speed-knowledge', 2, '2026-01-13 10:32:01', '2026-01-13 10:32:01'),
('73760382-770a-4a6a-9c4b-f0153f30de0f', 'single.png', 'image/png', '2/8c96d84b-7973-43c0-b755-42386530b1ce_single.png', 291794, 'speed-knowledge', 2, '2026-01-13 09:12:52', '2026-01-13 09:12:52'),
('767f6667-40bd-4113-9e36-a7fb7ed46cc6', 'single.png', 'image/png', '2/a4664a9d-f7a7-43b2-890b-1a2041350384_single.png', 291794, 'speed-knowledge', 2, '2026-01-12 21:01:55', '2026-01-12 21:01:55'),
('781b262d-0d07-4bb2-8fcf-713536ef5417', 'single.png', 'image/png', '2/dc3e5442-fb2a-42cc-b97e-b1ab3f5a363d_single.png', 291794, 'speed-knowledge', 2, '2026-01-12 17:08:08', '2026-01-12 17:08:08'),
('7a8e847a-30c4-4820-8ad4-26011b4d85a2', 'A_IvwES5EwvsEAAAAAAAAAAABkARQnAQ.png', 'image/png', '2/f5127dbb-8eb3-4ed6-95f3-4ce2067ba3fc_A_IvwES5EwvsEAAAAAAAAAAABkARQnAQ.png', 3962, 'speed-knowledge', 2, '2025-11-19 18:36:45', '2025-11-19 18:36:45'),
('7ef51238-380e-48a9-8b86-2203c9caaa26', 'single.png', 'image/png', '2/83509576-043b-42c1-826d-f95c3cccf7cc_single.png', 291794, 'speed-knowledge', 2, '2026-01-13 09:10:39', '2026-01-13 09:10:39'),
('86383940-29b8-4b30-834c-7975992552d0', 'single.png', 'image/png', '2/9493f3e3-1854-41ca-98bf-3ab95cb42e81_single.png', 291794, 'speed-knowledge', 2, '2026-01-12 19:19:17', '2026-01-12 19:19:17'),
('883e2685-80ca-4c85-af4c-817c5042d38b', '测试22221.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', '2/3fb5b344-37e9-48b5-a929-4c846d9b073d_测试22221.docx', 7133, 'speed-knowledge', 2, '2026-01-13 14:31:24', '2026-01-13 14:31:24'),
('8984df27-c0aa-4339-9fe8-e30823415f49', 'single.png', 'image/png', '2/a4ac669e-56b4-4a50-a0eb-947ca5c96d6f_single.png', 291794, 'speed-knowledge', 2, '2026-01-12 19:21:07', '2026-01-12 19:21:07'),
('9f2e61eb-09f2-4cdd-88ef-d1789059d21e', 'single.png', 'image/png', '2/6928fc14-9822-44f9-900b-0917559f990f_single.png', 291794, 'speed-knowledge', 2, '2026-01-12 20:42:25', '2026-01-12 20:42:25'),
('a4fc4c20-755d-4435-b3c6-02fac4ed4633', '测试22221.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', '2/8460df49-8d45-45c3-871c-4b12a66811d0_测试22221.docx', 7133, 'speed-knowledge', 2, '2026-01-13 11:22:43', '2026-01-13 11:22:43'),
('a6b14c83-5f2d-454c-866c-263a0aa97dd2', 'single.png', 'image/png', '2/1d6a8fa8-392f-40da-9bb0-3ae04f953a13_single.png', 291794, 'speed-knowledge', 2, '2026-01-12 17:08:53', '2026-01-12 17:08:53'),
('aea742c2-7aba-4bf3-aeb0-60ea416d043f', 'single.png', 'image/png', '2/6c5900cb-4641-4204-b3e9-fb35fed33eed_single.png', 291794, 'speed-knowledge', 2, '2026-01-12 18:17:34', '2026-01-12 18:17:34'),
('b0b96862-80df-4ab5-ba55-54c0f188aa60', 'single.png', 'image/png', '2/26d815a8-c1cd-477a-87bf-2d296e38e99c_single.png', 291794, 'speed-knowledge', 2, '2026-01-12 16:41:33', '2026-01-12 16:41:33'),
('b480842b-232a-44a6-b47d-021428e391b0', 'single.png', 'image/png', '2/0ad7f308-8042-4d2c-8a75-8c95837c88dd_single.png', 291794, 'speed-knowledge', 2, '2026-01-12 16:48:14', '2026-01-12 16:48:14'),
('b72d1d4d-ca6f-4b5f-9b3a-28f179633214', 'single.png', 'image/png', '2/d41e9c8e-9981-49f2-8808-b8ad08be3914_single.png', 291794, 'speed-knowledge', 2, '2026-01-12 19:18:18', '2026-01-12 19:18:18'),
('b7551284-c924-4829-9842-76e39e281fa0', 'single.png', 'image/png', '2/7b7b298c-4a66-4bb3-882b-f5698d2b5b4e_single.png', 291794, 'speed-knowledge', 2, '2026-01-12 20:30:05', '2026-01-12 20:30:05'),
('c026bcd1-157f-44f5-be03-5dfd29b72e8d', '测试22221.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', '2/99fe334c-9b5a-4822-99fd-58d8016dcb9d_测试22221.docx', 7133, 'speed-knowledge', 2, '2026-01-15 18:46:20', '2026-01-15 18:46:20'),
('c7059590-f8c2-49c9-b16b-f7dbda3051ed', 'single.png', 'image/png', '2/9688a954-4aa6-44e5-9e57-8bc0da95f7b1_single.png', 291794, 'speed-knowledge', 2, '2026-01-12 17:35:55', '2026-01-12 17:35:55'),
('c8120f07-4cc1-463e-9119-eface352cd82', 'default_cover.png', 'image/png', '2/20df2ccd-d338-4cc8-8ad4-e919b19a27a8_default_cover.png', 3962, 'speed-knowledge', 2, '2025-11-21 18:46:27', '2025-11-21 18:46:27'),
('cc3db391-5fb6-4914-bbe2-068a221d588d', '中电万维[2022]18号 .pdf', 'application/pdf', '2/f94ab1b7-cd0d-4ac8-b27b-6283697fdbc8_中电万维[2022]18号 .pdf', 785232, 'speed-knowledge', 2, '2026-01-13 16:56:06', '2026-01-13 16:56:06'),
('cd0d72e1-b56a-473a-b6e0-ab14069a13da', 'single.png', 'image/png', '2/d62f811f-e18e-4a96-9046-60d14c26c4e7_single.png', 291794, 'speed-knowledge', 2, '2026-01-13 10:06:07', '2026-01-13 10:06:07'),
('cdfa6e97-f566-4247-bd6a-a0c15a117124', 'single.png', 'image/png', '2/93807c6e-7bcc-4298-a36a-eae8a5ff02e0_single.png', 291794, 'speed-knowledge', 2, '2026-01-12 20:17:57', '2026-01-12 20:17:57'),
('d191a553-6448-44ed-9493-a835b13dbd31', 'single.png', 'image/png', '2/4e46dfd2-b8dc-47b5-a907-b9b5ffa221d0_single.png', 291794, 'speed-knowledge', 2, '2026-01-12 19:25:26', '2026-01-12 19:25:26'),
('d1f0e706-5dd7-45ea-a508-dd0fac9eb0a5', 'single.png', 'image/png', '2/15e96e98-96c1-41fe-8e95-54d65ae1c6fe_single.png', 291794, 'speed-knowledge', 2, '2026-01-12 20:51:21', '2026-01-12 20:51:21'),
('d1fa32b7-8730-44a4-806e-e509dce13829', 'default_cover.png', 'image/png', '2/dda33992-aa13-4517-a37c-fa5cb91c89d0_default_cover.png', 3962, 'speed-knowledge', 2, '2025-11-21 17:57:13', '2025-11-21 17:57:13'),
('d6afdbf0-c14b-4305-b77d-0793ee217e26', 'single.png', 'image/png', '2/7a5e5f14-f1a8-453f-9419-a73f80af5814_single.png', 291794, 'speed-knowledge', 2, '2026-01-12 20:46:46', '2026-01-12 20:46:46'),
('da56ccf0-ae60-4323-b441-3c8059630ff3', '缩小图片.png', 'image/png', '2/d149cf90-aba4-4297-b7d8-67f22bb105d1_缩小图片.png', 2233003, 'speed-knowledge', 2, '2026-02-02 14:38:42', '2026-02-02 14:38:42'),
('dd587dd7-aada-4c95-9c65-1493583ca992', 'single.png', 'image/png', '2/b76ddbe4-bbce-495b-ad42-3fd26e7b2fb1_single.png', 291794, 'speed-knowledge', 2, '2026-01-12 19:05:44', '2026-01-12 19:05:44'),
('deacd384-7095-4a52-b004-b5f22a1a2199', 'single.png', 'image/png', '2/8f63a7da-4f4c-4a0b-8490-535618be4d9c_single.png', 291794, 'speed-knowledge', 2, '2026-01-12 19:16:22', '2026-01-12 19:16:22'),
('e39f678c-bfe5-40c5-b043-3d27035af3b2', '缩小图片.png', 'image/png', '2/4ae35eb7-8b2f-4c22-b1a5-542afc8033cf_缩小图片.png', 2233003, 'speed-knowledge', 2, '2026-01-23 19:08:28', '2026-01-23 19:08:28'),
('e61678c0-a321-4b18-8fc9-6b99d181a180', 'single.png', 'image/png', '2/c6f2daae-5e73-4808-8a17-1b006daaba89_single.png', 291794, 'speed-knowledge', 2, '2026-01-12 20:44:23', '2026-01-12 20:44:23'),
('e6dc91f5-25d4-427f-ae04-aa7a577737b0', '测试22221.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', '2/6e81daa1-d85a-4554-b980-7f3999c3ce82_测试22221.docx', 7133, 'speed-knowledge', 2, '2026-01-13 14:24:31', '2026-01-13 14:24:31'),
('ecef5240-e043-4cdf-a6ab-ca200965bfbf', 'single.png', 'image/png', '2/3a27d6fa-cccb-4c51-8b15-af44b42cbc3f_single.png', 291794, 'speed-knowledge', 2, '2026-01-12 21:01:39', '2026-01-12 21:01:39'),
('ed5d8fc6-5771-4832-a720-b5935a826db4', 'single.png', 'image/png', '2/9a19881a-2e34-43ff-b004-28fd46e9d931_single.png', 291794, 'speed-knowledge', 2, '2026-01-12 17:25:01', '2026-01-12 17:25:01'),
('f2362759-ce1e-4632-83ba-bdbf9020d5c1', 'single.png', 'image/png', '2/39001891-47cd-40c0-b399-90dfad430601_single.png', 291794, 'speed-knowledge', 2, '2026-01-12 16:59:27', '2026-01-12 16:59:27');

-- --------------------------------------------------------

--
-- 表的结构 `collaborator`
--

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
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- 转存表中的数据 `collaborator`
--

INSERT INTO `collaborator` (`id`, `knowledge_id`, `document_id`, `user_id`, `role`, `target_type`, `status`, `source`, `created_at`, `updated_at`) VALUES
('6f44b1c5-087f-449f-ae22-a9efa25d07e6', 'd4bcf15c-01b9-4998-a243-86bc2dc4e92b', NULL, 2, 3, 'knowledge', 2, 0, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('9dbefe1f-5a2d-4743-a378-a1ef109a0684', NULL, 'c926bbfa-e7da-492a-a885-b29314cd5fa5', 2, 3, 'document', 2, 0, '2026-03-17 14:29:33', '2026-03-17 14:29:33'),
('b4e13b82-379d-41b0-830c-cc8a2ec65811', NULL, 'd11be93d-de3d-4838-b67c-b33360e2745b', 2, 3, 'document', 2, 0, '2026-03-17 15:48:38', '2026-03-17 15:48:38'),
('ff8d25a9-9011-4c3a-8963-bc215cf6ec49', '28ca1a60-11a9-46ba-a075-f17043823adc', NULL, 2, 3, 'knowledge', 2, 0, '2026-03-17 15:44:39', '2026-03-17 15:44:39');

-- --------------------------------------------------------

--
-- 表的结构 `collect`
--

CREATE TABLE `collect` (
  `id` varchar(36) NOT NULL,
  `user_id` int NOT NULL COMMENT '用户ID',
  `resource_type` varchar(20) NOT NULL COMMENT '资源类型',
  `knowledge_id` varchar(36) DEFAULT NULL COMMENT '知识库ID',
  `document_id` varchar(36) DEFAULT NULL COMMENT '文档ID',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

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
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  `view_count` int NOT NULL COMMENT '浏览次数',
  `deleted_at` datetime DEFAULT NULL COMMENT '删除时间(NULL表示未删除)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- 转存表中的数据 `document_base`
--

INSERT INTO `document_base` (`id`, `user_id`, `knowledge_id`, `name`, `slug`, `type`, `is_public`, `content_updated_at`, `created_at`, `updated_at`, `view_count`, `deleted_at`) VALUES
('c926bbfa-e7da-492a-a885-b29314cd5fa5', 2, 'd4bcf15c-01b9-4998-a243-86bc2dc4e92b', 'ykx测试文档122', 'EnUvxNSFMN3KTjTf', 'word', 0, '2026-03-17 15:05:18', '2026-03-17 14:29:33', '2026-03-17 15:05:18', 1, NULL),
('d11be93d-de3d-4838-b67c-b33360e2745b', 2, '28ca1a60-11a9-46ba-a075-f17043823adc', '如何插入图片', 'PjFOgZHUvwo1eADM', 'word', 0, '2026-03-17 15:52:04', '2026-03-17 15:48:38', '2026-03-17 15:52:04', 1, NULL);

-- --------------------------------------------------------

--
-- 表的结构 `document_content`
--

CREATE TABLE `document_content` (
  `id` varchar(36) NOT NULL COMMENT '主键',
  `document_id` varchar(36) NOT NULL COMMENT '所属文档',
  `content` longblob NOT NULL COMMENT '文档内容(为协同编辑的的二进制数据)',
  `content_updated_at` datetime DEFAULT NULL COMMENT '内容最近更新时间',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  `node_json` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '文档内容(为协同编辑的的二进制json数据)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- 转存表中的数据 `document_content`
--

INSERT INTO `document_content` (`id`, `document_id`, `content`, `content_updated_at`, `created_at`, `updated_at`, `node_json`) VALUES
('4c0007c3-b77c-44eb-a122-1f52fa79bb9e', 'c926bbfa-e7da-492a-a885-b29314cd5fa5', 0x0804b9eb9b9e0a0001010764656661756c740187b9eb9b9e0a0003097061726167726170682800b9eb9b9e0a0106696e64656e74017d002100b9eb9b9e0a01066e6f646549640102ccad88cb070001010764656661756c7402000b04f0fdcdb2060001010764656661756c740187f0fdcdb2060003097061726167726170682800f0fdcdb2060106696e64656e74017d002100f0fdcdb20601066e6f646549640102a0c1be8d040001010764656661756c7401000601faaed9d103008487ca82a901230232320797f1ce99030007010764656661756c7403057469746c658197f1ce990300010002c197f1ce990301a0c1be8d040001000b070097f1ce99030006010097f1ce990310040a87ca82a901008197f1ce990314018487ca82a9010003796b788187ca82a90103098487ca82a9010c06e6b58be8af958187ca82a9010e128487ca82a9012007e69687e6a1a3310700f0fdcdb2060106040087ca82a90124063132333333330700b9eb9b9e0a0106040087ca82a9012b0331313105a1a7cc7f0087b9eb9b9e0a0103097061726167726170682800a1a7cc7f0006696e64656e74017d000700a1a7cc7f00060400a1a7cc7f020334343481a1a7cc7f050307b9eb9b9e0a0200010301ccad88cb0701000df0fdcdb2060200010301a0c1be8d0401000797f1ce990302010f110487ca82a90103000104090f12a1a7cc7f010603, '2026-03-17 15:05:18', '2026-03-17 14:29:33', '2026-03-17 15:05:18', '{\"default\":{\"type\":\"doc\",\"content\":[{\"type\":\"title\",\"content\":[{\"type\":\"text\",\"text\":\"ykx测试文档122\"}]},{\"type\":\"paragraph\",\"attrs\":{\"indent\":0},\"content\":[{\"type\":\"text\",\"text\":\"123333\"}]},{\"type\":\"paragraph\",\"attrs\":{\"indent\":0},\"content\":[{\"type\":\"text\",\"text\":\"111\"}]},{\"type\":\"paragraph\",\"attrs\":{\"indent\":0},\"content\":[{\"type\":\"text\",\"text\":\"444\"}]}]}}'),
('b8503a9f-20e6-45a3-a4ac-c6644b7b8a5e', 'd11be93d-de3d-4838-b67c-b33360e2745b', 0x0268d6c9b36a008188dd90280001008801c188dd902800d6c9b36a0001000e8488dd90280612e5a682e4bd95e68f92e585a5e59bbee7898787d6c9b36a0003097061726167726170680700d6c9b36a9e01060600d6c9b36a9f0104626f6c64027b7d84d6c9b36aa0010ce68f92e585a5e4b88ae4bca086d6c9b36aa40104626f6c64046e756c6c84d6c9b36aa501b001efbc9ae5a682e8a681e4bda0e8a681e59ca8e69687e6a1a3e68f92e585a5e59bbee78987efbc8ce58fafe4bba5e98089e68ba9e59ca8e58da1e78987e68f92e585a5e4b8ade98089e68ba9e2809ce59bbee78987e2809de38082e5908ce697b6e694afe68c81e4bba5e4b88be5bfabe68db7e994aeefbc88e694afe68c81e4b8ade69687efbc8ce68bbce99fb3e5928ce88bb1e69687efbc892fe59bbee789872f74757069616e2f74702f696d61676581d6c9b36aeb01342800d6c9b36a9e0106696e64656e74017d00c788dd902800d6c9b36a8901030768656164696e670700d6c9b36aa102060600d6c9b36aa20204626f6c64027b7d84d6c9b36aa30212e5bfabe9809fe68f92e585a5e59bbee7898786d6c9b36aa90204626f6c64046e756c6c2800d6c9b36aa10206696e64656e74017d002800d6c9b36aa102056c6576656c017d0387d6c9b36a9e0103097061726167726170680700d6c9b36aad02060600d6c9b36aae0204626f6c64027b7d84d6c9b36aaf020ce79bb4e68ea5e68b96e585a586d6c9b36ab30204626f6c64046e756c6c84d6c9b36ab4022defbc9ae8bf98e694afe68c81e79bb4e68ea5e5b086e59bbee78987e68b96e585a5e588b0e7bc96e8be91e599a881d6c9b36ac3021f2800d6c9b36aad0206696e64656e74017d0087d6c9b36aad0203097061726167726170680700d6c9b36ae402060600d6c9b36ae50204626f6c64027b7d84d6c9b36ae6020ce79bb4e68ea5e7b298e8b4b486d6c9b36aea0204626f6c64046e756c6c84d6c9b36aeb024befbc9ae59bbee78987e79bb4e68ea5e5a48de588b6e588b0e7bc96e8be91e599a8e4b8adefbc8ce8bf99e6a0b7e4b99fe58fafe4bba5e79bb4e68ea5e4b88ae4bca0e59bbee78987e380822800d6c9b36ae40206696e64656e74017d0087d6c9b36ae40203097061726167726170682800d6c9b36a860306696e64656e74017d000700d6c9b36a8603060400d6c9b36a880372e5b086e9bca0e6a087e682ace6b5aee588b0e59bbee78987e4b88aefbc8ce58fafe594a4e98692e59bbee78987e5b7a5e585b7e6a08fefbc9be782b9e587bbe59bbee78987e58fb3e4b88ae8a792e2809c2e2e2ee2809defbc8ce58fafe8bf9be8a18ce69bb4e5a49ae6938de4bd9ce38082c7d6c9b36ae402d6c9b36a8603030768656164696e670700d6c9b36ab103060400d6c9b36ab2030ce58a9fe883bde7ae80e4bb8b2800d6c9b36ab10306696e64656e74017d002800d6c9b36ab103056c6576656c017d02c7d6c9b36ab103d6c9b36a860303097061726167726170680700d6c9b36ab903060400d6c9b36aba0306e9809ae8bf8786d6c9b36abc0304626f6c64027b7d84d6c9b36abd030fe59bbee78987e5b7a5e585b7e6a08f86d6c9b36ac20304626f6c64046e756c6c84d6c9b36ac3039301efbc8ce58fafe4bba5e5afb9e59bbee78987e8bf9be8a18ce8aebee7bdaee38082e694afe68c81e4bfaee694b9e59bbee78987e5a4a7e5b08fe38081e6a0b7e5bc8fefbc8ce58fafe4bba5e5afb9e59bbee78987e8bf9be8a18ce8a381e589aae38081e6978be8bdacefbc8ce8bf98e58fafe4bba5e6b7bbe58aa0e59bbee78987e68f8fe8bfb0e38081e993bee68ea5e380822800d6c9b36ab90306696e64656e74017d0081d6c9b36a8603010001c7d6c9b36a8603d6c9b36af603030768656164696e670700d6c9b36af803060400d6c9b36af90312e4bfaee694b9e59bbee78987e5b0bae5afb82800d6c9b36af80306696e64656e74017d002800d6c9b36af803056c6576656c017d04c7d6c9b36af803d6c9b36af603030b6f7264657265644c6973740700d6c9b36a820403086c6973744974656d0700d6c9b36a830403097061726167726170680700d6c9b36a8404060400d6c9b36a850448e79bb4e68ea5e68b96e68bbdefbc9ae98089e4b8ade59bbee78987efbc8ce68b96e58aa8e59bbee78987203420e4b8aae8a792e58fafe4bfaee694b9e59bbee78987e5a4a7e5b08f2800d6c9b36a840406696e64656e74017d002800d6c9b36a830406696e64656e74017d0087d6c9b36a830403086c6973744974656d0700d6c9b36aa20403097061726167726170680700d6c9b36aa304060400d6c9b36aa40430e59bbee78987e5b7a5e585b7e6a08fe8aebee7bdaee59bbee78987e5aebde5928ce9ab98e68896e799bee58886e6af942800d6c9b36aa30406696e64656e74017d002800d6c9b36aa20406696e64656e74017d002800d6c9b36a8204057374617274017d0181d6c9b36aa204010003c1d6c9b36aa204d6c9b36ab804010003c1d6c9b36a8204d6c9b36af60301000fc7d6c9b36a8204d6c9b36ac004030768656164696e672800d6c9b36ad00406696e64656e74017d002800d6c9b36ad004056c6576656c017d040700d6c9b36ad004060100d6c9b36ad3040484d6c9b36ad70406e59bbee7898781d6c9b36ad9041384d6c9b36aec0406e694afe68c8181d6c9b36aee040284d6c9b36af00403e79a8481d6c9b36af1040484d6c9b36af50406e6a0bce5bc8f81d6c9b36af7040384d6c9b36afa0403e69c89c1d6c9b36ad004d6c9b36ac004010003c7d6c9b36ad004d6c9b36afc040309636f6465426c6f636b2800d6c9b36a8005086c616e6775616765017709706c61696e746578742800d6c9b36a80050d6c616e6775616765416c696173017709706c61696e746578742800d6c9b36a8005047772617001782800d6c9b36a8005057468656d6501770e61746f6d2d6f6e652d6c696768742800d6c9b36a80050a6973457870616e64656401782800d6c9b36a8005066865696768740177033235300700d6c9b36a8005060400d6c9b36a870516706e670a6769660a6a7067e380816a7065670a7376670388dd90280007010764656661756c7403057469746c65070088dd90280006010088dd9028010502d6c9b36a0b009801ec0134c4021ff60302b80418d40404da0413ef0402f20404f80403fc040488dd9028010205, '2026-03-17 15:52:04', '2026-03-17 15:48:38', '2026-03-17 15:52:04', '{\"default\":{\"type\":\"doc\",\"content\":[{\"type\":\"title\",\"content\":[{\"type\":\"text\",\"text\":\"如何插入图片\"}]},{\"type\":\"heading\",\"attrs\":{\"indent\":0,\"level\":3},\"content\":[{\"type\":\"text\",\"text\":\"快速插入图片\",\"marks\":[{\"type\":\"bold\",\"attrs\":{}}]}]},{\"type\":\"paragraph\",\"attrs\":{\"indent\":0},\"content\":[{\"type\":\"text\",\"text\":\"插入上传\",\"marks\":[{\"type\":\"bold\",\"attrs\":{}}]},{\"type\":\"text\",\"text\":\"：如要你要在文档插入图片，可以选择在卡片插入中选择“图片”。同时支持以下快捷键（支持中文，拼音和英文）/图片/tupian/tp/image\"}]},{\"type\":\"paragraph\",\"attrs\":{\"indent\":0},\"content\":[{\"type\":\"text\",\"text\":\"直接拖入\",\"marks\":[{\"type\":\"bold\",\"attrs\":{}}]},{\"type\":\"text\",\"text\":\"：还支持直接将图片拖入到编辑器\"}]},{\"type\":\"paragraph\",\"attrs\":{\"indent\":0},\"content\":[{\"type\":\"text\",\"text\":\"直接粘贴\",\"marks\":[{\"type\":\"bold\",\"attrs\":{}}]},{\"type\":\"text\",\"text\":\"：图片直接复制到编辑器中，这样也可以直接上传图片。\"}]},{\"type\":\"heading\",\"attrs\":{\"indent\":0,\"level\":2},\"content\":[{\"type\":\"text\",\"text\":\"功能简介\"}]},{\"type\":\"paragraph\",\"attrs\":{\"indent\":0},\"content\":[{\"type\":\"text\",\"text\":\"通过\"},{\"type\":\"text\",\"text\":\"图片工具栏\",\"marks\":[{\"type\":\"bold\",\"attrs\":{}}]},{\"type\":\"text\",\"text\":\"，可以对图片进行设置。支持修改图片大小、样式，可以对图片进行裁剪、旋转，还可以添加图片描述、链接。\"}]},{\"type\":\"paragraph\",\"attrs\":{\"indent\":0},\"content\":[{\"type\":\"text\",\"text\":\"将鼠标悬浮到图片上，可唤醒图片工具栏；点击图片右上角“...”，可进行更多操作。\"}]},{\"type\":\"heading\",\"attrs\":{\"indent\":0,\"level\":4},\"content\":[{\"type\":\"text\",\"text\":\"修改图片尺寸\"}]},{\"type\":\"orderedList\",\"attrs\":{\"start\":1},\"content\":[{\"type\":\"listItem\",\"attrs\":{\"indent\":0},\"content\":[{\"type\":\"paragraph\",\"attrs\":{\"indent\":0},\"content\":[{\"type\":\"text\",\"text\":\"直接拖拽：选中图片，拖动图片 4 个角可修改图片大小\"}]}]},{\"type\":\"listItem\",\"attrs\":{\"indent\":0},\"content\":[{\"type\":\"paragraph\",\"attrs\":{\"indent\":0},\"content\":[{\"type\":\"text\",\"text\":\"图片工具栏设置图片宽和高或百分比\"}]}]}]},{\"type\":\"heading\",\"attrs\":{\"indent\":0,\"level\":4},\"content\":[{\"type\":\"text\",\"text\":\"图片支持的格式有\"}]},{\"type\":\"codeBlock\",\"attrs\":{\"language\":\"plaintext\",\"languageAlias\":\"plaintext\",\"wrap\":true,\"theme\":\"atom-one-light\",\"isExpanded\":true,\"height\":\"250\"},\"content\":[{\"type\":\"text\",\"text\":\"png\\ngif\\njpg、jpeg\\nsvg\"}]}]}}');

-- --------------------------------------------------------

--
-- 表的结构 `document_edit_history`
--

CREATE TABLE `document_edit_history` (
  `id` varchar(36) NOT NULL,
  `document_id` varchar(36) NOT NULL COMMENT '所属文档',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  `edited_user_id` int NOT NULL COMMENT '编辑的用户',
  `edited_datetime` datetime DEFAULT NULL COMMENT '编辑时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- 转存表中的数据 `document_edit_history`
--

INSERT INTO `document_edit_history` (`id`, `document_id`, `created_at`, `updated_at`, `edited_user_id`, `edited_datetime`) VALUES
('0818b06e-7759-44d4-8cbf-872171143779', 'd11be93d-de3d-4838-b67c-b33360e2745b', '2026-03-17 15:48:41', '2026-03-17 15:48:41', 2, '2026-03-17 15:48:41'),
('fad1a038-65c8-4906-9cbb-abb201286e44', 'c926bbfa-e7da-492a-a885-b29314cd5fa5', '2026-03-17 14:29:35', '2026-03-17 14:29:35', 2, '2026-03-17 14:29:36');

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
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted_at` datetime DEFAULT NULL COMMENT '删除时间(NULL表示未删除)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- 转存表中的数据 `document_node`
--

INSERT INTO `document_node` (`id`, `type`, `title`, `parent_id`, `first_child_id`, `document_id`, `prev_id`, `next_id`, `knowledge_id`, `created_at`, `updated_at`, `deleted_at`) VALUES
('299bb78a-e37f-4567-8115-47206af9dd8c', 'DOC', '如何插入图片', NULL, NULL, 'd11be93d-de3d-4838-b67c-b33360e2745b', NULL, NULL, '28ca1a60-11a9-46ba-a075-f17043823adc', '2026-03-17 15:48:38', '2026-03-17 15:48:38', NULL),
('bfe2033d-f287-4e9c-b837-9a1bcc7b534b', 'DOC', 'ykx测试文档122', NULL, NULL, 'c926bbfa-e7da-492a-a885-b29314cd5fa5', NULL, NULL, 'd4bcf15c-01b9-4998-a243-86bc2dc4e92b', '2026-03-17 14:29:33', '2026-03-17 14:29:33', NULL);

-- --------------------------------------------------------

--
-- 表的结构 `document_view_history`
--

CREATE TABLE `document_view_history` (
  `id` varchar(36) NOT NULL,
  `document_id` varchar(36) NOT NULL COMMENT '所属文档',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  `viewed_user_id` int NOT NULL COMMENT '浏览的用户',
  `viewed_datetime` datetime DEFAULT NULL COMMENT '浏览时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- 转存表中的数据 `document_view_history`
--

INSERT INTO `document_view_history` (`id`, `document_id`, `created_at`, `updated_at`, `viewed_user_id`, `viewed_datetime`) VALUES
('8788ecf3-b41d-44f5-b672-bb3c4e2e2c3a', 'd11be93d-de3d-4838-b67c-b33360e2745b', '2026-03-17 16:07:53', '2026-03-17 16:07:53', 2, '2026-03-17 20:09:21'),
('fe452832-135d-4738-b4ea-cfd7cf5e70dc', 'c926bbfa-e7da-492a-a885-b29314cd5fa5', '2026-03-17 14:32:28', '2026-03-17 14:32:28', 2, '2026-03-17 14:44:32');

-- --------------------------------------------------------

--
-- 表的结构 `invitation`
--

CREATE TABLE `invitation` (
  `id` varchar(36) NOT NULL COMMENT '主键',
  `knowledge_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '所属知识库',
  `document_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '所属文档',
  `inviter_id` int DEFAULT NULL COMMENT '被邀请用户id',
  `token` varchar(45) NOT NULL COMMENT '邀请链接token',
  `role` int NOT NULL COMMENT '角色',
  `invitate_type` varchar(20) NOT NULL COMMENT '邀请来源:knowledge-知识库,document-文档',
  `need_approval` int DEFAULT NULL COMMENT '是否需要审批:0-否,1-是',
  `status` int NOT NULL COMMENT '状态:1-正常,2-已撤销',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

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
  `content_updated_at` datetime DEFAULT NULL COMMENT '内容最近更新时间',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `group_id` varchar(36) NOT NULL COMMENT '所属分组',
  `icon` varchar(20) NOT NULL COMMENT '知识库图标',
  `enable_catalog` tinyint(1) NOT NULL DEFAULT '1' COMMENT '是否启用目录',
  `layout` varchar(20) NOT NULL COMMENT '布局',
  `sort` varchar(20) NOT NULL COMMENT '排序',
  `enable_custom_body` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否启用自定义模块',
  `enable_user_feed` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否显示协同人员',
  `deleted_at` datetime DEFAULT NULL COMMENT '删除时间(NULL表示未删除)',
  `team_id` varchar(36) NOT NULL COMMENT '所属团队',
  `space_id` varchar(36) NOT NULL COMMENT '所属空间（冗余字段）'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- 转存表中的数据 `knowledge_base`
--

INSERT INTO `knowledge_base` (`id`, `user_id`, `name`, `slug`, `description`, `cover_url`, `is_public`, `content_updated_at`, `created_at`, `updated_at`, `group_id`, `icon`, `enable_catalog`, `layout`, `sort`, `enable_custom_body`, `enable_user_feed`, `deleted_at`, `team_id`, `space_id`) VALUES
('28ca1a60-11a9-46ba-a075-f17043823adc', 2, '用于实现rag的知识库1', 'Nma4aX', '用于提供一些说明文档给rag', '{\"id\": \"0567a480-0f34-4ab8-9e5d-6ab99dfcd191\", \"fileName\": \"default_cover.png\", \"fileSize\": 3962, \"fileType\": \"image/png\"}', 0, NULL, '2026-03-17 15:44:39', '2026-03-17 15:44:39', '5c75553f-2f64-4b48-a55a-9736b8d6c746', 'icon-book-5', 1, 'catalog', 'catalog', 0, 0, NULL, '1bc00c0d-8408-442a-9a9a-5c3aa726a127', '7e74e342-9086-4f1f-b621-27578d856208'),
('d4bcf15c-01b9-4998-a243-86bc2dc4e92b', 2, 'ykx测试知识库A', 'o6BXQ1', '111', '{\"id\": \"0567a480-0f34-4ab8-9e5d-6ab99dfcd191\", \"fileName\": \"default_cover.png\", \"fileSize\": 3962, \"fileType\": \"image/png\"}', 0, NULL, '2026-02-10 20:26:02', '2026-02-10 20:26:02', '5c75553f-2f64-4b48-a55a-9736b8d6c746', 'icon-book-0', 1, 'catalog', 'catalog', 0, 0, NULL, '1bc00c0d-8408-442a-9a9a-5c3aa726a127', '7e74e342-9086-4f1f-b621-27578d856208');

-- --------------------------------------------------------

--
-- 表的结构 `knowledge_daily_stats`
--

CREATE TABLE `knowledge_daily_stats` (
  `id` varchar(36) NOT NULL,
  `knowledge_id` varchar(36) NOT NULL,
  `stats_date` date NOT NULL,
  `word_count` int NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
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
  `display_config` json DEFAULT NULL COMMENT '显示配置',
  `deleted_at` datetime DEFAULT NULL COMMENT '删除时间(NULL表示未删除)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- 转存表中的数据 `knowledge_group`
--

INSERT INTO `knowledge_group` (`id`, `user_id`, `group_name`, `order_index`, `is_default`, `created_at`, `updated_at`, `display_config`, `deleted_at`) VALUES
('06458191-389f-4412-9c7a-8273b61d045a', 4, '我的知识库', 0, 1, '2026-01-06 15:35:35', '2026-01-06 15:35:35', '{\"type\": \"card\", \"style\": \"detail\", \"doc_order_type\": 1, \"show_knowledge_icon\": true, \"show_knowledge_description\": true}', NULL),
('1d1dc844-4033-49f9-b3c5-668c38a7a7a6', 10, '我的知识库', 0, 1, '2026-01-20 20:25:54', '2026-01-20 20:25:54', '{\"type\": \"card\", \"style\": \"detail\", \"doc_order_type\": 1, \"show_knowledge_icon\": true, \"show_knowledge_description\": true}', NULL),
('30ae65c3-7e12-4640-9ee4-2ecd73fac02c', 1, '我的知识库', 0, 1, '2026-01-04 19:29:16', '2026-01-04 19:29:16', '{\"type\": \"card\", \"style\": \"detail\", \"doc_order_type\": 1, \"show_knowledge_icon\": true, \"show_knowledge_description\": true}', NULL),
('513eabf6-c748-4c6b-9ec1-15ff701a3faa', 3, '我的知识库', 0, 1, '2026-01-04 20:00:14', '2026-01-04 20:00:14', '{\"type\": \"card\", \"style\": \"detail\", \"doc_order_type\": 1, \"show_knowledge_icon\": true, \"show_knowledge_description\": true}', NULL),
('51df5499-93ac-4843-aaf5-2bc0223ceec2', 3, '我的知识库', 0, 1, '2025-12-16 17:44:45', '2025-12-16 17:44:45', '{\"type\": \"card\", \"style\": \"detail\", \"doc_order_type\": 1, \"show_knowledge_icon\": true, \"show_knowledge_description\": true}', NULL),
('5c75553f-2f64-4b48-a55a-9736b8d6c746', 2, '我的知识库', 0, 1, '2025-11-19 11:49:57', '2025-11-19 11:49:57', '{\"type\": \"card\", \"style\": \"detail\", \"doc_order_type\": 1, \"show_knowledge_icon\": true, \"show_knowledge_description\": true}', NULL);

-- --------------------------------------------------------

--
-- 表的结构 `permission_abilities`
--

CREATE TABLE `permission_abilities` (
  `id` varchar(36) NOT NULL,
  `permission_group_id` varchar(36) NOT NULL COMMENT '权限组ID',
  `ability_key` varchar(30) NOT NULL COMMENT '能力键',
  `enable` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否启用',
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT (now())
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- 转存表中的数据 `permission_abilities`
--

INSERT INTO `permission_abilities` (`id`, `permission_group_id`, `ability_key`, `enable`, `created_at`, `updated_at`) VALUES
('01123ba5-6bdc-487f-9e86-867eeb679d9a', '8a77b0f9-af46-475f-b220-c6498e9690b1', 'doc_share', 1, '2026-03-03 11:35:01', '2026-03-03 11:35:01'),
('0275952a-9c17-4fa6-923e-eadc72887d31', '71e84916-2164-4797-9625-a1f17778564f', 'modify_book_permission', 0, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('03a78c9b-0f18-4e88-9b1f-798c65b22f40', '3c4e3ec2-2891-4622-808e-a3d422f6b1c0', 'doc_read', 1, '2026-03-02 10:34:03', '2026-03-02 10:34:03'),
('04c88a69-f048-425f-a671-fdee4427f532', '3c4e3ec2-2891-4622-808e-a3d422f6b1c0', 'doc_edit', 1, '2026-03-02 10:34:03', '2026-03-02 10:34:03'),
('07101b4f-b6d2-4d7d-a228-df8188e53bdf', '3c4e3ec2-2891-4622-808e-a3d422f6b1c0', 'doc_comment', 1, '2026-03-02 10:34:03', '2026-03-02 10:34:03'),
('07a49d8c-c7c6-4cb6-9729-9301c65adca9', 'd63c0b3e-5db8-4d3e-b77d-2dd2a26654c1', 'doc_create', 0, '2026-03-17 14:29:33', '2026-03-17 14:29:33'),
('097dd467-eaad-4328-8d57-cbae55df3045', '5a7dbae6-058f-4874-af49-540bf1a7de84', 'doc_edit', 0, '2026-03-04 19:23:23', '2026-03-04 19:23:23'),
('099d660b-48fc-4894-93dc-698efb8ad5a4', '29981c27-113a-436f-9eed-a03f7fb9981d', 'doc_read', 0, '2026-03-02 10:34:03', '2026-03-02 10:34:03'),
('0a15e567-3923-4f2a-a2fa-192617d5d2c1', '1e9cf2ee-1e0d-42a1-9ced-47018f31b91c', 'doc_join', 0, '2026-02-26 18:27:52', '2026-02-26 18:27:52'),
('0a3485cb-2163-4374-85ad-df5f4561b793', '2efc8a38-3db1-4029-801d-a462e90f35bb', 'doc_delete', 1, '2026-03-04 19:23:23', '2026-03-04 19:23:23'),
('0b9eaa64-6b73-4e2f-ad49-51fbac9fbe38', 'c14494ca-f2f3-46b5-9c18-9f0ac99f6109', 'doc_delete', 0, '2026-02-26 18:27:52', '2026-02-26 18:27:52'),
('0c67e515-efaf-4c9a-8fa9-acc8c788af1d', '4d5e99b4-ce0c-41b7-8ce7-0b7b032ad0d3', 'doc_edit', 1, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('113b2b76-9b90-4be3-8271-6cf32a848bee', '37419883-832b-4b5c-ab18-c4a8e9997fad', 'doc_delete', 0, '2026-03-02 10:09:52', '2026-03-02 10:09:52'),
('118c75b6-93de-43ea-bef5-3d181fdcb3be', '29981c27-113a-436f-9eed-a03f7fb9981d', 'doc_comment', 0, '2026-03-02 10:34:03', '2026-03-02 10:34:03'),
('12dd4c6e-3846-4bba-9d63-92ab768d64bd', '63f80453-a04b-43a8-8a3d-78721defb43c', 'doc_comment', 0, '2026-03-17 14:29:33', '2026-03-17 14:29:33'),
('13c65717-39c2-4fb2-b140-4af65db9eddc', '642cd1b6-4c08-40fb-833c-a3a6039b3d55', 'doc_share', 0, '2026-03-04 15:21:14', '2026-03-04 15:21:14'),
('146f01f8-1915-4070-b614-dd674e1d05a4', '8f9b4d09-f0ad-4581-9363-ad78da8446b9', 'delete_book', 0, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('152b5b06-30b2-42bc-8d7c-fae6263194b4', 'fdcfd51e-6188-4d8d-bec3-069ffb331a02', 'read_book', 1, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('15ad7b1d-d53b-4fc5-adf3-e2ca89deb262', '86194019-3723-4758-8716-3b7c6f5ab000', 'doc_join', 0, '2026-03-02 10:09:52', '2026-03-02 10:09:52'),
('16b940cc-cb85-4d10-9008-16b0e84e234c', '63f80453-a04b-43a8-8a3d-78721defb43c', 'doc_share', 1, '2026-03-17 14:29:33', '2026-03-17 14:29:33'),
('17a9f8c8-b894-4783-be47-5f0d65c36a78', 'f6886a73-ed14-433a-8696-2f030ede7236', 'doc_edit', 0, '2026-03-03 11:35:01', '2026-03-03 11:35:01'),
('194f39c3-def7-4224-a5ac-ffe70ea95d9a', '86194019-3723-4758-8716-3b7c6f5ab000', 'doc_delete', 0, '2026-03-02 10:09:52', '2026-03-02 10:09:52'),
('196a8086-6165-4906-8233-eff2121021a0', '71e84916-2164-4797-9625-a1f17778564f', 'read_book', 1, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('1a4dc960-14fc-49ad-8bdd-f62417acea2c', '53ace0e8-2300-40dd-9d05-4bee73023a13', 'doc_share', 1, '2026-03-04 15:21:14', '2026-03-04 15:21:14'),
('1b51a000-c5c0-482f-9538-179563dce8d5', '86194019-3723-4758-8716-3b7c6f5ab000', 'doc_create', 0, '2026-03-02 10:09:52', '2026-03-02 10:09:52'),
('1b63b09f-57b5-40e1-a394-4db012083506', '86194019-3723-4758-8716-3b7c6f5ab000', 'doc_edit', 0, '2026-03-02 10:09:52', '2026-03-02 10:09:52'),
('1b80dc54-fcc6-4f1b-ba9e-1d9b03446c4b', '37419883-832b-4b5c-ab18-c4a8e9997fad', 'doc_edit', 1, '2026-03-02 10:09:52', '2026-03-02 10:09:52'),
('1bcbf6d1-7be8-4942-8801-7495d73809f2', 'effaa58a-a9f1-488a-8482-9032a9629fc4', 'doc_join', 0, '2026-03-03 11:37:14', '2026-03-03 11:37:14'),
('1c40a5f4-a52a-4ea7-a6b5-3e0d467cb4c5', 'f6886a73-ed14-433a-8696-2f030ede7236', 'doc_join', 0, '2026-03-03 11:35:01', '2026-03-03 11:35:01'),
('1c43b5fa-52ec-4148-8e21-5dc60b5c29ff', '4d5e99b4-ce0c-41b7-8ce7-0b7b032ad0d3', 'create_book', 0, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('1c7897ed-b347-4051-b775-05002778cf58', 'a4132219-4759-4915-88c6-9ca34ca21b5a', 'doc_share', 1, '2026-03-03 11:40:07', '2026-03-03 11:40:07'),
('1df5bc8f-eaec-4747-9d82-929db240011e', 'f6886a73-ed14-433a-8696-2f030ede7236', 'doc_comment', 0, '2026-03-03 11:35:01', '2026-03-03 11:35:01'),
('1ff7b696-b9e2-4de6-a929-ea7875e02e79', 'a287025b-d1e9-47fb-aaf3-95672b353eb3', 'modify_book_setting', 1, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('21b1221f-22ed-4c17-855d-21d4272a3b03', '4a7485c5-f18f-4f93-9ce8-224d25c17445', 'doc_create', 0, '2026-03-03 11:40:07', '2026-03-03 11:40:07'),
('227fa682-6a2b-4178-bd08-60c18bfda39b', '53ace0e8-2300-40dd-9d05-4bee73023a13', 'doc_create', 0, '2026-03-04 15:21:14', '2026-03-04 15:21:14'),
('232ac692-2f39-4f9c-81cb-f2558afad6e5', '53ace0e8-2300-40dd-9d05-4bee73023a13', 'doc_edit', 1, '2026-03-04 15:21:14', '2026-03-04 15:21:14'),
('233b3c1a-fd69-4c2b-82ed-7403aea516bd', 'c14494ca-f2f3-46b5-9c18-9f0ac99f6109', 'doc_share', 0, '2026-02-26 18:27:52', '2026-02-26 18:27:52'),
('24a79e7a-ac59-4e7e-8471-c2af4c682892', '823b614c-1bf1-4f41-921d-ffae0bb31efc', 'doc_create', 0, '2026-03-03 11:49:24', '2026-03-03 11:49:24'),
('24bc473d-d0df-4c54-b0af-4993fbcb233d', '4a7485c5-f18f-4f93-9ce8-224d25c17445', 'doc_share', 0, '2026-03-03 11:40:07', '2026-03-03 11:40:07'),
('25102897-b7b7-4961-bc87-98fce8695f6e', '3c4e3ec2-2891-4622-808e-a3d422f6b1c0', 'doc_join', 1, '2026-03-02 10:34:03', '2026-03-02 10:34:03'),
('25e8d83f-cee2-497b-b7bf-c438f70ebcd0', '8f9b4d09-f0ad-4581-9363-ad78da8446b9', 'doc_join', 0, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('26696151-1992-421b-9f3d-7fa841f709c5', 'b054a80a-42fd-49a3-bd94-88d624010339', 'read_book', 1, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('2838edc7-902a-4b51-aa9e-edf99f868492', '1de5cf1f-b7c4-4ab1-b3a5-c0999848ea1c', 'doc_edit', 1, '2026-03-03 11:40:07', '2026-03-03 11:40:07'),
('28530c6d-6955-4569-aa16-2ace816aaea1', 'fdcfd51e-6188-4d8d-bec3-069ffb331a02', 'doc_share', 1, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('2991b3e6-d963-408b-9263-75c9c9842d11', '71e84916-2164-4797-9625-a1f17778564f', 'doc_edit', 0, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('29d1af9b-d58f-4dd9-a51a-08d7355bf8b7', 'fe3036ae-d59d-4b7f-aacd-0525a3a6655c', 'doc_delete', 0, '2026-03-17 15:48:38', '2026-03-17 15:48:38'),
('2a157a38-3a67-49ca-8283-6a510febca65', '1127af73-1db9-409b-a710-468582398a40', 'doc_delete', 0, '2026-03-02 10:34:03', '2026-03-02 10:34:03'),
('2e067aac-67dc-4f00-ae93-ae7b6c267d0b', '1e9cf2ee-1e0d-42a1-9ced-47018f31b91c', 'doc_delete', 0, '2026-02-26 18:27:52', '2026-02-26 18:27:52'),
('2fcbf20d-5425-4bfb-85b5-fa66cb9312b7', '4d5e99b4-ce0c-41b7-8ce7-0b7b032ad0d3', 'modify_book_permission', 0, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('2fd2246d-efe5-4ea9-a2f5-e6e1e7630736', 'effaa58a-a9f1-488a-8482-9032a9629fc4', 'doc_delete', 0, '2026-03-03 11:37:14', '2026-03-03 11:37:14'),
('2ffb0412-d5ac-42cb-81bc-ebc974713f58', '6db65823-074a-49f0-8173-2a5e68aeb8df', 'doc_edit', 1, '2026-03-03 11:35:01', '2026-03-03 11:35:01'),
('3002cff3-4923-4b0f-b600-dbc5a87cb5c6', 'a4132219-4759-4915-88c6-9ca34ca21b5a', 'doc_read', 0, '2026-03-03 11:40:07', '2026-03-03 11:40:07'),
('30ea5c02-b621-48f6-9a0c-16eff21f0fcd', 'fdcfd51e-6188-4d8d-bec3-069ffb331a02', 'doc_delete', 1, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('31312b22-410e-4856-ae24-9f63935181f2', 'f6886a73-ed14-433a-8696-2f030ede7236', 'doc_read', 0, '2026-03-03 11:35:01', '2026-03-03 11:35:01'),
('32567d12-a57f-415f-a8ec-aaea11759bae', '8a77b0f9-af46-475f-b220-c6498e9690b1', 'doc_comment', 1, '2026-03-03 11:35:01', '2026-03-03 11:35:01'),
('34552d40-d7c7-4f73-a55f-1c0eeb52dc02', '8f9b4d09-f0ad-4581-9363-ad78da8446b9', 'doc_create', 0, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('34ad786f-59f7-4a33-bd00-a7fc1c3e9ae2', '6db65823-074a-49f0-8173-2a5e68aeb8df', 'doc_share', 1, '2026-03-03 11:35:01', '2026-03-03 11:35:01'),
('34e1e850-9c06-4f37-9057-e3136344697a', 'b054a80a-42fd-49a3-bd94-88d624010339', 'doc_comment', 0, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('34fedd18-c38a-46a5-b19f-982487bbad64', '2efc8a38-3db1-4029-801d-a462e90f35bb', 'doc_join', 1, '2026-03-04 19:23:23', '2026-03-04 19:23:23'),
('3500964b-8322-4435-9cab-fc21edc4fff4', 'b054a80a-42fd-49a3-bd94-88d624010339', 'create_book', 0, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('3568cf1b-152f-42c6-ba8b-8f520377e916', 'b054a80a-42fd-49a3-bd94-88d624010339', 'doc_read', 0, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('367fa602-c2f6-43ac-bc7a-e1e3a44493d5', 'fdcfd51e-6188-4d8d-bec3-069ffb331a02', 'doc_comment', 1, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('375b1b52-ac7e-4d32-aa06-b32c81d510aa', 'fe3036ae-d59d-4b7f-aacd-0525a3a6655c', 'doc_create', 0, '2026-03-17 15:48:38', '2026-03-17 15:48:38'),
('3c202ef6-d0b2-44fa-93d5-ec1cff21250c', '823b614c-1bf1-4f41-921d-ffae0bb31efc', 'doc_delete', 0, '2026-03-03 11:49:24', '2026-03-03 11:49:24'),
('3cb508ce-32ae-44f3-9308-76a7a49b7e76', '6db65823-074a-49f0-8173-2a5e68aeb8df', 'doc_comment', 0, '2026-03-03 11:35:01', '2026-03-03 11:35:01'),
('3d277f49-4238-4489-bfd5-a97e215e4b57', '6d4173d4-9e9e-4531-88da-753782ebd7e2', 'doc_share', 1, '2026-02-26 18:27:52', '2026-02-26 18:27:52'),
('3f4b7f00-46c0-445a-a6ba-722c066f5838', '9ad1dee9-3819-411d-bb72-72da36aada94', 'doc_edit', 1, '2026-03-17 15:48:38', '2026-03-17 15:48:38'),
('3f4ce4ba-b885-4953-bb2d-1fadf3d8de79', 'f6886a73-ed14-433a-8696-2f030ede7236', 'doc_share', 0, '2026-03-03 11:35:01', '2026-03-03 11:35:01'),
('408b64ea-7311-43f2-90c7-22b3b8c9067f', '8a77b0f9-af46-475f-b220-c6498e9690b1', 'doc_read', 1, '2026-03-03 11:35:01', '2026-03-03 11:35:01'),
('40a65066-74ce-4538-a3cb-bdfe4b29072a', '6db65823-074a-49f0-8173-2a5e68aeb8df', 'doc_join', 0, '2026-03-03 11:35:01', '2026-03-03 11:35:01'),
('40ac9fb8-c480-4e91-bffc-b6acbdc17797', 'd63c0b3e-5db8-4d3e-b77d-2dd2a26654c1', 'doc_comment', 0, '2026-03-17 14:29:33', '2026-03-17 14:29:33'),
('40ba209d-ec5e-4a96-b9ee-8821eda7ac1a', '39de80d4-3ccd-4c56-9248-25391b6c84ee', 'doc_share', 1, '2026-03-03 11:49:24', '2026-03-03 11:49:24'),
('40ced1ec-3fc0-4947-9fee-943945c1d860', '6d4173d4-9e9e-4531-88da-753782ebd7e2', 'doc_comment', 1, '2026-02-26 18:27:52', '2026-02-26 18:27:52'),
('4129f0d1-3f0d-49f7-b3cf-802bbd1a40ec', 'effaa58a-a9f1-488a-8482-9032a9629fc4', 'doc_read', 0, '2026-03-03 11:37:14', '2026-03-03 11:37:14'),
('4200b36b-1486-4bac-b0b4-3f2fbb45901b', '4d5e99b4-ce0c-41b7-8ce7-0b7b032ad0d3', 'doc_share', 1, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('43f220e0-fcd9-40f3-aee9-d05d07b96624', '1e9cf2ee-1e0d-42a1-9ced-47018f31b91c', 'doc_comment', 0, '2026-02-26 18:27:52', '2026-02-26 18:27:52'),
('441fa6a0-125c-4140-bb03-d8345897c348', 'a287025b-d1e9-47fb-aaf3-95672b353eb3', 'export_book', 1, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('4629720d-163b-4f45-8af1-586b41012d0c', 'b054a80a-42fd-49a3-bd94-88d624010339', 'collect_book', 1, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('46ee83e3-0797-472b-88e1-ad410236f038', '71e84916-2164-4797-9625-a1f17778564f', 'modify_book_setting', 0, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('4753dc90-9a86-4af8-950c-3ed31df5316a', 'd5ca457f-19d8-4ddc-8765-0a64487bbaea', 'doc_create', 0, '2026-03-17 15:48:38', '2026-03-17 15:48:38'),
('491e4bcc-c129-4977-a7e2-9e3c1f8f8a57', 'b095315c-8231-40cf-ad63-82688ab49138', 'doc_share', 0, '2026-03-03 11:37:14', '2026-03-03 11:37:14'),
('4925ed42-272a-4bc9-b069-e333b20d2e07', '71e84916-2164-4797-9625-a1f17778564f', 'delete_book', 0, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('499ba842-e612-45f3-9ad1-0f7eae2548e6', '9ad1dee9-3819-411d-bb72-72da36aada94', 'doc_comment', 1, '2026-03-17 15:48:38', '2026-03-17 15:48:38'),
('4b69d065-7f3a-4056-a332-d798dde1283d', '642cd1b6-4c08-40fb-833c-a3a6039b3d55', 'doc_comment', 0, '2026-03-04 15:21:14', '2026-03-04 15:21:14'),
('4bffe319-3b6a-4be0-9187-81d645bdcd12', 'fe3036ae-d59d-4b7f-aacd-0525a3a6655c', 'doc_edit', 0, '2026-03-17 15:48:38', '2026-03-17 15:48:38'),
('4d1abb74-1cb2-4270-9d84-710a94f4c79c', '71e84916-2164-4797-9625-a1f17778564f', 'doc_join', 0, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('4fd13e76-3781-41f2-8d92-b154aca9a514', '1127af73-1db9-409b-a710-468582398a40', 'doc_comment', 0, '2026-03-02 10:34:03', '2026-03-02 10:34:03'),
('50c57bc8-2a72-4059-ac48-7e2f385d3634', '4d5e99b4-ce0c-41b7-8ce7-0b7b032ad0d3', 'doc_join', 0, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('50c8344f-37c3-432e-b8c3-c57d1f6da74a', '1f4eb7df-e207-476c-9337-06415ff41b6d', 'doc_delete', 1, '2026-03-03 11:49:24', '2026-03-03 11:49:24'),
('50c84f92-bf16-4e8a-a3ac-c20acd985739', '341c9007-9d36-4609-897d-578a4b9146ee', 'doc_comment', 1, '2026-03-03 11:37:14', '2026-03-03 11:37:14'),
('50d28ac7-ddfd-4ce3-8c1a-781bb5b32144', 'fbb40a2f-5bb4-438a-91be-098134ed0631', 'doc_read', 1, '2026-03-17 14:29:33', '2026-03-17 14:29:33'),
('514889bf-a52e-4f6e-99bd-24e436450db4', 'fdcfd51e-6188-4d8d-bec3-069ffb331a02', 'doc_edit', 1, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('51a4b4fb-b2a6-4d73-b8d6-ebb0f9841766', 'a287025b-d1e9-47fb-aaf3-95672b353eb3', 'doc_read', 1, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('52586930-0109-4d37-b6bf-447ef489644b', '87f30c16-b898-4335-a700-8439b7217e45', 'doc_join', 0, '2026-03-04 19:23:23', '2026-03-04 19:23:23'),
('526c58e1-c126-4822-a452-44a6f1b7aa09', 'fbb40a2f-5bb4-438a-91be-098134ed0631', 'doc_edit', 1, '2026-03-17 14:29:33', '2026-03-17 14:29:33'),
('52ce9daf-9fde-415d-bffc-7d1932d64dae', 'fdcfd51e-6188-4d8d-bec3-069ffb331a02', 'create_book', 1, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('531bcfe8-4c34-4722-8ad6-56acb7cb0d8d', '5a7dbae6-058f-4874-af49-540bf1a7de84', 'doc_join', 0, '2026-03-04 19:23:23', '2026-03-04 19:23:23'),
('5356a543-b18a-44e9-9a9b-36321d3f8eb3', '71e84916-2164-4797-9625-a1f17778564f', 'export_book', 0, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('5531bde4-0186-4f51-8b0b-03ec1753e426', 'e421e043-f5c7-43a1-9a34-8cefdd5ffa25', 'doc_read', 1, '2026-03-02 10:09:52', '2026-03-02 10:09:52'),
('570e26e0-f908-4961-b20b-3449c5ce8fae', 'b095315c-8231-40cf-ad63-82688ab49138', 'doc_edit', 0, '2026-03-03 11:37:14', '2026-03-03 11:37:14'),
('58222d47-8dfd-4c2a-a53c-5a504f55e2a9', '642cd1b6-4c08-40fb-833c-a3a6039b3d55', 'doc_delete', 0, '2026-03-04 15:21:14', '2026-03-04 15:21:14'),
('5a16ea71-f99d-444d-ac80-6e986c2fc771', '8f9b4d09-f0ad-4581-9363-ad78da8446b9', 'doc_share', 1, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('5adbb808-02a4-4cf8-a11c-78bbee556053', '823b614c-1bf1-4f41-921d-ffae0bb31efc', 'doc_read', 0, '2026-03-03 11:49:24', '2026-03-03 11:49:24'),
('5bc0c677-95e7-42f4-8626-f49068c846b7', '6d4173d4-9e9e-4531-88da-753782ebd7e2', 'doc_delete', 1, '2026-02-26 18:27:52', '2026-02-26 18:27:52'),
('5c0d3f97-e6a0-4216-9479-486c1c8dfcc5', 'fe3036ae-d59d-4b7f-aacd-0525a3a6655c', 'doc_comment', 0, '2026-03-17 15:48:38', '2026-03-17 15:48:38'),
('5c1e3e2e-8ee8-4630-9826-4406cf0f4517', 'e421e043-f5c7-43a1-9a34-8cefdd5ffa25', 'doc_join', 1, '2026-03-02 10:09:52', '2026-03-02 10:09:52'),
('5c3a50a7-a312-4e68-b751-6f0e743031a7', 'd5ca457f-19d8-4ddc-8765-0a64487bbaea', 'doc_edit', 1, '2026-03-17 15:48:38', '2026-03-17 15:48:38'),
('5cba2fbf-98fd-4c42-8656-221fd832b690', 'a287025b-d1e9-47fb-aaf3-95672b353eb3', 'modify_book_permission', 1, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('5ccc4a6e-961d-4874-83d4-dd94411c85fc', 'd5ca457f-19d8-4ddc-8765-0a64487bbaea', 'doc_comment', 0, '2026-03-17 15:48:38', '2026-03-17 15:48:38'),
('5cd32a70-54b2-4d50-ab98-9eef750926f4', '87f30c16-b898-4335-a700-8439b7217e45', 'doc_read', 0, '2026-03-04 19:23:23', '2026-03-04 19:23:23'),
('5d6692b9-d38f-4de4-899e-f5ca3141f89f', 'b054a80a-42fd-49a3-bd94-88d624010339', 'doc_share', 0, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('600dfca6-b91e-4225-94c5-bbdbe6566459', '1de5cf1f-b7c4-4ab1-b3a5-c0999848ea1c', 'doc_share', 1, '2026-03-03 11:40:07', '2026-03-03 11:40:07'),
('60c77226-0cee-4ccb-a46f-2d0084f6ad4d', 'fdcfd51e-6188-4d8d-bec3-069ffb331a02', 'create_book_collaborator', 1, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('60dbd776-7275-4c17-9e18-4862b8e6c1d5', 'b095315c-8231-40cf-ad63-82688ab49138', 'doc_comment', 0, '2026-03-03 11:37:14', '2026-03-03 11:37:14'),
('6257a51e-8d67-47d7-b41f-f916af6b0628', 'a4132219-4759-4915-88c6-9ca34ca21b5a', 'doc_join', 0, '2026-03-03 11:40:07', '2026-03-03 11:40:07'),
('63856c00-dd36-4b02-81ec-ee28b56691b5', '9ad1dee9-3819-411d-bb72-72da36aada94', 'doc_share', 1, '2026-03-17 15:48:38', '2026-03-17 15:48:38'),
('64593936-b6d7-406b-9d65-b0301f5675e2', 'a287025b-d1e9-47fb-aaf3-95672b353eb3', 'doc_delete', 1, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('6497a824-3af6-429e-8d3c-41e8cd330864', '1127af73-1db9-409b-a710-468582398a40', 'doc_join', 0, '2026-03-02 10:34:03', '2026-03-02 10:34:03'),
('64e3dc2d-5319-4342-b56b-ab047e5a279d', 'a4132219-4759-4915-88c6-9ca34ca21b5a', 'doc_edit', 1, '2026-03-03 11:40:07', '2026-03-03 11:40:07'),
('662dd2be-ef94-4437-986b-27f18c281bca', '63f80453-a04b-43a8-8a3d-78721defb43c', 'doc_create', 0, '2026-03-17 14:29:33', '2026-03-17 14:29:33'),
('665f3aa5-a3d1-47ec-b8e0-f34bb0b0a202', '4a7485c5-f18f-4f93-9ce8-224d25c17445', 'doc_read', 0, '2026-03-03 11:40:07', '2026-03-03 11:40:07'),
('6663c46b-47f6-42f4-a8c8-ab7b04e8a97b', '39de80d4-3ccd-4c56-9248-25391b6c84ee', 'doc_comment', 0, '2026-03-03 11:49:24', '2026-03-03 11:49:24'),
('669d9db6-2a78-4bc1-a13e-eed42be09b82', 'e59e51cd-8bb1-44e9-b4de-1bd2602baf0d', 'doc_create', 1, '2026-03-04 15:21:14', '2026-03-04 15:21:14'),
('66f0c1be-187a-44a1-867c-3646ba567065', 'fbb40a2f-5bb4-438a-91be-098134ed0631', 'doc_join', 1, '2026-03-17 14:29:33', '2026-03-17 14:29:33'),
('6750ba06-8fe9-4721-96a4-e38cf6b9a7ae', '1de5cf1f-b7c4-4ab1-b3a5-c0999848ea1c', 'doc_comment', 1, '2026-03-03 11:40:07', '2026-03-03 11:40:07'),
('68e2c074-3e9a-40d0-9975-03c7fa294dc6', '87f30c16-b898-4335-a700-8439b7217e45', 'doc_create', 0, '2026-03-04 19:23:23', '2026-03-04 19:23:23'),
('6923ec37-4e3b-4fd8-8318-0801f8e18fb8', '8f9b4d09-f0ad-4581-9363-ad78da8446b9', 'doc_delete', 0, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('6b1f85f4-2163-49b0-8e50-597f4b68ea15', '86194019-3723-4758-8716-3b7c6f5ab000', 'doc_share', 0, '2026-03-02 10:09:52', '2026-03-02 10:09:52'),
('6bad061b-e62e-4be0-b5ce-50078e4b3d77', 'fdcfd51e-6188-4d8d-bec3-069ffb331a02', 'collect_book', 1, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('6bc27977-5bbc-4c0d-838f-753079404929', 'b054a80a-42fd-49a3-bd94-88d624010339', 'doc_join', 0, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('6d293e02-d8d0-458a-a5cc-b706c1dd103a', 'a4132219-4759-4915-88c6-9ca34ca21b5a', 'doc_comment', 0, '2026-03-03 11:40:07', '2026-03-03 11:40:07'),
('6e03e8bb-379b-4276-a46b-dd4818268492', '87f30c16-b898-4335-a700-8439b7217e45', 'doc_edit', 1, '2026-03-04 19:23:23', '2026-03-04 19:23:23'),
('6ebf63b1-d1f5-48a4-93da-eb235dccf666', '2efc8a38-3db1-4029-801d-a462e90f35bb', 'doc_comment', 1, '2026-03-04 19:23:23', '2026-03-04 19:23:23'),
('6ee898e9-0132-4a67-bc0a-cd7cfb6cd610', 'fdcfd51e-6188-4d8d-bec3-069ffb331a02', 'modify_book_permission', 1, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('6f48894f-65b0-43f6-99d4-74f28aeba5b4', '2efc8a38-3db1-4029-801d-a462e90f35bb', 'doc_share', 1, '2026-03-04 19:23:23', '2026-03-04 19:23:23'),
('71fe1139-9ae6-4ca2-a2d2-e60bde27ebe6', '71e84916-2164-4797-9625-a1f17778564f', 'share_book', 0, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('723a9e11-bfa4-4c0d-8a9c-a653307bb195', '39de80d4-3ccd-4c56-9248-25391b6c84ee', 'doc_create', 0, '2026-03-03 11:49:24', '2026-03-03 11:49:24'),
('72e4c81a-b496-46a1-a897-686f6497e970', 'e59e51cd-8bb1-44e9-b4de-1bd2602baf0d', 'doc_edit', 1, '2026-03-04 15:21:14', '2026-03-04 15:21:14'),
('735a5ea0-128d-4436-ae19-5f8cc4ced8d2', 'fbb40a2f-5bb4-438a-91be-098134ed0631', 'doc_share', 1, '2026-03-17 14:29:33', '2026-03-17 14:29:33'),
('73df013d-eadb-4ae7-8d8b-bec39526f75f', 'effaa58a-a9f1-488a-8482-9032a9629fc4', 'doc_edit', 1, '2026-03-03 11:37:14', '2026-03-03 11:37:14'),
('74282535-fb96-407a-8bc7-69e8ebd2cd01', '6db65823-074a-49f0-8173-2a5e68aeb8df', 'doc_read', 0, '2026-03-03 11:35:01', '2026-03-03 11:35:01'),
('74626ea4-a1a7-40b0-a901-3d94798ef3f2', '6d4173d4-9e9e-4531-88da-753782ebd7e2', 'doc_edit', 1, '2026-02-26 18:27:52', '2026-02-26 18:27:52'),
('74f31e1f-02cd-4ac8-b198-9dc9d9f081ee', '8a77b0f9-af46-475f-b220-c6498e9690b1', 'doc_delete', 1, '2026-03-03 11:35:01', '2026-03-03 11:35:01'),
('75aa1273-2c0f-4845-a2d7-f83f06dadb29', 'c14494ca-f2f3-46b5-9c18-9f0ac99f6109', 'doc_create', 0, '2026-02-26 18:27:52', '2026-02-26 18:27:52'),
('76053e57-f8e1-4c7a-8f21-f4fc9b7895aa', '63f80453-a04b-43a8-8a3d-78721defb43c', 'doc_delete', 0, '2026-03-17 14:29:33', '2026-03-17 14:29:33'),
('7627998a-0167-4552-bf9a-c19f0c627c37', '1de5cf1f-b7c4-4ab1-b3a5-c0999848ea1c', 'doc_create', 1, '2026-03-03 11:40:07', '2026-03-03 11:40:07'),
('774a0c6a-ebd1-4ae3-ad28-708b5da2512c', '4d5e99b4-ce0c-41b7-8ce7-0b7b032ad0d3', 'read_book', 1, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('78225ad4-bbdf-45cf-a6cc-798274545ea1', '1127af73-1db9-409b-a710-468582398a40', 'doc_share', 0, '2026-03-02 10:34:03', '2026-03-02 10:34:03'),
('7ba670db-8b6b-4f19-8c5f-8ecb23765cc5', 'b054a80a-42fd-49a3-bd94-88d624010339', 'modify_book_setting', 0, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('7bf5ec73-e236-4ee2-b610-db310b4d9326', '642cd1b6-4c08-40fb-833c-a3a6039b3d55', 'doc_edit', 0, '2026-03-04 15:21:14', '2026-03-04 15:21:14'),
('7c89389d-2fd8-49ee-9999-527ce0353c76', '823b614c-1bf1-4f41-921d-ffae0bb31efc', 'doc_comment', 0, '2026-03-03 11:49:24', '2026-03-03 11:49:24'),
('7c975d77-b1ed-4720-97be-ee41f19a78d6', 'fdcfd51e-6188-4d8d-bec3-069ffb331a02', 'doc_read', 1, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('7ef44bde-1e8e-40f1-98c2-fa2ff8b8f0f8', 'fbb40a2f-5bb4-438a-91be-098134ed0631', 'doc_comment', 1, '2026-03-17 14:29:33', '2026-03-17 14:29:33'),
('7ff59eb3-7256-4203-94c7-db00c7e609d8', '4d5e99b4-ce0c-41b7-8ce7-0b7b032ad0d3', 'modify_book_setting', 0, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('805fb503-888e-47da-89f7-cc4b9e79b78f', 'b054a80a-42fd-49a3-bd94-88d624010339', 'doc_create', 0, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('80ab48de-38ce-4cc6-9715-ba7b111817fb', '2efc8a38-3db1-4029-801d-a462e90f35bb', 'doc_create', 1, '2026-03-04 19:23:23', '2026-03-04 19:23:23'),
('80c36dcf-bf0a-44e6-95ef-b100ac9c8121', 'c14494ca-f2f3-46b5-9c18-9f0ac99f6109', 'doc_read', 0, '2026-02-26 18:27:52', '2026-02-26 18:27:52'),
('827cd3c9-e523-49b2-bb8c-4ca6c2534d26', '1e9cf2ee-1e0d-42a1-9ced-47018f31b91c', 'doc_share', 1, '2026-02-26 18:27:52', '2026-02-26 18:27:52'),
('8386feb1-5be2-4ac1-bb5d-9597b6ebcdf5', '71e84916-2164-4797-9625-a1f17778564f', 'doc_share', 0, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('8512f58a-25f3-4eba-ac13-9e9db061a2fb', '1f4eb7df-e207-476c-9337-06415ff41b6d', 'doc_edit', 1, '2026-03-03 11:49:24', '2026-03-03 11:49:24'),
('85cd7009-385a-4d8f-90ee-ceb55afc3aac', '4d5e99b4-ce0c-41b7-8ce7-0b7b032ad0d3', 'delete_book', 0, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('8647114f-2eb6-497d-9b11-81e3d2cbed91', '9ad1dee9-3819-411d-bb72-72da36aada94', 'doc_create', 1, '2026-03-17 15:48:38', '2026-03-17 15:48:38'),
('86832903-064d-41cf-88c4-4f46254e9afe', 'effaa58a-a9f1-488a-8482-9032a9629fc4', 'doc_create', 0, '2026-03-03 11:37:14', '2026-03-03 11:37:14'),
('8728a693-9ad2-4716-8bc0-288662ee68e2', '1127af73-1db9-409b-a710-468582398a40', 'doc_edit', 0, '2026-03-02 10:34:03', '2026-03-02 10:34:03'),
('890be6bc-cf08-4cfd-b76c-401c06725c41', 'b054a80a-42fd-49a3-bd94-88d624010339', 'export_book', 0, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('89ddf72f-1cee-4a23-920a-6fa470690ff9', 'e59e51cd-8bb1-44e9-b4de-1bd2602baf0d', 'doc_join', 1, '2026-03-04 15:21:14', '2026-03-04 15:21:14'),
('8a940a2a-8b74-438c-acc8-c7a48e2ca1cf', '4d5e99b4-ce0c-41b7-8ce7-0b7b032ad0d3', 'doc_create', 0, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('8aa9d706-ea0e-4eeb-9d13-7b132a08ae37', 'a287025b-d1e9-47fb-aaf3-95672b353eb3', 'doc_edit', 1, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('8b97ba29-93df-489f-9ff3-d5e92839f4a6', '2efc8a38-3db1-4029-801d-a462e90f35bb', 'doc_edit', 1, '2026-03-04 19:23:23', '2026-03-04 19:23:23'),
('8c5cbe22-7fcf-4c9e-825e-7bedd685a483', '1de5cf1f-b7c4-4ab1-b3a5-c0999848ea1c', 'doc_delete', 1, '2026-03-03 11:40:07', '2026-03-03 11:40:07'),
('8cc5ec29-70df-4554-aeb9-0c37a4529649', '9ad1dee9-3819-411d-bb72-72da36aada94', 'doc_delete', 1, '2026-03-17 15:48:38', '2026-03-17 15:48:38'),
('8da1ed3a-83a7-4ea7-9a19-25ff6acd9a85', '642cd1b6-4c08-40fb-833c-a3a6039b3d55', 'doc_join', 0, '2026-03-04 15:21:14', '2026-03-04 15:21:14'),
('8e637073-1911-42d6-b52a-74fb2f7b9eb1', '8f9b4d09-f0ad-4581-9363-ad78da8446b9', 'doc_read', 0, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('8e968f83-d654-4654-823a-0362bb9ab748', '86194019-3723-4758-8716-3b7c6f5ab000', 'doc_comment', 0, '2026-03-02 10:09:52', '2026-03-02 10:09:52'),
('8eb8138f-37eb-47f4-9f03-2ab0f87c5481', 'fdcfd51e-6188-4d8d-bec3-069ffb331a02', 'export_book', 1, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('91375ade-57ce-4116-8ed4-38c11aa8aaae', '29981c27-113a-436f-9eed-a03f7fb9981d', 'doc_delete', 0, '2026-03-02 10:34:03', '2026-03-02 10:34:03'),
('9139e8b4-f217-49b3-91a7-93f36bdeb18f', '37419883-832b-4b5c-ab18-c4a8e9997fad', 'doc_join', 0, '2026-03-02 10:09:52', '2026-03-02 10:09:52'),
('915a4147-0032-4418-bdbe-f376b376f497', '63f80453-a04b-43a8-8a3d-78721defb43c', 'doc_join', 0, '2026-03-17 14:29:33', '2026-03-17 14:29:33'),
('92203457-1f72-4c63-8a3a-acac1fd34222', '1de5cf1f-b7c4-4ab1-b3a5-c0999848ea1c', 'doc_read', 1, '2026-03-03 11:40:07', '2026-03-03 11:40:07'),
('92365fe1-6721-4074-9e1a-bcbfaae399f2', 'b054a80a-42fd-49a3-bd94-88d624010339', 'doc_edit', 0, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('92652e71-cd73-4638-bec3-67a8289d913d', '1e9cf2ee-1e0d-42a1-9ced-47018f31b91c', 'doc_read', 0, '2026-02-26 18:27:52', '2026-02-26 18:27:52'),
('99f3e2ab-b842-428b-8ccb-fbcaad98c41b', '8a77b0f9-af46-475f-b220-c6498e9690b1', 'doc_edit', 1, '2026-03-03 11:35:01', '2026-03-03 11:35:01'),
('9a09dd8a-c634-4108-80de-635df3d4a242', '8f9b4d09-f0ad-4581-9363-ad78da8446b9', 'create_book', 0, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('9b21d1f8-b7d1-4f48-8cfb-fa734a84bfb7', 'fdcfd51e-6188-4d8d-bec3-069ffb331a02', 'share_book', 1, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('9d15e846-5dd2-437c-bccd-481590760c16', 'e421e043-f5c7-43a1-9a34-8cefdd5ffa25', 'doc_edit', 1, '2026-03-02 10:09:52', '2026-03-02 10:09:52'),
('9e2febae-8306-4e6d-8192-4c386ff1e288', 'c14494ca-f2f3-46b5-9c18-9f0ac99f6109', 'doc_join', 0, '2026-02-26 18:27:52', '2026-02-26 18:27:52'),
('9e4cc675-9ff9-46d3-924d-94034751c7e6', '4a7485c5-f18f-4f93-9ce8-224d25c17445', 'doc_join', 0, '2026-03-03 11:40:07', '2026-03-03 11:40:07'),
('9ee536d0-556b-489a-81dc-7d61e81c7cee', '87f30c16-b898-4335-a700-8439b7217e45', 'doc_share', 1, '2026-03-04 19:23:23', '2026-03-04 19:23:23'),
('a0d59f8a-1957-47d3-9391-53f923bdb464', 'a287025b-d1e9-47fb-aaf3-95672b353eb3', 'collect_book', 1, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('a209ad5d-a6e0-423c-812f-f8592de49ec2', '341c9007-9d36-4609-897d-578a4b9146ee', 'doc_share', 1, '2026-03-03 11:37:14', '2026-03-03 11:37:14'),
('a2329d97-6ac3-4dca-a9da-1e005d04fedc', 'a287025b-d1e9-47fb-aaf3-95672b353eb3', 'read_book', 1, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('a5809e6b-987c-4d77-b428-cbe2a1799b08', '2efc8a38-3db1-4029-801d-a462e90f35bb', 'doc_read', 1, '2026-03-04 19:23:23', '2026-03-04 19:23:23'),
('a58629d1-aae7-4698-bbc8-55cd12c40bf3', 'e421e043-f5c7-43a1-9a34-8cefdd5ffa25', 'doc_comment', 1, '2026-03-02 10:09:52', '2026-03-02 10:09:52'),
('a60f2be8-d209-44c1-80ea-8912a94b88db', '53ace0e8-2300-40dd-9d05-4bee73023a13', 'doc_read', 0, '2026-03-04 15:21:14', '2026-03-04 15:21:14'),
('a6319444-f71c-438a-83f5-419fc43c2f0d', '5a7dbae6-058f-4874-af49-540bf1a7de84', 'doc_create', 0, '2026-03-04 19:23:23', '2026-03-04 19:23:23'),
('a6c64daf-f9b9-4c06-bf06-522eb42c1828', 'a287025b-d1e9-47fb-aaf3-95672b353eb3', 'doc_create', 1, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('a71d4b53-b693-46b4-a60b-402fd048fc73', '4d5e99b4-ce0c-41b7-8ce7-0b7b032ad0d3', 'export_book', 1, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('a8a8faab-6955-44cc-84ea-a0e33aac05be', '37419883-832b-4b5c-ab18-c4a8e9997fad', 'doc_read', 0, '2026-03-02 10:09:52', '2026-03-02 10:09:52'),
('a8ead8e2-aa76-4439-83ff-1a947c6a83f7', '6d4173d4-9e9e-4531-88da-753782ebd7e2', 'doc_join', 1, '2026-02-26 18:27:52', '2026-02-26 18:27:52'),
('a9d13e32-1f55-498e-9d5b-10f6b22551f8', '3c4e3ec2-2891-4622-808e-a3d422f6b1c0', 'doc_create', 1, '2026-03-02 10:34:03', '2026-03-02 10:34:03'),
('ab546bb3-ca30-4eb4-bd2c-9fc1f85f1ab7', 'd5ca457f-19d8-4ddc-8765-0a64487bbaea', 'doc_delete', 0, '2026-03-17 15:48:38', '2026-03-17 15:48:38'),
('ab96732d-4800-4594-ae32-6c9c4731e7a5', '1127af73-1db9-409b-a710-468582398a40', 'doc_read', 0, '2026-03-02 10:34:03', '2026-03-02 10:34:03'),
('adddf5e6-2ac1-4e95-8ec9-1a6bb905608e', '71e84916-2164-4797-9625-a1f17778564f', 'doc_comment', 0, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('aebdeb0b-e3dc-4dcd-9a4f-87f824f2a221', '9ad1dee9-3819-411d-bb72-72da36aada94', 'doc_read', 1, '2026-03-17 15:48:38', '2026-03-17 15:48:38'),
('afde1b9f-ecd9-4648-a59e-89a9641b7d48', 'effaa58a-a9f1-488a-8482-9032a9629fc4', 'doc_share', 1, '2026-03-03 11:37:14', '2026-03-03 11:37:14'),
('b1fa92a1-274f-48f1-99c4-75cc994d3d6c', '1f4eb7df-e207-476c-9337-06415ff41b6d', 'doc_read', 1, '2026-03-03 11:49:24', '2026-03-03 11:49:24'),
('b2de4046-2c3e-4a5f-b6f7-fad3d0e87945', '1127af73-1db9-409b-a710-468582398a40', 'doc_create', 0, '2026-03-02 10:34:03', '2026-03-02 10:34:03'),
('b382b49c-b8c4-4fcd-8c4d-35dea88366a5', '4d5e99b4-ce0c-41b7-8ce7-0b7b032ad0d3', 'doc_delete', 0, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('b3e40507-c4b0-4cfe-9c76-8d590df0102a', 'd5ca457f-19d8-4ddc-8765-0a64487bbaea', 'doc_join', 0, '2026-03-17 15:48:38', '2026-03-17 15:48:38'),
('b460ca3a-33b7-43df-b3f3-7e85061bad0f', '53ace0e8-2300-40dd-9d05-4bee73023a13', 'doc_delete', 0, '2026-03-04 15:21:14', '2026-03-04 15:21:14'),
('b493fd23-cef7-4bf9-849b-33ae70950253', 'e421e043-f5c7-43a1-9a34-8cefdd5ffa25', 'doc_create', 1, '2026-03-02 10:09:52', '2026-03-02 10:09:52'),
('b51471c7-891f-4298-bd37-5bd7c320b7d8', 'd5ca457f-19d8-4ddc-8765-0a64487bbaea', 'doc_read', 0, '2026-03-17 15:48:38', '2026-03-17 15:48:38'),
('b543ec70-05bb-404f-af22-3e3eb6e1661a', '29981c27-113a-436f-9eed-a03f7fb9981d', 'doc_create', 0, '2026-03-02 10:34:03', '2026-03-02 10:34:03'),
('b55fd17c-cf67-4851-a89a-89f1c1d829ea', 'a287025b-d1e9-47fb-aaf3-95672b353eb3', 'share_book', 1, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('b654784a-d419-41bb-ad24-b57ca78cab32', '71e84916-2164-4797-9625-a1f17778564f', 'doc_create', 0, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('b6f6d30c-c0cb-4876-b07a-acd7a6475a43', '71e84916-2164-4797-9625-a1f17778564f', 'doc_read', 0, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('b6f88d7b-a073-4542-9d17-3afdc8f2a69e', '39de80d4-3ccd-4c56-9248-25391b6c84ee', 'doc_join', 0, '2026-03-03 11:49:24', '2026-03-03 11:49:24'),
('b8c15a10-2a29-4a5e-a088-beb746319be8', '341c9007-9d36-4609-897d-578a4b9146ee', 'doc_read', 1, '2026-03-03 11:37:14', '2026-03-03 11:37:14'),
('b8ef6353-5568-4708-ae39-a99c5ae2eb1a', 'c14494ca-f2f3-46b5-9c18-9f0ac99f6109', 'doc_comment', 0, '2026-02-26 18:27:52', '2026-02-26 18:27:52'),
('baea3c5e-d40a-497f-84c7-94a4437c196d', '341c9007-9d36-4609-897d-578a4b9146ee', 'doc_create', 1, '2026-03-03 11:37:14', '2026-03-03 11:37:14'),
('bb203997-493a-4fb1-b77a-de83b4d8e49d', '4a7485c5-f18f-4f93-9ce8-224d25c17445', 'doc_comment', 0, '2026-03-03 11:40:07', '2026-03-03 11:40:07'),
('bb20d109-b356-439b-a5cc-58c8ce0ab8bd', '3c4e3ec2-2891-4622-808e-a3d422f6b1c0', 'doc_share', 1, '2026-03-02 10:34:03', '2026-03-02 10:34:03'),
('bb913424-594d-4ee2-9fea-eb6e7716c454', '5a7dbae6-058f-4874-af49-540bf1a7de84', 'doc_comment', 0, '2026-03-04 19:23:23', '2026-03-04 19:23:23'),
('bd3dc753-d752-4ada-a7d0-ee77de49c682', 'a287025b-d1e9-47fb-aaf3-95672b353eb3', 'create_book_collaborator', 1, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('bd543fb7-cf33-4306-8c81-fe91cc065e68', '37419883-832b-4b5c-ab18-c4a8e9997fad', 'doc_create', 0, '2026-03-02 10:09:52', '2026-03-02 10:09:52'),
('bd9d4ab8-4140-45d9-8ba1-95fb6424704e', '71e84916-2164-4797-9625-a1f17778564f', 'create_book_collaborator', 0, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('be6d1d41-90a2-4487-b941-878505c99907', 'b054a80a-42fd-49a3-bd94-88d624010339', 'share_book', 0, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('be96da0c-ba5b-42bf-9153-172eac21131b', 'd63c0b3e-5db8-4d3e-b77d-2dd2a26654c1', 'doc_share', 0, '2026-03-17 14:29:33', '2026-03-17 14:29:33'),
('bf53153d-6942-47c6-85f6-2ec9bfb47758', '53ace0e8-2300-40dd-9d05-4bee73023a13', 'doc_comment', 0, '2026-03-04 15:21:14', '2026-03-04 15:21:14'),
('bf5ce500-2866-4748-888b-a37f7f0e44dc', '8a77b0f9-af46-475f-b220-c6498e9690b1', 'doc_join', 1, '2026-03-03 11:35:01', '2026-03-03 11:35:01'),
('bfacc29e-2360-4dcd-8ada-7ce477a46894', '1de5cf1f-b7c4-4ab1-b3a5-c0999848ea1c', 'doc_join', 1, '2026-03-03 11:40:07', '2026-03-03 11:40:07'),
('bffe267c-1d1f-4718-ab3d-4e5388cda1fc', '4a7485c5-f18f-4f93-9ce8-224d25c17445', 'doc_delete', 0, '2026-03-03 11:40:07', '2026-03-03 11:40:07'),
('c004685e-cd17-4509-8835-c2de6c3ae74b', 'fbb40a2f-5bb4-438a-91be-098134ed0631', 'doc_delete', 1, '2026-03-17 14:29:33', '2026-03-17 14:29:33'),
('c11eb1e7-95fd-40c9-b2e4-585956c460f0', '341c9007-9d36-4609-897d-578a4b9146ee', 'doc_edit', 1, '2026-03-03 11:37:14', '2026-03-03 11:37:14'),
('c2e32fa0-5214-400d-afd8-d2993447bc44', 'd63c0b3e-5db8-4d3e-b77d-2dd2a26654c1', 'doc_delete', 0, '2026-03-17 14:29:33', '2026-03-17 14:29:33'),
('c30d412d-1f09-4e28-a8e8-12629c3fdd24', '29981c27-113a-436f-9eed-a03f7fb9981d', 'doc_share', 1, '2026-03-02 10:34:03', '2026-03-02 10:34:03'),
('c317ab06-db39-4a30-bdab-b0e73c39ca85', '9ad1dee9-3819-411d-bb72-72da36aada94', 'doc_join', 1, '2026-03-17 15:48:38', '2026-03-17 15:48:38'),
('c4579352-db44-4862-80d6-bcfa7d9f3c5e', '4d5e99b4-ce0c-41b7-8ce7-0b7b032ad0d3', 'collect_book', 1, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('c480fc8e-7f18-4b93-b43b-5cee3b175b69', 'b095315c-8231-40cf-ad63-82688ab49138', 'doc_delete', 0, '2026-03-03 11:37:14', '2026-03-03 11:37:14'),
('c4b39163-26ba-404f-918d-f2f1e80f969e', '341c9007-9d36-4609-897d-578a4b9146ee', 'doc_delete', 1, '2026-03-03 11:37:14', '2026-03-03 11:37:14'),
('c4b53793-457d-4a3e-bb78-a5eb1d35e36c', 'd63c0b3e-5db8-4d3e-b77d-2dd2a26654c1', 'doc_edit', 0, '2026-03-17 14:29:33', '2026-03-17 14:29:33'),
('c5460d5d-b810-46d8-85c6-312b86013924', '8f9b4d09-f0ad-4581-9363-ad78da8446b9', 'doc_comment', 0, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('c5517bfd-5133-4d58-b5b7-bd956d616b0a', '1f4eb7df-e207-476c-9337-06415ff41b6d', 'doc_join', 1, '2026-03-03 11:49:24', '2026-03-03 11:49:24'),
('c644a9e6-1dfd-4593-b619-65e2fbdfee9d', '39de80d4-3ccd-4c56-9248-25391b6c84ee', 'doc_edit', 1, '2026-03-03 11:49:24', '2026-03-03 11:49:24'),
('c6cc7007-2367-4bfc-9c80-0e7ba32a3e60', '71e84916-2164-4797-9625-a1f17778564f', 'doc_delete', 0, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('c7e3a953-230d-4070-bee2-d6f75a62fb5f', 'fdcfd51e-6188-4d8d-bec3-069ffb331a02', 'delete_book', 1, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('c7fb91e9-b575-49c3-9b56-06a2bde7891d', '4d5e99b4-ce0c-41b7-8ce7-0b7b032ad0d3', 'doc_comment', 0, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('c8521457-4842-44e4-b2fc-72f2c73339b4', 'e59e51cd-8bb1-44e9-b4de-1bd2602baf0d', 'doc_share', 1, '2026-03-04 15:21:14', '2026-03-04 15:21:14'),
('ca90ce02-1c1c-4db7-9dbb-843e2ad66dee', '1e9cf2ee-1e0d-42a1-9ced-47018f31b91c', 'doc_edit', 1, '2026-02-26 18:27:52', '2026-02-26 18:27:52'),
('cc254a2b-3de8-462f-bfd6-53c2d13757d2', 'b054a80a-42fd-49a3-bd94-88d624010339', 'create_book_collaborator', 0, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('cc4c91d4-4eea-4ec7-90a0-8c034ac64543', '642cd1b6-4c08-40fb-833c-a3a6039b3d55', 'doc_read', 0, '2026-03-04 15:21:14', '2026-03-04 15:21:14'),
('ccb884fd-6b3c-4d26-9df0-1283a9ae84ed', 'b054a80a-42fd-49a3-bd94-88d624010339', 'modify_book_permission', 0, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('ced3fece-9f4c-4714-9d5d-169394f277b2', 'a287025b-d1e9-47fb-aaf3-95672b353eb3', 'doc_share', 1, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('cfe7a941-8317-44bc-a2be-4283bbc20d6b', 'f6886a73-ed14-433a-8696-2f030ede7236', 'doc_delete', 0, '2026-03-03 11:35:01', '2026-03-03 11:35:01'),
('d1419a5a-12e9-45cb-be40-57d7a6f86888', 'f6886a73-ed14-433a-8696-2f030ede7236', 'doc_create', 0, '2026-03-03 11:35:01', '2026-03-03 11:35:01'),
('d14a4d9f-4a86-4b4e-ac29-e6984a93612b', '86194019-3723-4758-8716-3b7c6f5ab000', 'doc_read', 0, '2026-03-02 10:09:52', '2026-03-02 10:09:52'),
('d2528ea1-3a38-457f-b2b5-f521efe8a7a1', '37419883-832b-4b5c-ab18-c4a8e9997fad', 'doc_comment', 0, '2026-03-02 10:09:52', '2026-03-02 10:09:52'),
('d26229c9-e943-460a-96a2-56dc5e15acd7', 'b095315c-8231-40cf-ad63-82688ab49138', 'doc_read', 0, '2026-03-03 11:37:14', '2026-03-03 11:37:14'),
('d27b5a4a-cab5-4e1f-bfec-3e816c3e388d', '5a7dbae6-058f-4874-af49-540bf1a7de84', 'doc_share', 0, '2026-03-04 19:23:23', '2026-03-04 19:23:23'),
('d2c00444-5597-4531-821e-2ef85c06f3cf', '1f4eb7df-e207-476c-9337-06415ff41b6d', 'doc_comment', 1, '2026-03-03 11:49:24', '2026-03-03 11:49:24'),
('d2f63524-c4bf-43bf-8cfb-f616fdcee9f6', '6d4173d4-9e9e-4531-88da-753782ebd7e2', 'doc_read', 1, '2026-02-26 18:27:52', '2026-02-26 18:27:52'),
('d4117c39-2f88-403f-b40b-a9d9becbcf49', '3c4e3ec2-2891-4622-808e-a3d422f6b1c0', 'doc_delete', 1, '2026-03-02 10:34:03', '2026-03-02 10:34:03'),
('d4f0af9c-bc45-4b7c-9153-7c7a929d2d1f', '87f30c16-b898-4335-a700-8439b7217e45', 'doc_delete', 0, '2026-03-04 19:23:23', '2026-03-04 19:23:23'),
('d5ef7442-e6ca-46df-9477-e2904cb761d3', '8a77b0f9-af46-475f-b220-c6498e9690b1', 'doc_create', 1, '2026-03-03 11:35:01', '2026-03-03 11:35:01'),
('d785154b-00d5-4ae9-8b0c-18a02614daec', '71e84916-2164-4797-9625-a1f17778564f', 'create_book', 0, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('d818cc71-ead5-4a88-bb1f-f9ebfc8cdfce', 'fe3036ae-d59d-4b7f-aacd-0525a3a6655c', 'doc_join', 0, '2026-03-17 15:48:38', '2026-03-17 15:48:38'),
('d84abd1d-0b93-4dde-8716-faaca174f85b', '8f9b4d09-f0ad-4581-9363-ad78da8446b9', 'modify_book_permission', 0, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('d8529c22-6de6-44f9-8bbc-81422fa98bbd', '6db65823-074a-49f0-8173-2a5e68aeb8df', 'doc_create', 0, '2026-03-03 11:35:01', '2026-03-03 11:35:01'),
('d8e48588-f7c1-4401-852d-b22c38aaa1da', 'fe3036ae-d59d-4b7f-aacd-0525a3a6655c', 'doc_share', 0, '2026-03-17 15:48:38', '2026-03-17 15:48:38'),
('d8ead796-9b24-4cf4-87db-5ce44a711f4d', 'c14494ca-f2f3-46b5-9c18-9f0ac99f6109', 'doc_edit', 0, '2026-02-26 18:27:52', '2026-02-26 18:27:52'),
('d97f7295-1e38-466f-ba9c-6c65bfeabd12', 'fdcfd51e-6188-4d8d-bec3-069ffb331a02', 'doc_join', 1, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('dab7334b-aab3-4415-ad41-009a01cc8d5c', 'fdcfd51e-6188-4d8d-bec3-069ffb331a02', 'doc_create', 1, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('db1ad34e-59cc-4deb-8f20-f0f8f025798f', 'effaa58a-a9f1-488a-8482-9032a9629fc4', 'doc_comment', 0, '2026-03-03 11:37:14', '2026-03-03 11:37:14'),
('db4ec8fa-56c4-42fd-998f-6a2ad05a429e', '39de80d4-3ccd-4c56-9248-25391b6c84ee', 'doc_delete', 0, '2026-03-03 11:49:24', '2026-03-03 11:49:24'),
('dc857934-39cc-4aa4-ae69-391fb2f7408d', '823b614c-1bf1-4f41-921d-ffae0bb31efc', 'doc_join', 0, '2026-03-03 11:49:24', '2026-03-03 11:49:24'),
('dd2b9530-725c-420b-8ae3-b21a4dbc5942', '5a7dbae6-058f-4874-af49-540bf1a7de84', 'doc_read', 0, '2026-03-04 19:23:23', '2026-03-04 19:23:23'),
('dd3b1c5c-3df9-4868-9e2f-67686ffbb67c', 'a4132219-4759-4915-88c6-9ca34ca21b5a', 'doc_delete', 0, '2026-03-03 11:40:07', '2026-03-03 11:40:07'),
('ddb57d5c-dedf-46b7-a858-9610e9a8cdb7', '8f9b4d09-f0ad-4581-9363-ad78da8446b9', 'share_book', 1, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('ddbd4284-72e1-4b41-ad14-cae711b0143a', '37419883-832b-4b5c-ab18-c4a8e9997fad', 'doc_share', 1, '2026-03-02 10:09:52', '2026-03-02 10:09:52'),
('de7803be-c535-4286-b582-452e84d8d33a', 'a287025b-d1e9-47fb-aaf3-95672b353eb3', 'doc_comment', 1, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('dec1d9d7-b7dd-4d3c-a6f0-924408ee9ef6', 'b054a80a-42fd-49a3-bd94-88d624010339', 'doc_delete', 0, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('e079d8ca-2b8f-45c9-84e0-4c9a027f5974', 'e59e51cd-8bb1-44e9-b4de-1bd2602baf0d', 'doc_comment', 1, '2026-03-04 15:21:14', '2026-03-04 15:21:14'),
('e0b082c0-c10a-4e60-8326-6011695a4d00', 'd63c0b3e-5db8-4d3e-b77d-2dd2a26654c1', 'doc_join', 0, '2026-03-17 14:29:33', '2026-03-17 14:29:33'),
('e1b0b943-d8a0-40bc-a4ea-eb2cc1d6d0a4', 'd63c0b3e-5db8-4d3e-b77d-2dd2a26654c1', 'doc_read', 0, '2026-03-17 14:29:33', '2026-03-17 14:29:33'),
('e1bf0dbe-7ebe-4023-8631-cd78e59d3e7a', '341c9007-9d36-4609-897d-578a4b9146ee', 'doc_join', 1, '2026-03-03 11:37:14', '2026-03-03 11:37:14'),
('e3bae4a4-9d9a-497f-a816-35f1069a461f', '4d5e99b4-ce0c-41b7-8ce7-0b7b032ad0d3', 'share_book', 1, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('e6096de0-56b9-4612-afa6-32f5aa8bf7b7', 'd5ca457f-19d8-4ddc-8765-0a64487bbaea', 'doc_share', 1, '2026-03-17 15:48:38', '2026-03-17 15:48:38'),
('e61f861a-8578-4323-8985-7f07ca950b10', '5a7dbae6-058f-4874-af49-540bf1a7de84', 'doc_delete', 0, '2026-03-04 19:23:23', '2026-03-04 19:23:23'),
('e68f8f97-c91b-46ef-8af5-4a58d0db2653', '1e9cf2ee-1e0d-42a1-9ced-47018f31b91c', 'doc_create', 0, '2026-02-26 18:27:52', '2026-02-26 18:27:52'),
('e6d08e57-20f6-42ef-ad81-3e4771ba316f', '63f80453-a04b-43a8-8a3d-78721defb43c', 'doc_read', 0, '2026-03-17 14:29:33', '2026-03-17 14:29:33'),
('e898c3f4-656b-47a0-a6ed-6d1c2c8d39b7', '8f9b4d09-f0ad-4581-9363-ad78da8446b9', 'collect_book', 1, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('e8de9ebc-4f4a-4159-be00-c843419afbff', 'e421e043-f5c7-43a1-9a34-8cefdd5ffa25', 'doc_share', 1, '2026-03-02 10:09:52', '2026-03-02 10:09:52'),
('e994030c-ea03-40f7-8b40-e199c9d54cd2', 'fdcfd51e-6188-4d8d-bec3-069ffb331a02', 'modify_book_setting', 1, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('ea6469bf-4331-4d3c-8070-435021ad260d', 'b095315c-8231-40cf-ad63-82688ab49138', 'doc_join', 0, '2026-03-03 11:37:14', '2026-03-03 11:37:14'),
('eaabc73e-0ff5-44c5-8bc3-2c8070ab0229', 'a287025b-d1e9-47fb-aaf3-95672b353eb3', 'doc_join', 1, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('eaeae726-65d2-4fa4-94b6-49bf29cf4c21', '8f9b4d09-f0ad-4581-9363-ad78da8446b9', 'modify_book_setting', 0, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('ebd08abb-277e-4b5e-adf3-eb3a39788174', '63f80453-a04b-43a8-8a3d-78721defb43c', 'doc_edit', 1, '2026-03-17 14:29:33', '2026-03-17 14:29:33'),
('ecfa4153-a85c-4fb4-a2b9-c21d10924d9a', '4d5e99b4-ce0c-41b7-8ce7-0b7b032ad0d3', 'create_book_collaborator', 0, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('ee6359a1-618f-4fda-87b3-21ca3838e3cc', 'e421e043-f5c7-43a1-9a34-8cefdd5ffa25', 'doc_delete', 1, '2026-03-02 10:09:52', '2026-03-02 10:09:52'),
('ee83fcf5-eef3-4e88-a9a7-37f4d3618b80', '29981c27-113a-436f-9eed-a03f7fb9981d', 'doc_edit', 1, '2026-03-02 10:34:03', '2026-03-02 10:34:03'),
('ee8c5ad5-449c-4741-8003-6e321631d560', '53ace0e8-2300-40dd-9d05-4bee73023a13', 'doc_join', 0, '2026-03-04 15:21:14', '2026-03-04 15:21:14'),
('ef0f8a81-4dfb-4077-8cbc-d489f1bb2ba4', 'e59e51cd-8bb1-44e9-b4de-1bd2602baf0d', 'doc_delete', 1, '2026-03-04 15:21:14', '2026-03-04 15:21:14'),
('ef15f4c0-b9b9-4e2a-b51c-22caf63aba7d', '29981c27-113a-436f-9eed-a03f7fb9981d', 'doc_join', 0, '2026-03-02 10:34:03', '2026-03-02 10:34:03'),
('ef346d68-debf-4e2f-a654-6449b127d09b', '39de80d4-3ccd-4c56-9248-25391b6c84ee', 'doc_read', 0, '2026-03-03 11:49:24', '2026-03-03 11:49:24'),
('f0d04eee-2e99-4bf1-b747-918f99005e12', '823b614c-1bf1-4f41-921d-ffae0bb31efc', 'doc_share', 0, '2026-03-03 11:49:24', '2026-03-03 11:49:24'),
('f0db3597-cd37-43d1-a800-e7371f5db78e', 'a287025b-d1e9-47fb-aaf3-95672b353eb3', 'delete_book', 1, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('f29d28ee-7881-42fb-a910-85d245ab293a', '6db65823-074a-49f0-8173-2a5e68aeb8df', 'doc_delete', 0, '2026-03-03 11:35:01', '2026-03-03 11:35:01'),
('f2a6e357-81d1-420e-a06d-fccfc64ab810', '4a7485c5-f18f-4f93-9ce8-224d25c17445', 'doc_edit', 0, '2026-03-03 11:40:07', '2026-03-03 11:40:07'),
('f2a70ce1-2bd7-4ce0-8e2b-17085c6f3420', '6d4173d4-9e9e-4531-88da-753782ebd7e2', 'doc_create', 1, '2026-02-26 18:27:52', '2026-02-26 18:27:52'),
('f2a8835f-a548-4cb8-9bed-73dd48fe0603', '1f4eb7df-e207-476c-9337-06415ff41b6d', 'doc_create', 1, '2026-03-03 11:49:24', '2026-03-03 11:49:24'),
('f305244b-571d-4a31-bd21-25667e26dda1', 'e59e51cd-8bb1-44e9-b4de-1bd2602baf0d', 'doc_read', 1, '2026-03-04 15:21:14', '2026-03-04 15:21:14'),
('f30b3ab7-3c57-4fad-b810-77af2157e1f0', '8f9b4d09-f0ad-4581-9363-ad78da8446b9', 'export_book', 1, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('f33a889d-2713-4f9f-8209-d9e45e1fc407', '8f9b4d09-f0ad-4581-9363-ad78da8446b9', 'doc_edit', 1, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('f5089763-3e92-48a8-b0a8-7492e70517fb', 'fbb40a2f-5bb4-438a-91be-098134ed0631', 'doc_create', 1, '2026-03-17 14:29:33', '2026-03-17 14:29:33'),
('f5636103-80a3-49c5-822d-3d80ae185751', 'a4132219-4759-4915-88c6-9ca34ca21b5a', 'doc_create', 0, '2026-03-03 11:40:07', '2026-03-03 11:40:07'),
('f621ac4d-ffb5-4bdf-9a3a-138156446b28', 'b054a80a-42fd-49a3-bd94-88d624010339', 'delete_book', 0, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('f7940bf6-1934-42e9-a8c0-3b2831ed0029', '8f9b4d09-f0ad-4581-9363-ad78da8446b9', 'read_book', 1, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('f7c0aa4f-0f4d-4cc8-b295-24ad54397172', 'b095315c-8231-40cf-ad63-82688ab49138', 'doc_create', 0, '2026-03-03 11:37:14', '2026-03-03 11:37:14'),
('f7e0594d-b6f8-4527-bbf4-1a44c12308a8', '642cd1b6-4c08-40fb-833c-a3a6039b3d55', 'doc_create', 0, '2026-03-04 15:21:14', '2026-03-04 15:21:14'),
('f7ea4d0a-24bb-44f6-83a6-c4ae16d9f78c', '1f4eb7df-e207-476c-9337-06415ff41b6d', 'doc_share', 1, '2026-03-03 11:49:24', '2026-03-03 11:49:24'),
('f848b0c2-8468-4edb-ab53-94c8d7b92261', '87f30c16-b898-4335-a700-8439b7217e45', 'doc_comment', 0, '2026-03-04 19:23:23', '2026-03-04 19:23:23'),
('f8d895b4-dcde-4830-8e04-58af1b90a045', 'fe3036ae-d59d-4b7f-aacd-0525a3a6655c', 'doc_read', 0, '2026-03-17 15:48:38', '2026-03-17 15:48:38'),
('fa264dc8-60d0-44c9-b173-46bedfd015aa', '4d5e99b4-ce0c-41b7-8ce7-0b7b032ad0d3', 'doc_read', 0, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('fb42fdc8-9fba-4775-a0ae-fe796f68a3e0', '71e84916-2164-4797-9625-a1f17778564f', 'collect_book', 1, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('fd5859f1-4339-4562-9166-634cf19cbbce', '8f9b4d09-f0ad-4581-9363-ad78da8446b9', 'create_book_collaborator', 0, '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('fdba29a6-14d3-45bd-af2b-d22ad08cdbb5', 'a287025b-d1e9-47fb-aaf3-95672b353eb3', 'create_book', 1, '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('ff479be2-8a34-4901-bec3-34e344e2a92d', '823b614c-1bf1-4f41-921d-ffae0bb31efc', 'doc_edit', 0, '2026-03-03 11:49:24', '2026-03-03 11:49:24');

-- --------------------------------------------------------

--
-- 表的结构 `permission_groups`
--

CREATE TABLE `permission_groups` (
  `id` varchar(36) NOT NULL,
  `name` varchar(100) NOT NULL COMMENT '权限组名称',
  `role` int NOT NULL COMMENT '角色',
  `target_type` varchar(30) NOT NULL COMMENT '目标类型(knowledge/document)',
  `target_id` varchar(36) NOT NULL COMMENT '目标ID(知识库/文档ID)',
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT (now())
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- 转存表中的数据 `permission_groups`
--

INSERT INTO `permission_groups` (`id`, `name`, `role`, `target_type`, `target_id`, `created_at`, `updated_at`) VALUES
('1127af73-1db9-409b-a710-468582398a40', '无标题文档(Mk9PFPptBPOuYC8R)-只读', 1, 'document', '4050e261-a2f5-4a1e-82cf-048c094c822e', '2026-03-02 10:34:03', '2026-03-02 10:34:03'),
('1de5cf1f-b7c4-4ab1-b3a5-c0999848ea1c', '无标题文档(yrVBbCD2brECIksP)-管理员', 3, 'document', '46a2f968-c9d5-4ca2-98ed-f17b68c6da1f', '2026-03-03 11:40:07', '2026-03-03 11:40:07'),
('1e9cf2ee-1e0d-42a1-9ced-47018f31b91c', '无标题文档(rF20hudF2sIWR92J)-编辑', 2, 'document', 'fc9bc01a-adce-4e59-96b7-768d89ab2761', '2026-02-26 18:27:52', '2026-02-26 18:27:52'),
('1f4eb7df-e207-476c-9337-06415ff41b6d', '无标题文档(CAGSZx0ixHzcS8Td)-管理员', 3, 'document', '19d93c0b-3ef9-4c8b-a8ec-8da685cc3361', '2026-03-03 11:49:24', '2026-03-03 11:49:24'),
('29981c27-113a-436f-9eed-a03f7fb9981d', '无标题文档(Mk9PFPptBPOuYC8R)-编辑', 2, 'document', '4050e261-a2f5-4a1e-82cf-048c094c822e', '2026-03-02 10:34:03', '2026-03-02 10:34:03'),
('2efc8a38-3db1-4029-801d-a462e90f35bb', '无标题文档(phv4478zgJ4FfDm9)-管理员', 3, 'document', '3284405b-df33-4b8d-8a8f-3d3b03e39e76', '2026-03-04 19:23:23', '2026-03-04 19:23:23'),
('341c9007-9d36-4609-897d-578a4b9146ee', '无标题文档(AxnOEykdT0nqg2vG)-管理员', 3, 'document', '7f6b98c0-3384-4a06-adc5-c43ebbfc14e6', '2026-03-03 11:37:14', '2026-03-03 11:37:14'),
('37419883-832b-4b5c-ab18-c4a8e9997fad', '无标题文档(srk3c7amghtyfRJR)-编辑', 2, 'document', '5de08f4a-2581-4957-b30e-8114b8c8eb57', '2026-03-02 10:09:52', '2026-03-02 10:09:52'),
('39de80d4-3ccd-4c56-9248-25391b6c84ee', '无标题文档(CAGSZx0ixHzcS8Td)-编辑', 2, 'document', '19d93c0b-3ef9-4c8b-a8ec-8da685cc3361', '2026-03-03 11:49:24', '2026-03-03 11:49:24'),
('3c4e3ec2-2891-4622-808e-a3d422f6b1c0', '无标题文档(Mk9PFPptBPOuYC8R)-管理员', 3, 'document', '4050e261-a2f5-4a1e-82cf-048c094c822e', '2026-03-02 10:34:03', '2026-03-02 10:34:03'),
('4a7485c5-f18f-4f93-9ce8-224d25c17445', '无标题文档(yrVBbCD2brECIksP)-只读', 1, 'document', '46a2f968-c9d5-4ca2-98ed-f17b68c6da1f', '2026-03-03 11:40:07', '2026-03-03 11:40:07'),
('4d5e99b4-ce0c-41b7-8ce7-0b7b032ad0d3', 'ykx测试知识库A(o6BXQ1)-编辑', 2, 'knowledge', 'd4bcf15c-01b9-4998-a243-86bc2dc4e92b', '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('53ace0e8-2300-40dd-9d05-4bee73023a13', '无标题文档(FGHDkXRSoAwrNxA7)-编辑', 2, 'document', '89fe7832-1d1e-4c40-8f34-40cf211faa83', '2026-03-04 15:21:14', '2026-03-04 15:21:14'),
('5a7dbae6-058f-4874-af49-540bf1a7de84', '无标题文档(phv4478zgJ4FfDm9)-只读', 1, 'document', '3284405b-df33-4b8d-8a8f-3d3b03e39e76', '2026-03-04 19:23:23', '2026-03-04 19:23:23'),
('63f80453-a04b-43a8-8a3d-78721defb43c', '无标题文档(EnUvxNSFMN3KTjTf)-编辑', 2, 'document', 'c926bbfa-e7da-492a-a885-b29314cd5fa5', '2026-03-17 14:29:33', '2026-03-17 14:29:33'),
('642cd1b6-4c08-40fb-833c-a3a6039b3d55', '无标题文档(FGHDkXRSoAwrNxA7)-只读', 1, 'document', '89fe7832-1d1e-4c40-8f34-40cf211faa83', '2026-03-04 15:21:14', '2026-03-04 15:21:14'),
('6d4173d4-9e9e-4531-88da-753782ebd7e2', '无标题文档(rF20hudF2sIWR92J)-管理员', 3, 'document', 'fc9bc01a-adce-4e59-96b7-768d89ab2761', '2026-02-26 18:27:52', '2026-02-26 18:27:52'),
('6db65823-074a-49f0-8173-2a5e68aeb8df', '无标题文档(fJQA8guQtIxCzkBy)-编辑', 2, 'document', 'a16ee278-3865-4489-a8fe-737ac85aabf3', '2026-03-03 11:35:01', '2026-03-03 11:35:01'),
('71e84916-2164-4797-9625-a1f17778564f', '用于实现rag的知识库1(Nma4aX)-只读', 1, 'knowledge', '28ca1a60-11a9-46ba-a075-f17043823adc', '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('823b614c-1bf1-4f41-921d-ffae0bb31efc', '无标题文档(CAGSZx0ixHzcS8Td)-只读', 1, 'document', '19d93c0b-3ef9-4c8b-a8ec-8da685cc3361', '2026-03-03 11:49:24', '2026-03-03 11:49:24'),
('86194019-3723-4758-8716-3b7c6f5ab000', '无标题文档(srk3c7amghtyfRJR)-只读', 1, 'document', '5de08f4a-2581-4957-b30e-8114b8c8eb57', '2026-03-02 10:09:52', '2026-03-02 10:09:52'),
('87f30c16-b898-4335-a700-8439b7217e45', '无标题文档(phv4478zgJ4FfDm9)-编辑', 2, 'document', '3284405b-df33-4b8d-8a8f-3d3b03e39e76', '2026-03-04 19:23:23', '2026-03-04 19:23:23'),
('8a77b0f9-af46-475f-b220-c6498e9690b1', '无标题文档(fJQA8guQtIxCzkBy)-管理员', 3, 'document', 'a16ee278-3865-4489-a8fe-737ac85aabf3', '2026-03-03 11:35:01', '2026-03-03 11:35:01'),
('8f9b4d09-f0ad-4581-9363-ad78da8446b9', '用于实现rag的知识库1(Nma4aX)-编辑', 2, 'knowledge', '28ca1a60-11a9-46ba-a075-f17043823adc', '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('9ad1dee9-3819-411d-bb72-72da36aada94', '无标题文档(PjFOgZHUvwo1eADM)-管理员', 3, 'document', 'd11be93d-de3d-4838-b67c-b33360e2745b', '2026-03-17 15:48:38', '2026-03-17 15:48:38'),
('a287025b-d1e9-47fb-aaf3-95672b353eb3', 'ykx测试知识库A(o6BXQ1)-管理员', 3, 'knowledge', 'd4bcf15c-01b9-4998-a243-86bc2dc4e92b', '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('a4132219-4759-4915-88c6-9ca34ca21b5a', '无标题文档(yrVBbCD2brECIksP)-编辑', 2, 'document', '46a2f968-c9d5-4ca2-98ed-f17b68c6da1f', '2026-03-03 11:40:07', '2026-03-03 11:40:07'),
('b054a80a-42fd-49a3-bd94-88d624010339', 'ykx测试知识库A(o6BXQ1)-只读', 1, 'knowledge', 'd4bcf15c-01b9-4998-a243-86bc2dc4e92b', '2026-02-10 20:26:02', '2026-02-10 20:26:02'),
('b095315c-8231-40cf-ad63-82688ab49138', '无标题文档(AxnOEykdT0nqg2vG)-只读', 1, 'document', '7f6b98c0-3384-4a06-adc5-c43ebbfc14e6', '2026-03-03 11:37:14', '2026-03-03 11:37:14'),
('c14494ca-f2f3-46b5-9c18-9f0ac99f6109', '无标题文档(rF20hudF2sIWR92J)-只读', 1, 'document', 'fc9bc01a-adce-4e59-96b7-768d89ab2761', '2026-02-26 18:27:52', '2026-02-26 18:27:52'),
('d5ca457f-19d8-4ddc-8765-0a64487bbaea', '无标题文档(PjFOgZHUvwo1eADM)-编辑', 2, 'document', 'd11be93d-de3d-4838-b67c-b33360e2745b', '2026-03-17 15:48:38', '2026-03-17 15:48:38'),
('d63c0b3e-5db8-4d3e-b77d-2dd2a26654c1', '无标题文档(EnUvxNSFMN3KTjTf)-只读', 1, 'document', 'c926bbfa-e7da-492a-a885-b29314cd5fa5', '2026-03-17 14:29:33', '2026-03-17 14:29:33'),
('e421e043-f5c7-43a1-9a34-8cefdd5ffa25', '无标题文档(srk3c7amghtyfRJR)-管理员', 3, 'document', '5de08f4a-2581-4957-b30e-8114b8c8eb57', '2026-03-02 10:09:52', '2026-03-02 10:09:52'),
('e59e51cd-8bb1-44e9-b4de-1bd2602baf0d', '无标题文档(FGHDkXRSoAwrNxA7)-管理员', 3, 'document', '89fe7832-1d1e-4c40-8f34-40cf211faa83', '2026-03-04 15:21:14', '2026-03-04 15:21:14'),
('effaa58a-a9f1-488a-8482-9032a9629fc4', '无标题文档(AxnOEykdT0nqg2vG)-编辑', 2, 'document', '7f6b98c0-3384-4a06-adc5-c43ebbfc14e6', '2026-03-03 11:37:14', '2026-03-03 11:37:14'),
('f6886a73-ed14-433a-8696-2f030ede7236', '无标题文档(fJQA8guQtIxCzkBy)-只读', 1, 'document', 'a16ee278-3865-4489-a8fe-737ac85aabf3', '2026-03-03 11:35:01', '2026-03-03 11:35:01'),
('fbb40a2f-5bb4-438a-91be-098134ed0631', '无标题文档(EnUvxNSFMN3KTjTf)-管理员', 3, 'document', 'c926bbfa-e7da-492a-a885-b29314cd5fa5', '2026-03-17 14:29:33', '2026-03-17 14:29:33'),
('fdcfd51e-6188-4d8d-bec3-069ffb331a02', '用于实现rag的知识库1(Nma4aX)-管理员', 3, 'knowledge', '28ca1a60-11a9-46ba-a075-f17043823adc', '2026-03-17 15:44:39', '2026-03-17 15:44:39'),
('fe3036ae-d59d-4b7f-aacd-0525a3a6655c', '无标题文档(PjFOgZHUvwo1eADM)-只读', 1, 'document', 'd11be93d-de3d-4838-b67c-b33360e2745b', '2026-03-17 15:48:38', '2026-03-17 15:48:38');

-- --------------------------------------------------------

--
-- 表的结构 `space`
--

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
  `deleted_at` datetime DEFAULT NULL COMMENT '删除时间(NULL表示未删除)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- 转存表中的数据 `space`
--

INSERT INTO `space` (`id`, `type`, `domain`, `name`, `owner_id`, `contact_email`, `icon`, `description`, `created_at`, `updated_at`, `deleted_at`) VALUES
('3fb21c31-9b5c-4858-bf04-548ca5450bb9', 'PERSONAL', NULL, 'ykx测试3', 10, '15982819090@163.com', '{\"id\": \"0567a480-0f34-4ab8-9e5d-6ab99dfcd191\", \"fileName\": \"default_cover.png\", \"fileSize\": 3962, \"fileType\": \"image/png\"}', '', '2026-01-20 20:25:54', '2026-01-20 20:25:54', NULL),
('7e74e342-9086-4f1f-b621-27578d856208', 'PERSONAL', NULL, 'ykx测试空间1', 2, '15982819091@163.com', '{\"id\": \"0567a480-0f34-4ab8-9e5d-6ab99dfcd191\", \"fileName\": \"default_cover.png\", \"fileSize\": 3962, \"fileType\": \"image/png\"}', '用于测试的空间', '2026-01-19 18:34:59', '2026-01-19 18:34:59', NULL);

-- --------------------------------------------------------

--
-- 表的结构 `space_dept`
--

CREATE TABLE `space_dept` (
  `id` varchar(36) NOT NULL,
  `space_id` varchar(36) NOT NULL COMMENT '所属空间ID',
  `name` varchar(30) NOT NULL COMMENT '部门名称',
  `order` int NOT NULL COMMENT '排序',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted_at` datetime DEFAULT NULL COMMENT '删除时间(NULL表示未删除)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- 表的结构 `space_member`
--

CREATE TABLE `space_member` (
  `id` varchar(36) NOT NULL,
  `space_id` varchar(36) NOT NULL COMMENT '空间ID',
  `user_id` int NOT NULL COMMENT '用户ID',
  `role` enum('OWNER','ADMIN','MEMBER','EXTERNAL') NOT NULL COMMENT '角色',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted_at` datetime DEFAULT NULL COMMENT '删除时间(NULL表示未删除)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- 转存表中的数据 `space_member`
--

INSERT INTO `space_member` (`id`, `space_id`, `user_id`, `role`, `created_at`, `updated_at`, `deleted_at`) VALUES
('079a4e2b-ca52-4bc0-a093-3f43d5210eeb', '3fb21c31-9b5c-4858-bf04-548ca5450bb9', 10, 'OWNER', '2026-01-20 20:25:54', '2026-01-20 20:25:54', NULL),
('a9c031fa-80f2-4000-9b99-a65588163137', '7e74e342-9086-4f1f-b621-27578d856208', 2, 'OWNER', '2026-01-19 18:47:59', '2026-01-19 18:47:59', NULL);

-- --------------------------------------------------------

--
-- 表的结构 `team`
--

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
  `deleted_at` datetime DEFAULT NULL COMMENT '删除时间(NULL表示未删除)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- 转存表中的数据 `team`
--

INSERT INTO `team` (`id`, `name`, `icon`, `slug`, `space_id`, `description`, `visibility`, `created_at`, `updated_at`, `is_default`, `owner_id`, `joined_at`, `deleted_at`) VALUES
('1bc00c0d-8408-442a-9a9a-5c3aa726a127', '游开兴测试1', '', 'ykx_test1', '7e74e342-9086-4f1f-b621-27578d856208', '', 'PUBLIC', '2026-01-19 19:06:06', '2026-01-19 19:06:06', 1, 2, '2026-01-19 19:06:06', NULL),
('606d9538-8d29-4feb-8595-045d6078bb3e', 'ykx测试3', NULL, 'ShGv7g', '3fb21c31-9b5c-4858-bf04-548ca5450bb9', '', 'PUBLIC', '2026-01-20 20:25:54', '2026-01-20 20:25:54', 0, 10, '2026-01-20 20:25:54', NULL);

-- --------------------------------------------------------

--
-- 表的结构 `team_member`
--

CREATE TABLE `team_member` (
  `id` varchar(36) NOT NULL,
  `team_id` varchar(36) NOT NULL COMMENT '团队ID',
  `user_id` int NOT NULL COMMENT '用户ID',
  `role` enum('OWNER','ADMIN','MEMBER','EXTERNAL') NOT NULL COMMENT '角色',
  `dept_id` varchar(36) DEFAULT NULL COMMENT '部门ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- 转存表中的数据 `team_member`
--

INSERT INTO `team_member` (`id`, `team_id`, `user_id`, `role`, `dept_id`, `created_at`, `updated_at`) VALUES
('e48275aa-d4b4-4489-813e-6d5311e183d2', '606d9538-8d29-4feb-8595-045d6078bb3e', 10, 'OWNER', NULL, '2026-01-20 20:25:54', '2026-01-20 20:25:54'),
('ef842053-c31d-4292-b1e7-7038489eb7bb', '1bc00c0d-8408-442a-9a9a-5c3aa726a127', 2, 'OWNER', NULL, '2026-01-19 19:12:29', '2026-01-19 19:12:29');

-- --------------------------------------------------------

--
-- 表的结构 `user`
--

CREATE TABLE `user` (
  `id` int NOT NULL,
  `email` varchar(255) NOT NULL,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `nickname` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `deleted_at` datetime DEFAULT NULL COMMENT '删除时间(NULL表示未删除)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- 转存表中的数据 `user`
--

INSERT INTO `user` (`id`, `email`, `username`, `password`, `nickname`, `created_at`, `updated_at`, `deleted_at`) VALUES
(2, '15982819091@163.com', 'ykx_test1', '$2b$12$zCo2HWSPAT.gD/LMCheYEOaFZhcqqotIiZd09hvvmYs8qhwRmshou', '游开兴测试1', '2026-01-04 19:29:16', '2026-01-04 19:29:16', NULL),
(3, '1358645278@qq.com', 'ykx_test2', '$2b$12$vN4Tb4LoMiRKa6isaaMU0u8DYm5Dr/V1UylDUB.gKucqWzIC4HYz2', '游开兴测试2', '2026-01-04 20:00:14', '2026-01-04 20:00:14', NULL),
(4, '1392227049@qq.com', '123', '$2b$12$L1dBfmzlNSbf/SQg9cxeFet8FiRUuT.TOrc6dOQrv2zZMt19yExb.', '123', '2026-01-06 15:35:35', '2026-01-06 15:35:35', NULL),
(10, '15982819090@163.com', 'ykx_test3', '$2b$12$PG3d7lW71BNNjy/0NQcE0OPnBH10jyo7VhsCzBSBo1Cd.wcRWySka', 'ykx测试3', '2026-01-20 20:25:54', '2026-01-20 20:25:54', NULL);

-- --------------------------------------------------------

--
-- 替换视图以便查看 `v_permission_ability`
-- （参见下面的实际视图）
--
CREATE TABLE `v_permission_ability` (
`id` varchar(36)
,`permission_group_id` varchar(36)
,`ability_key` varchar(30)
,`enable` tinyint(1)
,`created_at` datetime
,`updated_at` datetime
,`group_name` varchar(100)
);

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
-- 表的索引 `collaborator`
--
ALTER TABLE `collaborator`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ix_collaborator_id` (`id`),
  ADD KEY `ix_collaborator_knowledge_id` (`knowledge_id`),
  ADD KEY `ix_collaborator_user_id` (`user_id`),
  ADD KEY `ix_collaborator_document_id` (`document_id`);

--
-- 表的索引 `collect`
--
ALTER TABLE `collect`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uix_user_knowledge_document` (`user_id`,`knowledge_id`,`document_id`),
  ADD KEY `ix_collect_document_id` (`document_id`),
  ADD KEY `ix_collect_knowledge_id` (`knowledge_id`),
  ADD KEY `ix_collect_user_id` (`user_id`);

--
-- 表的索引 `document_base`
--
ALTER TABLE `document_base`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uniq_knowledge_id_document_slug` (`knowledge_id`,`slug`),
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
-- 表的索引 `document_edit_history`
--
ALTER TABLE `document_edit_history`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uniq_document_id_edited_user_id` (`document_id`,`edited_user_id`),
  ADD KEY `ix_document_edit_history_document_id` (`document_id`),
  ADD KEY `ix_document_edit_history_edited_user_id` (`edited_user_id`);

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
-- 表的索引 `document_view_history`
--
ALTER TABLE `document_view_history`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uniq_document_id_viewed_user_id` (`document_id`,`viewed_user_id`),
  ADD KEY `ix_document_view_history_document_id` (`document_id`),
  ADD KEY `ix_document_view_history_viewed_user_id` (`viewed_user_id`);

--
-- 表的索引 `invitation`
--
ALTER TABLE `invitation`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `token` (`token`),
  ADD KEY `ix_invitation_id` (`id`),
  ADD KEY `ix_invitation_inviter_id` (`inviter_id`),
  ADD KEY `ix_invitation_knowledge_id` (`knowledge_id`),
  ADD KEY `ix_invitation_document_id` (`document_id`);

--
-- 表的索引 `knowledge_base`
--
ALTER TABLE `knowledge_base`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uniq_knowledge_slug` (`slug`),
  ADD UNIQUE KEY `ix_knowledge_base_slug` (`slug`),
  ADD KEY `ix_knowledge_base_group_id` (`group_id`),
  ADD KEY `ix_knowledge_base_id` (`id`),
  ADD KEY `ix_knowledge_base_user_id` (`user_id`),
  ADD KEY `ix_knowledge_base_space_id` (`space_id`),
  ADD KEY `ix_knowledge_base_team_id` (`team_id`);

--
-- 表的索引 `knowledge_daily_stats`
--
ALTER TABLE `knowledge_daily_stats`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uix_knowledge_id_stats_date` (`knowledge_id`,`stats_date`),
  ADD KEY `idx_knowledge_id` (`knowledge_id`),
  ADD KEY `idx_stats_date` (`stats_date`);

--
-- 表的索引 `knowledge_group`
--
ALTER TABLE `knowledge_group`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ix_knowledge_group_group_name` (`group_name`),
  ADD KEY `ix_knowledge_group_id` (`id`),
  ADD KEY `ix_knowledge_group_user_id` (`user_id`);

--
-- 表的索引 `permission_abilities`
--
ALTER TABLE `permission_abilities`
  ADD PRIMARY KEY (`id`),
  ADD KEY `permission_group_id` (`permission_group_id`);

--
-- 表的索引 `permission_groups`
--
ALTER TABLE `permission_groups`
  ADD PRIMARY KEY (`id`);

--
-- 表的索引 `space`
--
ALTER TABLE `space`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `domain` (`domain`),
  ADD KEY `owner_id` (`owner_id`);

--
-- 表的索引 `space_dept`
--
ALTER TABLE `space_dept`
  ADD PRIMARY KEY (`id`),
  ADD KEY `space_id` (`space_id`);

--
-- 表的索引 `space_member`
--
ALTER TABLE `space_member`
  ADD PRIMARY KEY (`id`),
  ADD KEY `space_id` (`space_id`),
  ADD KEY `user_id` (`user_id`);

--
-- 表的索引 `team`
--
ALTER TABLE `team`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ix_team_slug` (`slug`),
  ADD KEY `owner_id` (`owner_id`),
  ADD KEY `space_id` (`space_id`);

--
-- 表的索引 `team_member`
--
ALTER TABLE `team_member`
  ADD PRIMARY KEY (`id`),
  ADD KEY `dept_id` (`dept_id`),
  ADD KEY `team_id` (`team_id`),
  ADD KEY `user_id` (`user_id`);

--
-- 表的索引 `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ix_user_email` (`email`),
  ADD UNIQUE KEY `ix_user_username` (`username`),
  ADD KEY `ix_user_id` (`id`);

--
-- 在导出的表使用AUTO_INCREMENT
--

--
-- 使用表AUTO_INCREMENT `user`
--
ALTER TABLE `user`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

-- --------------------------------------------------------

--
-- 视图结构 `v_permission_ability`
--
DROP TABLE IF EXISTS `v_permission_ability`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`%` SQL SECURITY DEFINER VIEW `v_permission_ability`  AS SELECT `pa`.`id` AS `id`, `pa`.`permission_group_id` AS `permission_group_id`, `pa`.`ability_key` AS `ability_key`, `pa`.`enable` AS `enable`, `pa`.`created_at` AS `created_at`, `pa`.`updated_at` AS `updated_at`, `pg`.`name` AS `group_name` FROM (`permission_abilities` `pa` join `permission_groups` `pg` on((`pa`.`permission_group_id` = `pg`.`id`))) ;

--
-- 限制导出的表
--

--
-- 限制表 `collaborator`
--
ALTER TABLE `collaborator`
  ADD CONSTRAINT `collaborator_ibfk_1` FOREIGN KEY (`knowledge_id`) REFERENCES `knowledge_base` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `collaborator_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `collaborator_ibfk_3` FOREIGN KEY (`document_id`) REFERENCES `document_base` (`id`) ON DELETE CASCADE;

--
-- 限制表 `collect`
--
ALTER TABLE `collect`
  ADD CONSTRAINT `collect_ibfk_1` FOREIGN KEY (`document_id`) REFERENCES `document_base` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `collect_ibfk_2` FOREIGN KEY (`knowledge_id`) REFERENCES `knowledge_base` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `collect_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE;

--
-- 限制表 `document_base`
--
ALTER TABLE `document_base`
  ADD CONSTRAINT `document_base_ibfk_1` FOREIGN KEY (`knowledge_id`) REFERENCES `knowledge_base` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `document_base_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE;

--
-- 限制表 `document_content`
--
ALTER TABLE `document_content`
  ADD CONSTRAINT `document_content_ibfk_1` FOREIGN KEY (`document_id`) REFERENCES `document_base` (`id`) ON DELETE CASCADE;

--
-- 限制表 `document_edit_history`
--
ALTER TABLE `document_edit_history`
  ADD CONSTRAINT `document_edit_history_ibfk_2` FOREIGN KEY (`edited_user_id`) REFERENCES `user` (`id`),
  ADD CONSTRAINT `document_edit_history_ibfk_3` FOREIGN KEY (`document_id`) REFERENCES `document_base` (`id`) ON DELETE CASCADE;

--
-- 限制表 `document_node`
--
ALTER TABLE `document_node`
  ADD CONSTRAINT `document_node_ibfk_1` FOREIGN KEY (`document_id`) REFERENCES `document_base` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `document_node_ibfk_2` FOREIGN KEY (`first_child_id`) REFERENCES `document_node` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `document_node_ibfk_4` FOREIGN KEY (`next_id`) REFERENCES `document_node` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `document_node_ibfk_5` FOREIGN KEY (`parent_id`) REFERENCES `document_node` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `document_node_ibfk_6` FOREIGN KEY (`prev_id`) REFERENCES `document_node` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `document_node_ibfk_7` FOREIGN KEY (`knowledge_id`) REFERENCES `knowledge_base` (`id`) ON DELETE CASCADE;

--
-- 限制表 `document_view_history`
--
ALTER TABLE `document_view_history`
  ADD CONSTRAINT `document_view_history_ibfk_2` FOREIGN KEY (`viewed_user_id`) REFERENCES `user` (`id`),
  ADD CONSTRAINT `document_view_history_ibfk_3` FOREIGN KEY (`document_id`) REFERENCES `document_base` (`id`) ON DELETE CASCADE;

--
-- 限制表 `invitation`
--
ALTER TABLE `invitation`
  ADD CONSTRAINT `fk_document_id` FOREIGN KEY (`document_id`) REFERENCES `document_base` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `invitation_ibfk_1` FOREIGN KEY (`knowledge_id`) REFERENCES `knowledge_base` (`id`) ON DELETE CASCADE;

--
-- 限制表 `knowledge_base`
--
ALTER TABLE `knowledge_base`
  ADD CONSTRAINT `knowledge_base_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `knowledge_group` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `knowledge_base_ibfk_2` FOREIGN KEY (`team_id`) REFERENCES `team` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `knowledge_base_ibfk_3` FOREIGN KEY (`space_id`) REFERENCES `space` (`id`) ON DELETE CASCADE;

--
-- 限制表 `permission_abilities`
--
ALTER TABLE `permission_abilities`
  ADD CONSTRAINT `permission_abilities_ibfk_1` FOREIGN KEY (`permission_group_id`) REFERENCES `permission_groups` (`id`) ON DELETE CASCADE;

--
-- 限制表 `space`
--
ALTER TABLE `space`
  ADD CONSTRAINT `space_ibfk_1` FOREIGN KEY (`owner_id`) REFERENCES `user` (`id`) ON DELETE CASCADE;

--
-- 限制表 `space_dept`
--
ALTER TABLE `space_dept`
  ADD CONSTRAINT `space_dept_ibfk_1` FOREIGN KEY (`space_id`) REFERENCES `space` (`id`);

--
-- 限制表 `space_member`
--
ALTER TABLE `space_member`
  ADD CONSTRAINT `space_member_ibfk_1` FOREIGN KEY (`space_id`) REFERENCES `space` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `space_member_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE;

--
-- 限制表 `team`
--
ALTER TABLE `team`
  ADD CONSTRAINT `team_ibfk_1` FOREIGN KEY (`owner_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `team_ibfk_2` FOREIGN KEY (`space_id`) REFERENCES `space` (`id`) ON DELETE CASCADE;

--
-- 限制表 `team_member`
--
ALTER TABLE `team_member`
  ADD CONSTRAINT `team_member_ibfk_1` FOREIGN KEY (`dept_id`) REFERENCES `space_dept` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `team_member_ibfk_2` FOREIGN KEY (`team_id`) REFERENCES `team` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `team_member_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
