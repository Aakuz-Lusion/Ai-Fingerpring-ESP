-- phpMyAdmin SQL Dump
-- version 4.9.0.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 11, 2026 at 03:10 PM
-- Server version: 10.4.6-MariaDB
-- PHP Version: 7.2.22

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `attendance_test`
--

-- --------------------------------------------------------

--
-- Table structure for table `logs`
--

CREATE TABLE `logs` (
  `id` int(11) NOT NULL,
  `finger_id` int(11) DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `logs`
--

INSERT INTO `logs` (`id`, `finger_id`, `timestamp`) VALUES
(55, 105, '2026-04-08 09:25:00'),
(50, 105, '2026-03-14 09:25:00'),
(45, 105, '2026-03-13 09:25:00'),
(40, 105, '2026-03-12 09:25:00'),
(35, 105, '2026-03-11 09:25:00'),
(30, 105, '2026-03-10 09:25:00'),
(15, 105, '2026-03-10 09:25:00'),
(20, 105, '2026-03-11 09:22:00'),
(24, 104, '2026-03-12 09:19:00'),
(54, 104, '2026-04-08 09:20:00'),
(14, 104, '2026-03-10 09:20:00'),
(49, 104, '2026-03-14 09:20:00'),
(44, 104, '2026-03-13 09:20:00'),
(19, 104, '2026-03-11 09:18:00'),
(39, 104, '2026-03-12 09:20:00'),
(34, 104, '2026-03-11 09:20:00'),
(29, 104, '2026-03-10 09:20:00'),
(38, 103, '2026-03-12 09:15:00'),
(28, 103, '2026-03-10 09:15:00'),
(53, 103, '2026-04-08 09:15:00'),
(23, 103, '2026-03-12 09:14:00'),
(48, 103, '2026-03-14 09:15:00'),
(33, 103, '2026-03-11 09:15:00'),
(43, 103, '2026-03-13 09:15:00'),
(13, 103, '2026-03-10 09:15:00');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `logs`
--
ALTER TABLE `logs`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `logs`
--
ALTER TABLE `logs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=64;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
