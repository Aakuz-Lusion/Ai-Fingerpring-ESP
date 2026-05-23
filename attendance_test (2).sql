-- phpMyAdmin SQL Dump
-- version 4.9.0.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 11, 2026 at 02:33 PM
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
(1, 101, '2026-02-15 20:16:56'),
(2, 102, '2026-02-15 20:16:56'),
(3, 1, '2026-02-15 20:04:11'),
(4, 11, '2026-02-15 20:04:31'),
(5, 11, '1970-01-01 05:30:22'),
(6, 10, '1970-01-01 05:30:35'),
(7, 1, '2026-04-09 19:06:04'),
(8, 11, '2026-04-09 19:06:36'),
(9, 4, '2026-04-09 19:07:26'),
(10, 44, '2026-04-09 19:09:21'),
(11, 101, '2026-03-10 09:05:00'),
(12, 102, '2026-03-10 09:10:00'),
(13, 103, '2026-03-10 09:15:00'),
(14, 104, '2026-03-10 09:20:00'),
(15, 105, '2026-03-10 09:25:00'),
(16, 101, '2026-03-11 09:03:00'),
(17, 102, '2026-03-11 09:08:00'),
(18, 103, '2026-03-11 09:12:00'),
(19, 104, '2026-03-11 09:18:00'),
(20, 105, '2026-03-11 09:22:00'),
(21, 101, '2026-03-12 09:04:00'),
(22, 102, '2026-03-12 09:09:00'),
(23, 103, '2026-03-12 09:14:00'),
(24, 104, '2026-03-12 09:19:00'),
(25, 105, '2026-03-12 09:24:00'),
(26, 101, '2026-03-10 09:05:00'),
(27, 102, '2026-03-10 09:10:00'),
(28, 103, '2026-03-10 09:15:00'),
(29, 104, '2026-03-10 09:20:00'),
(30, 105, '2026-03-10 09:25:00'),
(31, 101, '2026-03-11 09:05:00'),
(32, 102, '2026-03-11 09:10:00'),
(33, 103, '2026-03-11 09:15:00'),
(34, 104, '2026-03-11 09:20:00'),
(35, 105, '2026-03-11 09:25:00'),
(36, 101, '2026-03-12 09:05:00'),
(37, 102, '2026-03-12 09:10:00'),
(38, 103, '2026-03-12 09:15:00'),
(39, 104, '2026-03-12 09:20:00'),
(40, 105, '2026-03-12 09:25:00'),
(41, 101, '2026-03-13 09:05:00'),
(42, 102, '2026-03-13 09:10:00'),
(43, 103, '2026-03-13 09:15:00'),
(44, 104, '2026-03-13 09:20:00'),
(45, 105, '2026-03-13 09:25:00'),
(46, 101, '2026-03-14 09:05:00'),
(47, 102, '2026-03-14 09:10:00'),
(48, 103, '2026-03-14 09:15:00'),
(49, 104, '2026-03-14 09:20:00'),
(50, 105, '2026-03-14 09:25:00'),
(51, 101, '2026-04-08 09:05:00'),
(52, 102, '2026-04-08 09:10:00'),
(53, 103, '2026-04-08 09:15:00'),
(54, 104, '2026-04-08 09:20:00'),
(55, 105, '2026-04-08 09:25:00'),
(56, 14, '2026-04-09 20:11:19'),
(57, 23, '2026-04-09 20:15:01'),
(58, 14, '2026-04-11 13:42:31'),
(59, 1, '2026-04-11 13:42:41'),
(60, 12, '2026-04-11 17:46:52'),
(61, 4, '2026-04-11 17:47:06');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `finger_id` int(11) DEFAULT NULL,
  `enrolled` int(11) DEFAULT 0,
  `delete_flag` int(11) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `name`, `finger_id`, `enrolled`, `delete_flag`) VALUES
(1, 'Rams', 44, 2, 0),
(2, 'Test User B', 50, 2, 0),
(3, 'Aakuz', 101, 2, 0),
(5, 'Rj', 111, 2, 0),
(7, 'Lusion', 102, 0, 0),
(8, 'Sub', 103, 0, 0),
(9, 'Anits', 104, 0, 0),
(11, 'tdz', 14, 0, 0),
(12, 'Lasttz', 23, 0, 0),
(13, 'sam', 4, 2, 0);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `logs`
--
ALTER TABLE `logs`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `finger_id` (`finger_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `logs`
--
ALTER TABLE `logs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=62;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
