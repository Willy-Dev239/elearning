-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Oct 08, 2026 at 02:23 PM
-- Server version: 11.7.2-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `elearning`
--

-- --------------------------------------------------------

--
-- Table structure for table `accounts_user`
--

CREATE TABLE `accounts_user` (
  `id` bigint(20) NOT NULL,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `role` varchar(10) NOT NULL,
  `phone` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Dumping data for table `accounts_user`
--

INSERT INTO `accounts_user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`, `role`, `phone`) VALUES
(1, 'pbkdf2_sha256$1000000$65YjveNVLLuDcP0voaRg2s$/+n8p8MGVsRIViw5uUVBtgfk7gmX2hM29WPvwODxdow=', NULL, 0, 'Willy', 'Niyuru', 'Willy', '', 0, 1, '2026-10-08 11:14:23.159436', 'STUDENT', ''),
(2, 'pbkdf2_sha256$1000000$ylWAQo7PjuPKzP0AI8gVB6$/4amUmQV3DaFCPWBKp9N2ERcqlCEB85df56QEnzdZ8w=', '2026-10-08 11:55:08.026528', 1, 'Willy@1', '', '', 'willy@gmail.com', 1, 1, '2026-10-08 11:17:37.203675', 'ADMIN', '');

-- --------------------------------------------------------

--
-- Table structure for table `accounts_user_groups`
--

