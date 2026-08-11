SET NAMES utf8mb4;
-- 创建数据库
CREATE DATABASE IF NOT EXISTS user_stu DEFAULT CHARSET utf8mb4;

USE user_stu;

-- ===================== 用户登录信息表 =====================
CREATE TABLE IF NOT EXISTS t_user (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键，用户id',
  `username` varchar(100) DEFAULT NULL COMMENT '用户名',
  `password` varchar(255) DEFAULT NULL COMMENT '密码（SHA256哈希）',
  `nickname` varchar(100) DEFAULT NULL COMMENT '用户名称',
  `role` varchar(20) DEFAULT '学生' COMMENT '角色：管理员 / 学生',
  `student_id` int DEFAULT NULL COMMENT '关联学生表id（角色为学生时）',
  `createDate` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户登录信息表';

-- ===================== 学生信息表 =====================
CREATE TABLE IF NOT EXISTS `student` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键，学生id',
  `name` varchar(100) DEFAULT NULL COMMENT '学生姓名',
  `gender` varchar(50) DEFAULT NULL COMMENT '性别',
  `age` int DEFAULT NULL COMMENT '年龄',
  `phone_number` varchar(100) DEFAULT NULL COMMENT '手机号',
  `birthday` date DEFAULT NULL COMMENT '出生日期',
  `grade` varchar(50) DEFAULT NULL COMMENT '年级',
  `class_id` int DEFAULT NULL COMMENT '所属班级id',
  `teacher_id` int DEFAULT NULL COMMENT '负责老师id',
  `createDate` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='学生信息表';

-- ===================== 老师信息表 =====================
CREATE TABLE IF NOT EXISTS `teachers` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键，老师id',
  `name` varchar(100) DEFAULT NULL COMMENT '老师姓名',
  `gender` varchar(50) DEFAULT NULL COMMENT '性别',
  `age` int DEFAULT NULL COMMENT '年龄',
  `subject` varchar(100) DEFAULT NULL COMMENT '教授科目',
  `phone` varchar(100) DEFAULT NULL COMMENT '手机号',
  `createDate` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='老师信息表';

-- ===================== 班级信息表 =====================
CREATE TABLE IF NOT EXISTS `classes` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键，班级id',
  `name` varchar(100) DEFAULT NULL COMMENT '班级名称',
  `grade` varchar(50) DEFAULT NULL COMMENT '年级',
  `head_teacher_id` int DEFAULT NULL COMMENT '班主任（老师）id',
  `createDate` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='班级信息表';

-- ===================== 课程信息表 =====================
CREATE TABLE IF NOT EXISTS `courses` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键，课程id',
  `name` varchar(100) DEFAULT NULL COMMENT '课程名称',
  `credit` int DEFAULT 0 COMMENT '学分',
  `teacher_id` int DEFAULT NULL COMMENT '授课老师id',
  `createDate` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='课程信息表';

-- ===================== 自愈：为已存在的旧表补齐缺失列 =====================
-- 若数据库已存在结构不完整的表，以下存储过程会为其补齐代码所需的列
DROP PROCEDURE IF EXISTS ensure_columns;
DELIMITER $$
CREATE PROCEDURE ensure_columns()
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.COLUMNS
                 WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'student' AND COLUMN_NAME = 'phone_number') THEN
    ALTER TABLE student ADD COLUMN phone_number varchar(100) DEFAULT NULL COMMENT '手机号' AFTER age;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.COLUMNS
                 WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'student' AND COLUMN_NAME = 'birthday') THEN
    ALTER TABLE student ADD COLUMN birthday date DEFAULT NULL COMMENT '出生日期' AFTER phone_number;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.COLUMNS
                 WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'student' AND COLUMN_NAME = 'grade') THEN
    ALTER TABLE student ADD COLUMN grade varchar(50) DEFAULT NULL COMMENT '年级' AFTER birthday;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.COLUMNS
                 WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'student' AND COLUMN_NAME = 'class_id') THEN
    ALTER TABLE student ADD COLUMN class_id int DEFAULT NULL COMMENT '所属班级id' AFTER grade;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.COLUMNS
                 WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'student' AND COLUMN_NAME = 'teacher_id') THEN
    ALTER TABLE student ADD COLUMN teacher_id int DEFAULT NULL COMMENT '负责老师id' AFTER class_id;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.COLUMNS
                 WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 't_user' AND COLUMN_NAME = 'role') THEN
    ALTER TABLE t_user ADD COLUMN role varchar(20) DEFAULT '学生' COMMENT '角色：管理员/学生' AFTER nickname;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.COLUMNS
                 WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 't_user' AND COLUMN_NAME = 'student_id') THEN
    ALTER TABLE t_user ADD COLUMN student_id int DEFAULT NULL COMMENT '关联学生表id' AFTER role;
  END IF;
