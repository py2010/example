/*
SQLyog Ultimate v12.08 (32 bit)
MySQL - 5.7.22 : Database - z
*********************************************************************
*/


/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

/*Table structure for table `django_migrations` */

CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

/*Data for the table `django_migrations` */

insert  into `django_migrations`(`id`,`app`,`name`,`applied`) values (1,'vr','0001_initial','2021-11-04 17:45:19.300687');

/*Table structure for table `test` */

CREATE TABLE `test` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` varchar(25) DEFAULT NULL,
  `sess_id` varchar(255) DEFAULT NULL,
  `keyword` varchar(25) NOT NULL,
  `url_n` varchar(3) DEFAULT NULL,
  `s_n` varchar(3) DEFAULT NULL,
  `select_url` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`,`keyword`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4;

/*Data for the table `test` */

insert  into `test`(`id`,`date`,`sess_id`,`keyword`,`url_n`,`s_n`,`select_url`) values (1,NULL,NULL,'111',NULL,NULL,NULL),(2,NULL,NULL,'222',NULL,NULL,NULL),(3,NULL,NULL,'222',NULL,NULL,NULL),(3,NULL,NULL,'333',NULL,NULL,NULL);

/*Table structure for table `vr_demo` */

CREATE TABLE `vr_demo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `p_id` smallint(6) DEFAULT NULL,
  `one_id` smallint(6) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;

/*Data for the table `vr_demo` */

insert  into `vr_demo`(`id`,`name`,`p_id`,`one_id`) values (1,'1',1,1),(2,'2',NULL,2),(3,'3333',2,NULL),(4,'4',2,3),(5,'5',3,4),(6,'6666',6,6);

/*Table structure for table `vr_middle` */

CREATE TABLE `vr_middle` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `demo_id` smallint(6) NOT NULL,
  `t_id` smallint(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `vr_middle_demo_id_t_id_a699e865_uniq` (`demo_id`,`t_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8;

/*Data for the table `vr_middle` */

insert  into `vr_middle`(`id`,`demo_id`,`t_id`) values (1,1,1),(2,1,2),(4,1,3),(5,2,3),(6,3,1),(8,3,4),(7,4,4);

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
