-- MySQL dump 10.13  Distrib 5.5.29, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: weather-severity
-- ------------------------------------------------------
-- Server version	5.5.29-0ubuntu0.12.10.1

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
-- Table structure for table `cap`
--

DROP TABLE IF EXISTS `cap`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cap` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `identifier` tinytext NOT NULL,
  `sent` datetime NOT NULL,
  `msgType` enum('Alert','Update','Cancel','Ack','Error') NOT NULL,
  `category` enum('Geo','Met','Safety','Security','Rescue','Fire','Health','Env','Transport','Infra','CBRNE','Other') NOT NULL,
  `event` varchar(255) NOT NULL,
  `responseType` enum('Shelter','Evacuate','Prepare','Execute','Avoid','Monitor','Assess','AllClear','None') DEFAULT NULL,
  `urgency` enum('Immediate','Expected','Future','Past','Unknown') NOT NULL,
  `severity` enum('Extreme','Severe','Moderate','Minor','Unknown') NOT NULL,
  `certainty` enum('Observed','Likely','Possible','Unlikely','Unknown') NOT NULL,
  `effective` datetime DEFAULT NULL,
  `onset` datetime DEFAULT NULL,
  `expires` datetime DEFAULT NULL,
  `headline` text,
  `description` text,
  `instruction` text,
  `begin_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `begintime` (`begin_time`) USING BTREE,
  KEY `expires` (`expires`),
  KEY `event` (`event`) USING HASH
) ENGINE=MyISAM AUTO_INCREMENT=429044 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,STRICT_ALL_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,TRADITIONAL,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER cap_insert BEFORE INSERT ON cap
  FOR EACH ROW BEGIN
    IF (NEW.onset IS NOT NULL) THEN
        SET NEW.begin_time = NEW.onset;
    ELSEIF (NEW.effective IS NOT NULL) THEN
        SET NEW.begin_time = NEW.effective;
    ELSE
        SET NEW.begin_time = NEW.sent;
    END IF;
  END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,STRICT_ALL_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,TRADITIONAL,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER halfcolumn_update BEFORE UPDATE ON cap
  FOR EACH ROW BEGIN
    IF (NEW.onset IS NOT NULL) THEN
        SET NEW.begin_time = NEW.onset;
    ELSEIF (NEW.effective IS NOT NULL) THEN
        SET NEW.begin_time = NEW.effective;
    ELSE
        SET NEW.begin_time = NEW.sent;
    END IF;
  END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `cap_fips`
--

DROP TABLE IF EXISTS `cap_fips`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cap_fips` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `fips` mediumint(8) unsigned NOT NULL,
  `cap` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fips` (`fips`),
  KEY `cap` (`cap`)
) ENGINE=InnoDB AUTO_INCREMENT=1835361 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `storm_events`
--

DROP TABLE IF EXISTS `storm_events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `storm_events` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `event_type` varchar(255) NOT NULL,
  `fips` mediumint(8) unsigned NOT NULL,
  `begin_time` datetime NOT NULL,
  `end_time` datetime NOT NULL,
  `injuries_direct` mediumint(8) unsigned NOT NULL,
  `injuries_indirect` mediumint(8) unsigned NOT NULL,
  `deaths_direct` mediumint(8) unsigned NOT NULL,
  `deaths_indirect` mediumint(8) unsigned NOT NULL,
  `property_damage` bigint(20) unsigned NOT NULL,
  `crop_damage` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `event_type` (`event_type`) USING HASH,
  KEY `fips` (`fips`) USING HASH,
  KEY `begin_time` (`begin_time`) USING BTREE,
  KEY `end_time` (`end_time`)
) ENGINE=InnoDB AUTO_INCREMENT=384932 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `valid_events`
--

DROP TABLE IF EXISTS `valid_events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `valid_events` (
  `cap_type` varchar(255) NOT NULL,
  `se_type` varchar(255) NOT NULL,
  `valid` bit(1) NOT NULL,
  UNIQUE KEY `unq` (`cap_type`,`se_type`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2013-05-14 13:38:17
