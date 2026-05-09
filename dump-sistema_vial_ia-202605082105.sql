-- MySQL dump 10.13  Distrib 8.0.19, for Win64 (x86_64)
--
-- Host: localhost    Database: sistema_vial_ia
-- ------------------------------------------------------
-- Server version	8.4.6

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `deteccion_magnetica`
--

DROP TABLE IF EXISTS `deteccion_magnetica`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `deteccion_magnetica` (
  `id_magnetico` int NOT NULL AUTO_INCREMENT,
  `sensor_id` varchar(10) NOT NULL,
  `presencia_metal` tinyint(1) DEFAULT '0',
  `frecuencia_pulso` float DEFAULT NULL,
  `timestamp` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_magnetico`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `deteccion_magnetica`
--

LOCK TABLES `deteccion_magnetica` WRITE;
/*!40000 ALTER TABLE `deteccion_magnetica` DISABLE KEYS */;
INSERT INTO `deteccion_magnetica` VALUES (1,'HALL_02',0,NULL,'2026-05-07 23:58:19'),(2,'HALL_02',0,NULL,'2026-05-08 00:04:39');
/*!40000 ALTER TABLE `deteccion_magnetica` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `deteccion_visual`
--

DROP TABLE IF EXISTS `deteccion_visual`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `deteccion_visual` (
  `id_visual` int NOT NULL AUTO_INCREMENT,
  `calle` varchar(50) NOT NULL,
  `cantidad_vehiculos` int DEFAULT '0',
  `flujo_detectado` enum('Vacio','Bajo','Normal','Alto') NOT NULL,
  `timestamp` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_visual`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `deteccion_visual`
--

LOCK TABLES `deteccion_visual` WRITE;
/*!40000 ALTER TABLE `deteccion_visual` DISABLE KEYS */;
/*!40000 ALTER TABLE `deteccion_visual` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `estado_actuadores`
--

DROP TABLE IF EXISTS `estado_actuadores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `estado_actuadores` (
  `id_actuador` int NOT NULL AUTO_INCREMENT,
  `semaforo_estado` enum('Rojo','Amarillo','Verde') NOT NULL,
  `mensaje_oled` varchar(100) DEFAULT NULL,
  `buzzer_activo` tinyint(1) DEFAULT '0',
  `timestamp` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_actuador`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `estado_actuadores`
--

LOCK TABLES `estado_actuadores` WRITE;
/*!40000 ALTER TABLE `estado_actuadores` DISABLE KEYS */;
/*!40000 ALTER TABLE `estado_actuadores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proximidad_ultrasonica`
--

DROP TABLE IF EXISTS `proximidad_ultrasonica`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proximidad_ultrasonica` (
  `id_proximidad` int NOT NULL AUTO_INCREMENT,
  `sensor_id` varchar(10) NOT NULL,
  `distancia_cm` float NOT NULL,
  `estado_fila` enum('Vacio','Moderado','Critico') NOT NULL,
  `timestamp` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_proximidad`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proximidad_ultrasonica`
--

LOCK TABLES `proximidad_ultrasonica` WRITE;
/*!40000 ALTER TABLE `proximidad_ultrasonica` DISABLE KEYS */;
/*!40000 ALTER TABLE `proximidad_ultrasonica` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `trafico_historico`
--

DROP TABLE IF EXISTS `trafico_historico`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `trafico_historico` (
  `id_historial` int NOT NULL AUTO_INCREMENT,
  `calle` varchar(50) DEFAULT NULL,
  `promedio_vehiculos` float DEFAULT NULL,
  `hora_pico` tinyint(1) DEFAULT '0',
  `timestamp` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_historial`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `trafico_historico`
--

LOCK TABLES `trafico_historico` WRITE;
/*!40000 ALTER TABLE `trafico_historico` DISABLE KEYS */;
/*!40000 ALTER TABLE `trafico_historico` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'sistema_vial_ia'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-05-08 21:05:14