END$$
DELIMITER ;

CALL ensure_columns();
DROP PROCEDURE ensure_columns;

-- ===================== 种子数据：老师 =====================
INSERT IGNORE INTO `teachers` (`id`, `name`, `gender`, `age`, `subject`, `phone`) VALUES
(1, '王明', '女', 35, '语文', '13800000001'),
(2, '李强', '男', 40, '数学', '13800000002'),
(3, '赵丽', '女', 32, '英语', '13800000003'),
(4, '孙军', '男', 45, '物理', '13800000004');

-- ===================== 种子数据：班级 =====================
INSERT IGNORE INTO `classes` (`id`, `name`, `grade`, `head_teacher_id`) VALUES
(1, '高一(1)班', '高一', 1),
(2, '高一(2)班', '高一', 2),
(3, '高二(1)班', '高二', 3),
(4, '高三(1)班', '高三', 4);

-- ===================== 种子数据：课程 =====================
INSERT IGNORE INTO `courses` (`id`, `name`, `credit`, `teacher_id`) VALUES
(1, '语文', 4, 1),
(2, '数学', 4, 2),
(3, '英语', 3, 3),
(4, '物理', 3, 4);

-- ===================== 种子数据：学生 =====================
INSERT IGNORE INTO `student` (`id`, `name`, `gender`, `age`, `phone_number`, `birthday`, `grade`, `class_id`, `teacher_id`) VALUES
(1, '张三', '男', 18, '18537857839', '2008-06-27', '高一', 1, 1),
(2, '李四', '女', 17, '17489214576', '2009-10-15', '高一', 1, 1),
(3, '王五', '男', 19, '12748369459', '2007-02-23', '高二', 3, 2),
(4, '赵六', '女', 18, '12788793425', '2008-07-05', '高二', 3, 2),
(5, '孙七', '男', 17, '12321133240', '2009-01-28', '高一', 2, 3),
(6, '周八', '女', 18, '13845678901', '2008-05-12', '高一', 2, 3);

-- 幂等：确保学生 手机号/生日/年级/班级/老师 关联信息正确（补齐旧数据缺失字段）
UPDATE `student` SET `phone_number`='18537857839', `birthday`='2008-06-27', `grade`='高一', `class_id`=1, `teacher_id`=1 WHERE `id`=1;
UPDATE `student` SET `phone_number`='17489214576', `birthday`='2009-10-15', `grade`='高一', `class_id`=1, `teacher_id`=1 WHERE `id`=2;
UPDATE `student` SET `phone_number`='12748369459', `birthday`='2007-02-23', `grade`='高二', `class_id`=3, `teacher_id`=2 WHERE `id`=3;
UPDATE `student` SET `phone_number`='12788793425', `birthday`='2008-07-05', `grade`='高二', `class_id`=3, `teacher_id`=2 WHERE `id`=4;
UPDATE `student` SET `phone_number`='12321133240', `birthday`='2009-01-28', `grade`='高一', `class_id`=2, `teacher_id`=3 WHERE `id`=5;
UPDATE `student` SET `phone_number`='13845678901', `birthday`='2008-05-12', `grade`='高一', `class_id`=2, `teacher_id`=3 WHERE `id`=6;

-- ===================== 种子数据：用户（密码均为 123456 的 SHA256 哈希） =====================
INSERT IGNORE INTO `t_user` (`id`, `username`, `password`, `nickname`, `role`, `student_id`) VALUES
(9,  'admin',   '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '张陈鹏', '管理员', NULL),
(10, 'ubuntu',  '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '老乌',   '管理员', NULL),
(11, '张三',    '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '张三',   '学生',   1);

-- 幂等：确保管理员账号角色与密码正确（兼容旧数据补齐，密码为 123456 的 SHA256）
UPDATE `t_user` SET `role`='管理员', `password`='8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92' WHERE `id` IN (9, 10);
-- 幂等：确保学生账号关联到正确的学生记录
UPDATE `t_user` SET `role`='学生', `student_id`=1 WHERE `id`=11;