CREATE TABLE `accounts_user_groups` (
  `id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `accounts_user_user_permissions`
--

CREATE TABLE `accounts_user_user_permissions` (
  `id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_group`
--

CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL,
  `name` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_group_permissions`
--

CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_permission`
--

CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Dumping data for table `auth_permission`
--

INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
(1, 'Can add log entry', 1, 'add_logentry'),
(2, 'Can change log entry', 1, 'change_logentry'),
(3, 'Can delete log entry', 1, 'delete_logentry'),
(4, 'Can view log entry', 1, 'view_logentry'),
(5, 'Can add permission', 2, 'add_permission'),
(6, 'Can change permission', 2, 'change_permission'),
(7, 'Can delete permission', 2, 'delete_permission'),
(8, 'Can view permission', 2, 'view_permission'),
(9, 'Can add group', 3, 'add_group'),
(10, 'Can change group', 3, 'change_group'),
(11, 'Can delete group', 3, 'delete_group'),
(12, 'Can view group', 3, 'view_group'),
(13, 'Can add content type', 4, 'add_contenttype'),
(14, 'Can change content type', 4, 'change_contenttype'),
(15, 'Can delete content type', 4, 'delete_contenttype'),
(16, 'Can view content type', 4, 'view_contenttype'),
(17, 'Can add session', 5, 'add_session'),
(18, 'Can change session', 5, 'change_session'),
(19, 'Can delete session', 5, 'delete_session'),
(20, 'Can view session', 5, 'view_session'),
(21, 'Can add user', 6, 'add_user'),
(22, 'Can change user', 6, 'change_user'),
(23, 'Can delete user', 6, 'delete_user'),
(24, 'Can view user', 6, 'view_user'),
(25, 'Can add school', 7, 'add_school'),
(26, 'Can change school', 7, 'change_school'),
(27, 'Can delete school', 7, 'delete_school'),
(28, 'Can view school', 7, 'view_school'),
(29, 'Can add classroom', 8, 'add_classroom'),
(30, 'Can change classroom', 8, 'change_classroom'),
(31, 'Can delete classroom', 8, 'delete_classroom'),
(32, 'Can view classroom', 8, 'view_classroom'),
(33, 'Can add enrollment', 9, 'add_enrollment'),
(34, 'Can change enrollment', 9, 'change_enrollment'),
(35, 'Can delete enrollment', 9, 'delete_enrollment'),
(36, 'Can view enrollment', 9, 'view_enrollment'),
(37, 'Can add course', 10, 'add_course'),
(38, 'Can change course', 10, 'change_course'),
(39, 'Can delete course', 10, 'delete_course'),
(40, 'Can view course', 10, 'view_course'),
(41, 'Can add lesson', 11, 'add_lesson'),
(42, 'Can change lesson', 11, 'change_lesson'),
(43, 'Can delete lesson', 11, 'delete_lesson'),
(44, 'Can view lesson', 11, 'view_lesson'),
(45, 'Can add question', 12, 'add_question'),
(46, 'Can change question', 12, 'change_question'),
(47, 'Can delete question', 12, 'delete_question'),
(48, 'Can view question', 12, 'view_question'),
(49, 'Can add choice', 13, 'add_choice'),
(50, 'Can change choice', 13, 'change_choice'),
(51, 'Can delete choice', 13, 'delete_choice'),
(52, 'Can view choice', 13, 'view_choice'),
(53, 'Can add quiz', 14, 'add_quiz'),
(54, 'Can change quiz', 14, 'change_quiz'),
(55, 'Can delete quiz', 14, 'delete_quiz'),
(56, 'Can view quiz', 14, 'view_quiz'),
(57, 'Can add attempt', 15, 'add_attempt'),
(58, 'Can change attempt', 15, 'change_attempt'),
(59, 'Can delete attempt', 15, 'delete_attempt'),
(60, 'Can view attempt', 15, 'view_attempt'),
(61, 'Can add fee', 16, 'add_fee'),
(62, 'Can change fee', 16, 'change_fee'),
(63, 'Can delete fee', 16, 'delete_fee'),
(64, 'Can view fee', 16, 'view_fee'),
(65, 'Can add payment', 17, 'add_payment'),
(66, 'Can change payment', 17, 'change_payment'),
(67, 'Can delete payment', 17, 'delete_payment'),
(68, 'Can view payment', 17, 'view_payment');

-- --------------------------------------------------------

--
-- Table structure for table `courses_course`
--

CREATE TABLE `courses_course` (
  `id` bigint(20) NOT NULL,
  `title` varchar(200) NOT NULL,
  `description` longtext NOT NULL,
  `created` datetime(6) NOT NULL,
  `classroom_id` bigint(20) NOT NULL,
  `teacher_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `courses_lesson`
--

CREATE TABLE `courses_lesson` (
  `id` bigint(20) NOT NULL,
  `title` varchar(200) NOT NULL,
  `kind` varchar(10) NOT NULL,
  `file` varchar(100) NOT NULL,
  `order` int(10) UNSIGNED NOT NULL CHECK (`order` >= 0),
  `created` datetime(6) NOT NULL,
  `course_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `django_admin_log`
--

CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) UNSIGNED NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Dumping data for table `django_admin_log`
--

INSERT INTO `django_admin_log` (`id`, `action_time`, `object_id`, `object_repr`, `action_flag`, `change_message`, `content_type_id`, `user_id`) VALUES
(1, '2026-10-08 11:26:51.934230', '1', 'Independante', 1, '[{\"added\": {}}]', 7, 2),
(2, '2026-10-08 11:27:33.489948', '1', 'Independante — Scence', 1, '[{\"added\": {}}]', 8, 2),
(3, '2026-10-08 11:28:43.322081', '1', 'Willy → Independante — Scence (2026-2027)', 1, '[{\"added\": {}}]', 9, 2),
(4, '2026-10-08 11:29:54.479931', '1', 'Minerval 1ere Tranche (Independante — Scence)', 1, '[{\"added\": {}}]', 16, 2);

-- --------------------------------------------------------

--
-- Table structure for table `django_content_type`
--

CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Dumping data for table `django_content_type`
--

INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES
(6, 'accounts', 'user'),
(1, 'admin', 'logentry'),
(3, 'auth', 'group'),
(2, 'auth', 'permission'),
(4, 'contenttypes', 'contenttype'),
(10, 'courses', 'course'),
(11, 'courses', 'lesson'),
(16, 'payments', 'fee'),
(17, 'payments', 'payment'),
(15, 'quizzes', 'attempt'),
(13, 'quizzes', 'choice'),
(12, 'quizzes', 'question'),
(14, 'quizzes', 'quiz'),
(8, 'schools', 'classroom'),
(9, 'schools', 'enrollment'),
(7, 'schools', 'school'),
(5, 'sessions', 'session');

-- --------------------------------------------------------

--
-- Table structure for table `django_migrations`
--

CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Dumping data for table `django_migrations`
--

INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES
(1, 'contenttypes', '0001_initial', '2026-10-08 11:12:18.550901'),
(2, 'contenttypes', '0002_remove_content_type_name', '2026-10-08 11:12:20.460474'),
(3, 'auth', '0001_initial', '2026-10-08 11:12:24.720658'),
(4, 'auth', '0002_alter_permission_name_max_length', '2026-10-08 11:12:25.462312'),
(5, 'auth', '0003_alter_user_email_max_length', '2026-10-08 11:12:25.479034'),
(6, 'auth', '0004_alter_user_username_opts', '2026-10-08 11:12:25.490200'),
(7, 'auth', '0005_alter_user_last_login_null', '2026-10-08 11:12:25.500364'),
(8, 'auth', '0006_require_contenttypes_0002', '2026-10-08 11:12:25.506822'),
(9, 'auth', '0007_alter_validators_add_error_messages', '2026-10-08 11:12:25.534767'),
(10, 'auth', '0008_alter_user_username_max_length', '2026-10-08 11:12:25.557582'),
(11, 'auth', '0009_alter_user_last_name_max_length', '2026-10-08 11:12:25.577754'),
(12, 'auth', '0010_alter_group_name_max_length', '2026-10-08 11:12:25.883349'),
(13, 'auth', '0011_update_proxy_permissions', '2026-10-08 11:12:25.901813'),
(14, 'auth', '0012_alter_user_first_name_max_length', '2026-10-08 11:12:25.928091'),
(15, 'accounts', '0001_initial', '2026-10-08 11:12:29.836061'),
(16, 'admin', '0001_initial', '2026-10-08 11:12:31.439541'),
(17, 'admin', '0002_logentry_remove_auto_add', '2026-10-08 11:12:31.499083'),
(18, 'admin', '0003_logentry_add_action_flag_choices', '2026-10-08 11:12:31.531511'),
(19, 'schools', '0001_initial', '2026-10-08 11:12:34.583726'),
(20, 'courses', '0001_initial', '2026-10-08 11:12:36.764216'),
(21, 'payments', '0001_initial', '2026-10-08 11:12:38.835122'),
(22, 'quizzes', '0001_initial', '2026-10-08 11:12:42.311507'),
(23, 'sessions', '0001_initial', '2026-10-08 11:12:42.852955'),
(24, 'accounts', '0002_alter_user_options_alter_user_phone_alter_user_role', '2026-10-08 12:08:26.292922'),
(25, 'schools', '0002_alter_classroom_options_alter_enrollment_options_and_more', '2026-10-08 12:08:26.466816'),
(26, 'courses', '0002_alter_course_options_alter_lesson_options_and_more', '2026-10-08 12:08:26.768831'),
(27, 'payments', '0002_alter_fee_options_alter_payment_options_and_more', '2026-10-08 12:08:27.123160'),
(28, 'quizzes', '0002_alter_attempt_options_alter_choice_options_and_more', '2026-10-08 12:08:27.503647');

-- --------------------------------------------------------

--
-- Table structure for table `django_session`
--

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Dumping data for table `django_session`
--

INSERT INTO `django_session` (`session_key`, `session_data`, `expire_date`) VALUES
('eb8z6rwtare07zdqsfowsz0uor4wgxm6', '.eJxVjEEOwiAQRe_C2pDSUsq4dO8ZyDAzSNVAUtqV8e7apAvd_vfef6mA25rD1mQJM6uz6tXpd4tIDyk74DuWW9VUy7rMUe-KPmjT18ryvBzu30HGlr-1JZrAkHgEg31nO4ARmIScs8kaJGRgw07iYIaEPiHSRECjd1YcRfX-APtFOPs:1xEmiK:DjmOKzX8_mKnC02yQywPyyeDWBPfJxAndD46_Rnp2eE', '2026-10-22 11:55:08.143409'),
('zff8pxpuo7mru2ul5r9h1u8mn1hwpo2k', '.eJxVjEEOwiAQRe_C2pDSUsq4dO8ZyDAzSNVAUtqV8e7apAvd_vfef6mA25rD1mQJM6uz6tXpd4tIDyk74DuWW9VUy7rMUe-KPmjT18ryvBzu30HGlr-1JZrAkHgEg31nO4ARmIScs8kaJGRgw07iYIaEPiHSRECjd1YcRfX-APtFOPs:1xEmFt:o5W4_pDnRqNX7DyKnaFNN89hLp-uXS_VgkRJNcBMjdA', '2026-10-22 11:25:45.018832');

-- --------------------------------------------------------

--
-- Table structure for table `payments_fee`
--

CREATE TABLE `payments_fee` (
  `id` bigint(20) NOT NULL,
  `title` varchar(200) NOT NULL,
  `amount` decimal(12,2) NOT NULL,
  `due_date` date NOT NULL,
  `classroom_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Dumping data for table `payments_fee`
--

INSERT INTO `payments_fee` (`id`, `title`, `amount`, `due_date`, `classroom_id`) VALUES
(1, 'Minerval 1ere Tranche', 80000.00, '2026-10-08', 1);

-- --------------------------------------------------------

--
-- Table structure for table `payments_payment`
--

CREATE TABLE `payments_payment` (
  `id` bigint(20) NOT NULL,
  `amount` decimal(12,2) NOT NULL,
  `method` varchar(15) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `status` varchar(10) NOT NULL,
  `reference` varchar(40) NOT NULL,
  `created` datetime(6) NOT NULL,
  `fee_id` bigint(20) NOT NULL,
  `student_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `quizzes_attempt`
--

CREATE TABLE `quizzes_attempt` (
  `id` bigint(20) NOT NULL,
  `score` int(10) UNSIGNED NOT NULL CHECK (`score` >= 0),
  `total` int(10) UNSIGNED NOT NULL CHECK (`total` >= 0),
  `created` datetime(6) NOT NULL,
  `student_id` bigint(20) NOT NULL,
  `quiz_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `quizzes_choice`
--

CREATE TABLE `quizzes_choice` (
  `id` bigint(20) NOT NULL,
  `text` varchar(300) NOT NULL,
  `is_correct` tinyint(1) NOT NULL,
  `question_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `quizzes_question`
--

CREATE TABLE `quizzes_question` (
  `id` bigint(20) NOT NULL,
  `text` varchar(500) NOT NULL,
  `order` int(10) UNSIGNED NOT NULL CHECK (`order` >= 0),
  `quiz_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `quizzes_quiz`
--

CREATE TABLE `quizzes_quiz` (
  `id` bigint(20) NOT NULL,
  `title` varchar(200) NOT NULL,
  `description` longtext NOT NULL,
  `pass_mark` int(10) UNSIGNED NOT NULL CHECK (`pass_mark` >= 0),
  `course_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `schools_classroom`
--

CREATE TABLE `schools_classroom` (
  `id` bigint(20) NOT NULL,
  `name` varchar(100) NOT NULL,
  `school_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Dumping data for table `schools_classroom`
--

INSERT INTO `schools_classroom` (`id`, `name`, `school_id`) VALUES
(1, 'Scence', 1);

-- --------------------------------------------------------

--
-- Table structure for table `schools_enrollment`
--

CREATE TABLE `schools_enrollment` (
  `id` bigint(20) NOT NULL,
  `academic_year` varchar(9) NOT NULL,
  `created` datetime(6) NOT NULL,
  `classroom_id` bigint(20) NOT NULL,
  `student_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Dumping data for table `schools_enrollment`
--

INSERT INTO `schools_enrollment` (`id`, `academic_year`, `created`, `classroom_id`, `student_id`) VALUES
(1, '2026-2027', '2026-10-08 11:28:43.319078', 1, 1);

-- --------------------------------------------------------

--
-- Table structure for table `schools_school`
--

CREATE TABLE `schools_school` (
  `id` bigint(20) NOT NULL,
  `name` varchar(150) NOT NULL,
  `address` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Dumping data for table `schools_school`
--

INSERT INTO `schools_school` (`id`, `name`, `address`) VALUES
(1, 'Independante', 'Bwiza');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `accounts_user`
--
ALTER TABLE `accounts_user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indexes for table `accounts_user_groups`
--
ALTER TABLE `accounts_user_groups`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `accounts_user_groups_user_id_group_id_59c0b32f_uniq` (`user_id`,`group_id`),
  ADD KEY `accounts_user_groups_group_id_bd11a704_fk_auth_group_id` (`group_id`);

--
-- Indexes for table `accounts_user_user_permissions`
--
ALTER TABLE `accounts_user_user_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `accounts_user_user_permi_user_id_permission_id_2ab516c2_uniq` (`user_id`,`permission_id`),
  ADD KEY `accounts_user_user_p_permission_id_113bb443_fk_auth_perm` (`permission_id`);

--
-- Indexes for table `auth_group`
--
ALTER TABLE `auth_group`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  ADD KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`);

--
-- Indexes for table `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`);

--
-- Indexes for table `courses_course`
--
ALTER TABLE `courses_course`
  ADD PRIMARY KEY (`id`),
  ADD KEY `courses_course_classroom_id_741bf988_fk_schools_classroom_id` (`classroom_id`),
  ADD KEY `courses_course_teacher_id_846fa526_fk_accounts_user_id` (`teacher_id`);

--
-- Indexes for table `courses_lesson`
--
ALTER TABLE `courses_lesson`
  ADD PRIMARY KEY (`id`),
  ADD KEY `courses_lesson_course_id_16bc4882_fk_courses_course_id` (`course_id`);

--
-- Indexes for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  ADD KEY `django_admin_log_user_id_c564eba6_fk_accounts_user_id` (`user_id`);

--
-- Indexes for table `django_content_type`
--
ALTER TABLE `django_content_type`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`);

--
-- Indexes for table `django_migrations`
--
ALTER TABLE `django_migrations`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `django_session`
--
ALTER TABLE `django_session`
  ADD PRIMARY KEY (`session_key`),
  ADD KEY `django_session_expire_date_a5c62663` (`expire_date`);

--
-- Indexes for table `payments_fee`
--
ALTER TABLE `payments_fee`
  ADD PRIMARY KEY (`id`),
  ADD KEY `payments_fee_classroom_id_15349538_fk_schools_classroom_id` (`classroom_id`);

--
-- Indexes for table `payments_payment`
--
ALTER TABLE `payments_payment`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `reference` (`reference`),
  ADD KEY `payments_payment_fee_id_18550ee6_fk_payments_fee_id` (`fee_id`),
  ADD KEY `payments_payment_student_id_b5fab56a_fk_accounts_user_id` (`student_id`);

--
-- Indexes for table `quizzes_attempt`
--
ALTER TABLE `quizzes_attempt`
  ADD PRIMARY KEY (`id`),
  ADD KEY `quizzes_attempt_student_id_e3bf362d_fk_accounts_user_id` (`student_id`),
  ADD KEY `quizzes_attempt_quiz_id_5dc3f292_fk_quizzes_quiz_id` (`quiz_id`);

--
-- Indexes for table `quizzes_choice`
--
ALTER TABLE `quizzes_choice`
  ADD PRIMARY KEY (`id`),
  ADD KEY `quizzes_choice_question_id_46d39dbb_fk_quizzes_question_id` (`question_id`);

--
-- Indexes for table `quizzes_question`
--
ALTER TABLE `quizzes_question`
  ADD PRIMARY KEY (`id`),
  ADD KEY `quizzes_question_quiz_id_70961654_fk_quizzes_quiz_id` (`quiz_id`);

--
-- Indexes for table `quizzes_quiz`
--
ALTER TABLE `quizzes_quiz`
  ADD PRIMARY KEY (`id`),
  ADD KEY `quizzes_quiz_course_id_6476d9c4_fk_courses_course_id` (`course_id`);

--
-- Indexes for table `schools_classroom`
--
ALTER TABLE `schools_classroom`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `schools_classroom_school_id_name_bee1ccca_uniq` (`school_id`,`name`);

--
-- Indexes for table `schools_enrollment`
--
ALTER TABLE `schools_enrollment`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `schools_enrollment_student_id_classroom_id__6b6aa4bc_uniq` (`student_id`,`classroom_id`,`academic_year`),
  ADD KEY `schools_enrollment_classroom_id_39941e98_fk_schools_classroom_id` (`classroom_id`);

--
-- Indexes for table `schools_school`
--
ALTER TABLE `schools_school`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `accounts_user`
--
ALTER TABLE `accounts_user`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `accounts_user_groups`
--
ALTER TABLE `accounts_user_groups`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `accounts_user_user_permissions`
--
ALTER TABLE `accounts_user_user_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_group`
--
ALTER TABLE `auth_group`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_permission`
--
ALTER TABLE `auth_permission`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=69;

--
-- AUTO_INCREMENT for table `courses_course`
--
ALTER TABLE `courses_course`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `courses_lesson`
--
ALTER TABLE `courses_lesson`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `django_content_type`
--
ALTER TABLE `django_content_type`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- AUTO_INCREMENT for table `django_migrations`
--
ALTER TABLE `django_migrations`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;

--
-- AUTO_INCREMENT for table `payments_fee`
--
ALTER TABLE `payments_fee`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `payments_payment`
--
ALTER TABLE `payments_payment`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `quizzes_attempt`
--
ALTER TABLE `quizzes_attempt`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `quizzes_choice`
--
ALTER TABLE `quizzes_choice`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `quizzes_question`
--
ALTER TABLE `quizzes_question`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `quizzes_quiz`
--
ALTER TABLE `quizzes_quiz`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `schools_classroom`
--
ALTER TABLE `schools_classroom`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `schools_enrollment`
--
ALTER TABLE `schools_enrollment`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `schools_school`
--
ALTER TABLE `schools_school`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `accounts_user_groups`
--
ALTER TABLE `accounts_user_groups`
  ADD CONSTRAINT `accounts_user_groups_group_id_bd11a704_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  ADD CONSTRAINT `accounts_user_groups_user_id_52b62117_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`);

--
-- Constraints for table `accounts_user_user_permissions`
--
ALTER TABLE `accounts_user_user_permissions`
  ADD CONSTRAINT `accounts_user_user_p_permission_id_113bb443_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `accounts_user_user_p_user_id_e4f0a161_fk_accounts_` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`);

--
-- Constraints for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);

--
-- Constraints for table `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);

--
-- Constraints for table `courses_course`
--
ALTER TABLE `courses_course`
  ADD CONSTRAINT `courses_course_classroom_id_741bf988_fk_schools_classroom_id` FOREIGN KEY (`classroom_id`) REFERENCES `schools_classroom` (`id`),
  ADD CONSTRAINT `courses_course_teacher_id_846fa526_fk_accounts_user_id` FOREIGN KEY (`teacher_id`) REFERENCES `accounts_user` (`id`);

--
-- Constraints for table `courses_lesson`
--
ALTER TABLE `courses_lesson`
  ADD CONSTRAINT `courses_lesson_course_id_16bc4882_fk_courses_course_id` FOREIGN KEY (`course_id`) REFERENCES `courses_course` (`id`);

--
-- Constraints for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  ADD CONSTRAINT `django_admin_log_user_id_c564eba6_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`);

--
-- Constraints for table `payments_fee`
--
ALTER TABLE `payments_fee`
  ADD CONSTRAINT `payments_fee_classroom_id_15349538_fk_schools_classroom_id` FOREIGN KEY (`classroom_id`) REFERENCES `schools_classroom` (`id`);

--
-- Constraints for table `payments_payment`
--
ALTER TABLE `payments_payment`
  ADD CONSTRAINT `payments_payment_fee_id_18550ee6_fk_payments_fee_id` FOREIGN KEY (`fee_id`) REFERENCES `payments_fee` (`id`),
  ADD CONSTRAINT `payments_payment_student_id_b5fab56a_fk_accounts_user_id` FOREIGN KEY (`student_id`) REFERENCES `accounts_user` (`id`);

--
-- Constraints for table `quizzes_attempt`
--
ALTER TABLE `quizzes_attempt`
  ADD CONSTRAINT `quizzes_attempt_quiz_id_5dc3f292_fk_quizzes_quiz_id` FOREIGN KEY (`quiz_id`) REFERENCES `quizzes_quiz` (`id`),
  ADD CONSTRAINT `quizzes_attempt_student_id_e3bf362d_fk_accounts_user_id` FOREIGN KEY (`student_id`) REFERENCES `accounts_user` (`id`);

--
-- Constraints for table `quizzes_choice`
--
ALTER TABLE `quizzes_choice`
  ADD CONSTRAINT `quizzes_choice_question_id_46d39dbb_fk_quizzes_question_id` FOREIGN KEY (`question_id`) REFERENCES `quizzes_question` (`id`);

--
-- Constraints for table `quizzes_question`
--
ALTER TABLE `quizzes_question`
  ADD CONSTRAINT `quizzes_question_quiz_id_70961654_fk_quizzes_quiz_id` FOREIGN KEY (`quiz_id`) REFERENCES `quizzes_quiz` (`id`);

--
-- Constraints for table `quizzes_quiz`
--
ALTER TABLE `quizzes_quiz`
  ADD CONSTRAINT `quizzes_quiz_course_id_6476d9c4_fk_courses_course_id` FOREIGN KEY (`course_id`) REFERENCES `courses_course` (`id`);

--
-- Constraints for table `schools_classroom`
--
ALTER TABLE `schools_classroom`
  ADD CONSTRAINT `schools_classroom_school_id_b093c6a4_fk_schools_school_id` FOREIGN KEY (`school_id`) REFERENCES `schools_school` (`id`);

--
-- Constraints for table `schools_enrollment`
--
ALTER TABLE `schools_enrollment`
  ADD CONSTRAINT `schools_enrollment_classroom_id_39941e98_fk_schools_classroom_id` FOREIGN KEY (`classroom_id`) REFERENCES `schools_classroom` (`id`),
  ADD CONSTRAINT `schools_enrollment_student_id_0e7db83f_fk_accounts_user_id` FOREIGN KEY (`student_id`) REFERENCES `accounts_user` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
