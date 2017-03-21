-- phpMyAdmin SQL Dump
-- version 4.2.12deb2+deb8u2
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Mar 21, 2017 at 10:43 AM
-- Server version: 5.5.54-0+deb8u1
-- PHP Version: 5.6.30-0+deb8u1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `keeper-db`
--

-- --------------------------------------------------------

--
-- Table structure for table `cdc_repos`
--

CREATE TABLE IF NOT EXISTS `cdc_repos` (
  `repo_id` char(37) NOT NULL,
`cdc_id` int(10) unsigned NOT NULL,
  `owner` varchar(255) NOT NULL,
  `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `modified` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00'
) ENGINE=InnoDB AUTO_INCREMENT=2073 DEFAULT CHARSET=utf8;


-- --------------------------------------------------------

--
-- Table structure for table `keeper_catalog`
--

CREATE TABLE IF NOT EXISTS `keeper_catalog` (
  `repo_id` varchar(37) NOT NULL,
`catalog_id` int(11) NOT NULL,
  `owner` varchar(255) NOT NULL,
  `md` text NOT NULL,
  `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `modified` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00'
) ENGINE=InnoDB AUTO_INCREMENT=87 DEFAULT CHARSET=utf8;


--
-- Indexes for dumped tables
--

--
-- Indexes for table `cdc_repos`
--
ALTER TABLE `cdc_repos`
 ADD PRIMARY KEY (`repo_id`), ADD KEY `cdc_id` (`cdc_id`);

--
-- Indexes for table `keeper_catalog`
--
ALTER TABLE `keeper_catalog`
 ADD PRIMARY KEY (`catalog_id`), ADD UNIQUE KEY `repo_id` (`repo_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `cdc_repos`
--
ALTER TABLE `cdc_repos`
MODIFY `cdc_id` int(10) unsigned NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=2073;
--
-- AUTO_INCREMENT for table `keeper_catalog`
--
ALTER TABLE `keeper_catalog`
MODIFY `catalog_id` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=87;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

