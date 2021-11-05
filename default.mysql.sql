/*
SQLyog Ultimate v12.08 (32 bit)
MySQL - 5.7.22 : Database - xyf
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
/*Table structure for table `a_b` */

CREATE TABLE `a_b` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4;

/*Data for the table `a_b` */

insert  into `a_b`(`id`,`name`) values (1,'1'),(2,'2'),(3,'3');

/*Table structure for table `a_m` */

CREATE TABLE `a_m` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `one_id` int(11) DEFAULT NULL,
  `p_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `o_id` (`one_id`),
  KEY `a_m_p_id_12c00990_fk_a_p_id` (`p_id`),
  CONSTRAINT `a_m_o_id_3af2348b_fk_a_one_id` FOREIGN KEY (`one_id`) REFERENCES `a_one` (`id`),
  CONSTRAINT `a_m_p_id_12c00990_fk_a_p_id` FOREIGN KEY (`p_id`) REFERENCES `a_p` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4;

/*Data for the table `a_m` */

insert  into `a_m`(`id`,`name`,`one_id`,`p_id`) values (1,'1',1,1),(2,'2',2,1),(3,'3',3,2),(4,'4',4,2),(5,'5',5,3),(6,'6',NULL,NULL);

/*Table structure for table `a_m2t` */

CREATE TABLE `a_m2t` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `m_id` int(11) NOT NULL,
  `t_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `a_m2t_m_id_b814ed6a_fk_a_m_id` (`m_id`),
  KEY `a_m2t_t_id_5700694c_fk_a_t_id` (`t_id`),
  CONSTRAINT `a_m2t_m_id_b814ed6a_fk_a_m_id` FOREIGN KEY (`m_id`) REFERENCES `a_m` (`id`),
  CONSTRAINT `a_m2t_t_id_5700694c_fk_a_t_id` FOREIGN KEY (`t_id`) REFERENCES `a_t` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4;

/*Data for the table `a_m2t` */

insert  into `a_m2t`(`id`,`m_id`,`t_id`) values (1,2,2),(2,2,3),(3,2,4),(4,1,2),(5,4,3),(6,4,6),(7,6,3),(8,6,5),(9,6,6);

/*Table structure for table `a_m_t` */

CREATE TABLE `a_m_t` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `m_id` int(11) NOT NULL,
  `t_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `a_m_t_m_id_t_id_2234b7df_uniq` (`m_id`,`t_id`),
  KEY `a_m_t_t_id_1421fb9c_fk_a_t_id` (`t_id`),
  CONSTRAINT `a_m_t_m_id_f4f20c8a_fk_a_m_id` FOREIGN KEY (`m_id`) REFERENCES `a_m` (`id`),
  CONSTRAINT `a_m_t_t_id_1421fb9c_fk_a_t_id` FOREIGN KEY (`t_id`) REFERENCES `a_t` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4;

/*Data for the table `a_m_t` */

insert  into `a_m_t`(`id`,`m_id`,`t_id`) values (4,1,2),(1,2,2),(2,2,3),(3,2,4),(5,4,3),(6,4,6),(7,6,3),(8,6,5),(9,6,6);

/*Table structure for table `a_one` */

CREATE TABLE `a_one` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `b_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `a_one_b_id_14bcc822_fk_a_b_id` (`b_id`),
  CONSTRAINT `a_one_b_id_14bcc822_fk_a_b_id` FOREIGN KEY (`b_id`) REFERENCES `a_b` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4;

/*Data for the table `a_one` */

insert  into `a_one`(`id`,`name`,`b_id`) values (1,'1',1),(2,'2',1),(3,'3666666',2),(4,'4',2),(5,'5',3),(7,'ooo43444535',2);

/*Table structure for table `a_p` */

CREATE TABLE `a_p` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `desc` varchar(100) DEFAULT NULL,
  `b_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `a_p_b_id_8b090004_fk_a_b_id` (`b_id`),
  CONSTRAINT `a_p_b_id_8b090004_fk_a_b_id` FOREIGN KEY (`b_id`) REFERENCES `a_b` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4;

/*Data for the table `a_p` */

insert  into `a_p`(`id`,`name`,`desc`,`b_id`) values (1,'111',NULL,1),(2,'22',NULL,1),(3,'333333',NULL,2);

/*Table structure for table `a_t` */

CREATE TABLE `a_t` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `one_id` int(11) DEFAULT NULL,
  `p_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `o_id` (`one_id`),
  KEY `a_t_p_id_06e6cdb2_fk_a_p_id` (`p_id`),
  CONSTRAINT `a_t_o_id_0cf125ad_fk_a_one_id` FOREIGN KEY (`one_id`) REFERENCES `a_one` (`id`),
  CONSTRAINT `a_t_p_id_06e6cdb2_fk_a_p_id` FOREIGN KEY (`p_id`) REFERENCES `a_p` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4;

