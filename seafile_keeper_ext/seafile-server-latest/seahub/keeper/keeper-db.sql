-- MySQL dump 10.16  Distrib 10.2.30-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: keeper-db
-- ------------------------------------------------------
-- Server version	10.2.30-MariaDB-10.2.30+maria~jessie-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `bloxberg_certificate`
--

DROP TABLE IF EXISTS `bloxberg_certificate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bloxberg_certificate` (
  `transaction_id` varchar(255) NOT NULL,
  `repo_id` char(37) NOT NULL,
  `commit_id` char(41) NOT NULL,
  `path` text NOT NULL,
  `obj_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL,
  `owner` varchar(255) NOT NULL,
  `checksum` varchar(64) NOT NULL,
  PRIMARY KEY (`obj_id`)
) ENGINE=InnoDB AUTO_INCREMENT=388 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cdc_repos`
--

DROP TABLE IF EXISTS `cdc_repos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cdc_repos` (
  `repo_id` char(37) NOT NULL,
  `cdc_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `owner` varchar(255) NOT NULL,
  `created` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `modified` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`repo_id`),
  KEY `cdc_id` (`cdc_id`)
) ENGINE=InnoDB AUTO_INCREMENT=646 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `doi_repos`
--

DROP TABLE IF EXISTS `doi_repos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `doi_repos` (
  `repo_id` char(37) NOT NULL,
  `repo_name` varchar(255) NOT NULL,
  `doi` char(37) NOT NULL,
  `prev_doi` char(37) DEFAULT NULL,
  `commit_id` char(41) DEFAULT NULL,
  `owner` varchar(255) NOT NULL,
  `md` text NOT NULL,
  `created` timestamp NOT NULL DEFAULT current_timestamp(),
  `rm` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`doi`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `keeper_archive`
--

DROP TABLE IF EXISTS `keeper_archive`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `keeper_archive` (
  `aid` int(11) NOT NULL AUTO_INCREMENT,
  `repo_id` char(37) NOT NULL,
  `commit_id` char(41) NOT NULL,
  `repo_name` varchar(255) NOT NULL,
  `owner` varchar(255) NOT NULL,
  `version` smallint(6) NOT NULL,
  `checksum` varchar(100) DEFAULT NULL,
  `external_path` text DEFAULT NULL,
  `md` longtext DEFAULT NULL,
  `status` varchar(30) NOT NULL DEFAULT 'NOT_QUEUED',
  `error_msg` text DEFAULT NULL,
  `created` datetime DEFAULT current_timestamp(),
  `archived` datetime DEFAULT NULL,
  PRIMARY KEY (`aid`),
  UNIQUE KEY `unq_keeper_archive_repo_id_version` (`repo_id`,`owner`,`version`),
  KEY `ix_keeper_archive_created` (`created`),
  KEY `ix_keeper_archive_repo_id` (`repo_id`),
  KEY `ix_keeper_archive_version` (`version`),
  KEY `ix_keeper_archive_owner` (`owner`)
) ENGINE=InnoDB AUTO_INCREMENT=1122 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `update_catalog_archive_status` AFTER UPDATE ON `keeper_archive` FOR EACH ROW UPDATE keeper_catalog SET is_archived=1 WHERE repo_id=NEW.repo_id AND is_archived=0 AND NEW.status='DONE' */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `keeper_archive_owner_quota`
--

DROP TABLE IF EXISTS `keeper_archive_owner_quota`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `keeper_archive_owner_quota` (
  `qid` int(11) NOT NULL AUTO_INCREMENT,
  `owner` varchar(255) NOT NULL,
  `repo_id` char(37) NOT NULL,
  `quota` smallint(6) DEFAULT NULL,
  PRIMARY KEY (`qid`,`owner`),
  UNIQUE KEY `unq_keeper_archive_quota_owner_repo_id` (`repo_id`,`owner`),
  KEY `ix_keeper_archive_owner_quota_repo_id` (`repo_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `keeper_catalog`
--

DROP TABLE IF EXISTS `keeper_catalog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `keeper_catalog` (
  `repo_id` varchar(37) NOT NULL,
  `repo_name` varchar(255) NOT NULL,
  `catalog_id` int(11) NOT NULL AUTO_INCREMENT,
  `owner` varchar(255) NOT NULL,
  `md` text NOT NULL,
  `created` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `modified` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `rm` timestamp NULL DEFAULT NULL,
  `is_archived` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`catalog_id`),
  UNIQUE KEY `repo_id` (`repo_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2134 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-02-26 18:37:42

