-- phpMyAdmin SQL Dump
-- version 4.6.6deb5ubuntu0.5
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Dec 16, 2022 at 12:01 AM
-- Server version: 10.4.17-MariaDB-1:10.4.17+maria~bionic-log
-- PHP Version: 7.2.24-0ubuntu0.18.04.15

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `keeper-db`
--

-- --------------------------------------------------------

--
-- Table structure for table `bloxberg_certificate`
--

CREATE TABLE IF NOT EXISTS `bloxberg_certificate` (
  `transaction_id` varchar(255) NOT NULL,
  `repo_id` char(37) NOT NULL,
  `commit_id` char(41) NOT NULL,
  `path` text NOT NULL,
  `obj_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL,
  `owner` varchar(255) NOT NULL,
  `checksum` varchar(64) NOT NULL,
  `md` longtext NOT NULL,
  `md_json` longtext NOT NULL,
  `pdf` longtext DEFAULT NULL,
  `content_type` longtext NOT NULL,
  `content_name` longtext NOT NULL,
  `status` varchar(30) NOT NULL,
  `error_msg` longtext DEFAULT NULL,
  PRIMARY KEY (`obj_id`)
) ENGINE=InnoDB AUTO_INCREMENT=8878 DEFAULT CHARSET=utf8;


--
-- Table structure for table `cdc_repos`
--

CREATE TABLE IF NOT EXISTS `cdc_repos` (
  `repo_id` char(37) NOT NULL,
  `cdc_id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `owner` varchar(255) NOT NULL,
  `created` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `modified` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`repo_id`),
  KEY `cdc_id` (`cdc_id`)
) ENGINE=InnoDB AUTO_INCREMENT=698 DEFAULT CHARSET=utf8;


--
-- Table structure for table `doi_repos`
--

CREATE TABLE IF NOT EXISTS `doi_repos` (
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


--
-- Table structure for table `keeper_archive`
--

CREATE TABLE IF NOT EXISTS `keeper_archive` (
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
) ENGINE=InnoDB AUTO_INCREMENT=69 DEFAULT CHARSET=utf8;


--
-- Triggers `keeper_archive`
--
DELIMITER $$
CREATE TRIGGER `update_catalog_archive_status` AFTER UPDATE ON `keeper_archive` FOR EACH ROW UPDATE keeper_catalog SET is_archived=1 WHERE repo_id=NEW.repo_id AND is_archived=0 AND NEW.status='DONE'
$$
DELIMITER ;

--
-- Table structure for table `keeper_archive_owner_quota`
--

CREATE TABLE IF NOT EXISTS `keeper_archive_owner_quota` (
  `qid` int(11) NOT NULL AUTO_INCREMENT,
  `owner` varchar(255) NOT NULL,
  `repo_id` char(37) NOT NULL,
  `quota` smallint(6) DEFAULT NULL,
  PRIMARY KEY (`qid`,`owner`),
  UNIQUE KEY `unq_keeper_archive_quota_owner_repo_id` (`repo_id`,`owner`),
  KEY `ix_keeper_archive_owner_quota_repo_id` (`repo_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


--
-- Table structure for table `keeper_catalog`
--

CREATE TABLE IF NOT EXISTS `keeper_catalog` (
  `repo_id` varchar(37) NOT NULL,
  `repo_name` varchar(255) NOT NULL,
  `catalog_id` int(11) NOT NULL AUTO_INCREMENT,
  `owner` varchar(255) NOT NULL,
  `md` longtext NOT NULL,
  `created` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `modified` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `rm` timestamp NULL DEFAULT NULL,
  `is_archived` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`catalog_id`),
  UNIQUE KEY `repo_id` (`repo_id`)
) ENGINE=InnoDB AUTO_INCREMENT=34696 DEFAULT CHARSET=utf8;


/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