/*Data for the table `a_t` */

insert  into `a_t`(`id`,`name`,`one_id`,`p_id`) values (1,'1',NULL,1),(2,'2',2,1),(3,'3',3,1),(4,'4',4,1),(5,'5',5,1),(6,'6',NULL,NULL),(7,'ttt444',NULL,1);

/*Table structure for table `auth_group` */

CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/*Data for the table `auth_group` */

/*Table structure for table `auth_group_permissions` */

CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/*Data for the table `auth_group_permissions` */

/*Table structure for table `auth_permission` */

CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=65 DEFAULT CHARSET=utf8mb4;

/*Data for the table `auth_permission` */

insert  into `auth_permission`(`id`,`name`,`content_type_id`,`codename`) values (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add user',4,'add_user'),(14,'Can change user',4,'change_user'),(15,'Can delete user',4,'delete_user'),(16,'Can view user',4,'view_user'),(17,'Can add content type',5,'add_contenttype'),(18,'Can change content type',5,'change_contenttype'),(19,'Can delete content type',5,'delete_contenttype'),(20,'Can view content type',5,'view_contenttype'),(21,'Can add session',6,'add_session'),(22,'Can change session',6,'change_session'),(23,'Can delete session',6,'delete_session'),(24,'Can view session',6,'view_session'),(25,'Can add TOTP device',7,'add_totpdevice'),(26,'Can change TOTP device',7,'change_totpdevice'),(27,'Can delete TOTP device',7,'delete_totpdevice'),(28,'Can view TOTP device',7,'view_totpdevice'),(29,'Can add 网站用户',8,'add_userprofile'),(30,'Can change 网站用户',8,'change_userprofile'),(31,'Can delete 网站用户',8,'delete_userprofile'),(32,'Can view 网站用户',8,'view_userprofile'),(33,'Can add BB',9,'add_b'),(34,'Can change BB',9,'change_b'),(35,'Can delete BB',9,'delete_b'),(36,'Can view BB',9,'view_b'),(37,'Can add M',10,'add_m'),(38,'Can change M',10,'change_m'),(39,'Can delete M',10,'delete_m'),(40,'Can view M',10,'view_m'),(41,'Can add OO',11,'add_one'),(42,'Can change OO',11,'change_one'),(43,'Can delete OO',11,'delete_one'),(44,'Can view OO',11,'view_one'),(45,'Can add 类型',12,'add_p'),(46,'Can change 类型',12,'change_p'),(47,'Can delete 类型',12,'delete_p'),(48,'Can view 类型',12,'view_p'),(49,'Can add T',13,'add_t'),(50,'Can change T',13,'change_t'),(51,'Can delete T',13,'delete_t'),(52,'Can view T',13,'view_t'),(53,'Can add M2T',14,'add_m2t'),(54,'Can change M2T',14,'change_m2t'),(55,'Can delete M2T',14,'delete_m2t'),(56,'Can view M2T',14,'view_m2t'),(57,'Can add Demo',15,'add_demo'),(58,'Can change Demo',15,'change_demo'),(59,'Can delete Demo',15,'delete_demo'),(60,'Can view Demo',15,'view_demo'),(61,'Can add 虚拟关联m2m中间表',16,'add_middle'),(62,'Can change 虚拟关联m2m中间表',16,'change_middle'),(63,'Can delete 虚拟关联m2m中间表',16,'delete_middle'),(64,'Can view 虚拟关联m2m中间表',16,'view_middle');

/*Table structure for table `auth_user` */

CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4;

/*Data for the table `auth_user` */

insert  into `auth_user`(`id`,`password`,`last_login`,`is_superuser`,`username`,`first_name`,`last_name`,`email`,`is_staff`,`is_active`,`date_joined`) values (1,'pbkdf2_sha256$150000$YuqyMI3ZKG82$XDNg6AIAOpkjRapOpeqWCSCTiFrM6WUjf45Y5egQKEw=','2021-11-05 11:42:15.622133',1,'demo','333','333','',1,1,'2021-10-20 11:26:00.000000'),(3,'555',NULL,0,'21215555555','','','',0,1,'2021-10-25 14:49:00.000000'),(4,'555',NULL,0,'21215555','','','',0,1,'2021-10-25 14:49:00.000000');

/*Table structure for table `auth_user_groups` */

CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/*Data for the table `auth_user_groups` */

/*Table structure for table `auth_user_user_permissions` */

CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/*Data for the table `auth_user_user_permissions` */

/*Table structure for table `django_admin_log` */

CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/*Data for the table `django_admin_log` */

/*Table structure for table `django_content_type` */

CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4;

/*Data for the table `django_content_type` */

insert  into `django_content_type`(`id`,`app_label`,`model`) values (9,'a','b'),(10,'a','m'),(14,'a','m2t'),(11,'a','one'),(12,'a','p'),(13,'a','t'),(1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'auth','user'),(5,'contenttypes','contenttype'),(8,'ops','userprofile'),(7,'otp_totp','totpdevice'),(6,'sessions','session'),(15,'vr','demo'),(16,'vr','middle');

/*Table structure for table `django_migrations` */

CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4;

/*Data for the table `django_migrations` */

insert  into `django_migrations`(`id`,`app`,`name`,`applied`) values (1,'a','0001_initial','2021-10-20 11:25:53.129567'),(2,'contenttypes','0001_initial','2021-10-20 11:25:54.818386'),(3,'auth','0001_initial','2021-10-20 11:25:55.201339'),(4,'admin','0001_initial','2021-10-20 11:25:56.591840'),(5,'admin','0002_logentry_remove_auto_add','2021-10-20 11:25:56.934432'),(6,'admin','0003_logentry_add_action_flag_choices','2021-10-20 11:25:56.945537'),(7,'contenttypes','0002_remove_content_type_name','2021-10-20 11:25:57.178706'),(8,'auth','0002_alter_permission_name_max_length','2021-10-20 11:25:57.333538'),(9,'auth','0003_alter_user_email_max_length','2021-10-20 11:25:57.358098'),(10,'auth','0004_alter_user_username_opts','2021-10-20 11:25:57.373287'),(11,'auth','0005_alter_user_last_login_null','2021-10-20 11:25:57.482790'),(12,'auth','0006_require_contenttypes_0002','2021-10-20 11:25:57.490650'),(13,'auth','0007_alter_validators_add_error_messages','2021-10-20 11:25:57.504709'),(14,'auth','0008_alter_user_username_max_length','2021-10-20 11:25:57.655060'),(15,'auth','0009_alter_user_last_name_max_length','2021-10-20 11:25:57.811614'),(16,'auth','0010_alter_group_name_max_length','2021-10-20 11:25:57.885557'),(17,'auth','0011_update_proxy_permissions','2021-10-20 11:25:57.902843'),(18,'ops','0001_initial','2021-10-20 11:25:57.969883'),(21,'sessions','0001_initial','2021-10-20 11:25:58.635149');

/*Table structure for table `django_session` */

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/*Data for the table `django_session` */

insert  into `django_session`(`session_key`,`session_data`,`expire_date`) values ('3vb0ykjkrzlj9vsnon7s754kcnq5me4p','NTMzYThjN2IyMTAyY2FlYzQyMzNmNzdlMjI2MDBlOGVjODY2M2RjNjp7ImxvZ2luX3VzZXJfaWQiOjEsIl9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiJhNzUzZGIwNzE1NTliNzFjYjU3NmViZTc5Njk0ZjQ0ZDQzZmQ1NTM3In0=','2021-10-23 11:28:39.811446'),('ib5oxhiwc3vmjxie7d084zs94ngai5on','MTU3ODE5YzQ1ZjNjNjRhODkwOGM1YjVmMGI2M2Q3Y2U0MmFhMDQ2YTp7ImxvZ2luX3VzZXJfaWQiOjEsIl9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiI1MTMxNWJkODMyYTE0OTI3ZTU1ZGM4YzJkOTRmNmZmYjQ2NWViODYzIn0=','2021-11-08 11:42:15.630478'),('okhb64oz2julnho8gfqsl7z3vi91wmdc','NTMzYThjN2IyMTAyY2FlYzQyMzNmNzdlMjI2MDBlOGVjODY2M2RjNjp7ImxvZ2luX3VzZXJfaWQiOjEsIl9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiJhNzUzZGIwNzE1NTliNzFjYjU3NmViZTc5Njk0ZjQ0ZDQzZmQ1NTM3In0=','2021-10-28 09:48:03.529380');

/*Table structure for table `ops_userprofile` */

CREATE TABLE `ops_userprofile` (
  `user_id` int(11) NOT NULL,
  `name` varchar(20) DEFAULT NULL,
  `phone` varchar(11) DEFAULT NULL,
  `ftp_readonly` tinyint(1) NOT NULL,
  `weixin` varchar(100) DEFAULT NULL,
  `otp` tinyint(1) NOT NULL,
  `show_otp` tinyint(1) NOT NULL,
  `userdays` smallint(6) NOT NULL,
  `usertime` datetime(6) NOT NULL,
  `pwdtime` datetime(6) NOT NULL,
  `pwddays` smallint(6) NOT NULL,
  PRIMARY KEY (`user_id`),
  CONSTRAINT `ops_userprofile_user_id_30b728bc_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/*Data for the table `ops_userprofile` */

insert  into `ops_userprofile`(`user_id`,`name`,`phone`,`ftp_readonly`,`weixin`,`otp`,`show_otp`,`userdays`,`usertime`,`pwdtime`,`pwddays`) values (1,'','',0,'',0,1,365,'2021-10-20 11:28:39.780721','2021-11-05 11:41:53.196014',90);

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
