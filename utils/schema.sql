SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL';

CREATE SCHEMA IF NOT EXISTS `weather-severity` DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci ;
USE `weather-severity` ;

-- -----------------------------------------------------
-- Table `weather-severity`.`cap`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `weather-severity`.`cap` ;

CREATE  TABLE IF NOT EXISTS `weather-severity`.`cap` (
  `id` BIGINT NOT NULL AUTO_INCREMENT ,
  `identifier` TINYTEXT NOT NULL ,
  `sent` DATETIME NOT NULL ,
  `msgType` ENUM('Alert','Update','Cancel','Ack','Error') NOT NULL ,
  `category` ENUM('Geo','Met','Safety','Security','Rescue','Fire','Health','Env','Transport','Infra','CBRNE','Other') NOT NULL ,
  `event` TINYTEXT NOT NULL ,
  `responseType` ENUM('Shelter','Evacuate','Prepare','Execute','Avoid','Monitor','Assess','AllClear','None') NULL ,
  `urgency` ENUM('Immediate','Expected','Future','Past','Unknown') NOT NULL ,
  `severity` ENUM('Extreme','Severe','Moderate','Minor','Unknown') NOT NULL ,
  `certainty` ENUM('Observed','Likely','Possible','Unlikely','Unknown') NOT NULL ,
  `effective` DATETIME NULL ,
  `onset` DATETIME NULL ,
  `expires` DATETIME NULL ,
  `headline` TEXT NULL ,
  `description` TEXT NULL ,
  `instruction` TEXT NULL ,
  `begin_time` DATETIME NULL ,
  PRIMARY KEY (`id`) )
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `weather-severity`.`storm_events`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `weather-severity`.`storm_events` ;

CREATE  TABLE IF NOT EXISTS `weather-severity`.`storm_events` (
  `id` BIGINT NOT NULL AUTO_INCREMENT ,
  `event_type` TINYTEXT NOT NULL ,
  `fips` MEDIUMINT UNSIGNED NOT NULL ,
  `begin_time` DATETIME NOT NULL ,
  `end_time` DATETIME NOT NULL ,
  `injuries_direct` MEDIUMINT UNSIGNED NOT NULL ,
  `injuries_indirect` MEDIUMINT UNSIGNED NOT NULL ,
  `deaths_direct` MEDIUMINT UNSIGNED NOT NULL ,
  `deaths_indirect` MEDIUMINT UNSIGNED NOT NULL ,
  `property_damage` BIGINT UNSIGNED NOT NULL ,
  `crop_damage` BIGINT UNSIGNED NOT NULL ,
  PRIMARY KEY (`id`) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `weather-severity`.`cap_fips`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `weather-severity`.`cap_fips` ;

CREATE  TABLE IF NOT EXISTS `weather-severity`.`cap_fips` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT ,
  `fips` MEDIUMINT UNSIGNED NOT NULL ,
  `cap` BIGINT UNSIGNED NOT NULL ,
  PRIMARY KEY (`id`) )
ENGINE = InnoDB;

USE `weather-severity`;

DELIMITER $$

USE `weather-severity`$$
DROP TRIGGER IF EXISTS `weather-severity`.`cap_insert` $$
USE `weather-severity`$$


CREATE TRIGGER cap_insert BEFORE INSERT ON cap
  FOR EACH ROW BEGIN
    IF (NEW.onset IS NOT NULL) THEN
        SET NEW.begin_time = NEW.onset;
    ELSEIF (NEW.effective IS NOT NULL) THEN
        SET NEW.begin_time = NEW.effective;
    ELSE
        SET NEW.begin_time = NEW.sent;
    END IF;
  END
$$


USE `weather-severity`$$
DROP TRIGGER IF EXISTS `weather-severity`.`halfcolumn_update` $$
USE `weather-severity`$$


CREATE TRIGGER halfcolumn_update BEFORE UPDATE ON cap
  FOR EACH ROW BEGIN
    IF (NEW.onset IS NOT NULL) THEN
        SET NEW.begin_time = NEW.onset;
    ELSEIF (NEW.effective IS NOT NULL) THEN
        SET NEW.begin_time = NEW.effective;
    ELSE
        SET NEW.begin_time = NEW.sent;
    END IF;
  END

$$


DELIMITER ;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
