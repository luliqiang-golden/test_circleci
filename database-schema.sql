-- phpMyAdmin SQL Dump
-- version 4.7.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Jun 19, 2018 at 06:55 PM
-- Server version: 5.7.19
-- PHP Version: 5.6.31

SET FOREIGN_KEY_CHECKS=0;
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `seed-to-sale-development`
--

-- --------------------------------------------------------

--
-- Table structure for table `activities`
--

DROP TABLE IF EXISTS `activities`;
CREATE TABLE IF NOT EXISTS `activities` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `organization_id` int(11) NOT NULL,
  `created_by` int(11) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `created_by` (`created_by`),
  KEY `organization` (`organization_id`)
) ENGINE=InnoDB AUTO_INCREMENT=77 DEFAULT CHARSET=utf8 COMMENT='An activity is a log of every event and data update in the system.';

--
-- Dumping data for table `activities`
--

INSERT INTO `activities` (`id`, `name`, `organization_id`, `created_by`, `timestamp`) VALUES
(40, 'receive_inventory', 1, 1, '2018-01-01 20:09:59'),
(41, 'receive_inventory', 1, 1, '2018-01-15 20:13:58'),
(42, 'create_mother', 1, 1, '2018-02-01 20:15:53'),
(43, 'create_mother', 1, 1, '2018-02-03 20:15:56'),
(44, 'create_mother', 1, 1, '2018-02-15 20:16:13'),
(45, 'create_mother', 1, 1, '2018-02-16 20:16:15'),
(46, 'create_batch', 1, 3, '2018-03-01 20:19:18'),
(47, 'propagate_seeds', 1, 3, '2018-03-01 20:23:45'),
(48, 'germinate_seeds', 1, 3, '2018-03-15 19:26:35'),
(49, 'germinate_seeds', 1, 3, '2018-03-17 19:27:44'),
(50, 'destroy_material', 1, 3, '2018-04-02 19:33:46'),
(51, 'destroy_material', 1, 3, '2018-05-01 19:35:23'),
(52, 'harvest_plants', 1, 3, '2018-05-15 19:36:47'),
(53, 'harvest_plants', 1, 3, '2018-05-18 19:37:47'),
(54, 'destroy_material', 1, 3, '2018-05-18 19:39:36'),
(55, 'complete_drying', 1, 3, '2018-06-01 19:47:17'),
(56, 'create_batch', 1, 1, '2018-04-01 19:52:28'),
(57, 'propagate_cuttings', 1, 1, '2018-04-01 19:52:28'),
(58, 'propagate_cuttings', 1, 1, '2018-04-01 19:52:28'),
(59, 'destroy_material', 1, 3, '2018-05-15 19:56:59'),
(60, 'harvest_plants', 1, 3, '2018-05-16 19:59:05'),
(61, 'destroy_material', 1, 3, '2018-05-26 20:00:12'),
(62, 'complete_oil_extraction', 1, 3, '2018-06-01 12:27:02'),
(65, 'lab_sample_sent', 1, 3, '2018-06-11 17:51:50'),
(76, 'lab_result_received', 1, 3, '2018-06-19 18:54:04');

-- --------------------------------------------------------

--
-- Table structure for table `activities_meta`
--

DROP TABLE IF EXISTS `activities_meta`;
CREATE TABLE IF NOT EXISTS `activities_meta` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `activity_id` int(11) NOT NULL,
  `meta_name` varchar(250) NOT NULL,
  `meta_value` text NOT NULL,
  `organization_id` int(11) NOT NULL,
  `created_by` int(11) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `activity_id` (`activity_id`,`meta_name`,`organization_id`) USING BTREE,
  KEY `taxonomy_id` (`activity_id`),
  KEY `created_by` (`created_by`),
  KEY `organization_id` (`organization_id`)
) ENGINE=InnoDB AUTO_INCREMENT=584 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `activities_meta`
--

INSERT INTO `activities_meta` (`id`, `activity_id`, `meta_name`, `meta_value`, `organization_id`, `created_by`, `timestamp`) VALUES
(314, 40, 'strain', 'Hybrid', 1, 1, '2018-06-07 19:09:59'),
(315, 40, 'description', '10 packages of 50 seeds', 1, 1, '2018-06-07 19:09:59'),
(316, 40, 'date_received', '2018-06-07', 1, 1, '2018-06-07 19:09:59'),
(317, 40, 'received_from_person', 'Personable Salesperson', 1, 1, '2018-06-07 19:09:59'),
(318, 40, 'intended_use', 'Planting for sale', 1, 1, '2018-06-07 19:09:59'),
(319, 40, 'to_inventory_id', '23', 1, 1, '2018-06-07 19:09:59'),
(320, 40, 'received_at_address', '123 Woody Lane, Montreal QC A2C 4F6', 1, 1, '2018-06-07 19:09:59'),
(321, 40, 'to_qty_unit', 'seeds', 1, 1, '2018-06-07 19:09:59'),
(322, 40, 'substance', 'fresh', 1, 1, '2018-06-07 19:09:59'),
(323, 40, 'proof_of_purchase', 'receipt-2018.png', 1, 1, '2018-06-07 19:09:59'),
(324, 40, 'upload_id', '6', 1, 1, '2018-06-07 19:09:59'),
(325, 40, 'to_qty', '500', 1, 1, '2018-06-07 19:09:59'),
(326, 40, 'brand', 'Test Brand', 1, 1, '2018-06-07 19:09:59'),
(327, 40, 'variety', 'Cotton Candy Kush', 1, 1, '2018-06-07 19:09:59'),
(328, 41, 'strain', 'Indica', 1, 1, '2018-06-07 19:13:58'),
(329, 41, 'description', 'Plants in 50 lots of 10', 1, 1, '2018-06-07 19:13:58'),
(330, 41, 'date_received', '2018-06-07', 1, 1, '2018-06-07 19:13:58'),
(331, 41, 'received_from_person', 'Great Northern Seed Company', 1, 1, '2018-06-07 19:13:58'),
(332, 41, 'intended_use', 'Propagation', 1, 1, '2018-06-07 19:13:58'),
(333, 41, 'to_inventory_id', '24', 1, 1, '2018-06-07 19:13:58'),
(334, 41, 'received_at_address', '123 N Rd, Townville, SK h1h3k4', 1, 1, '2018-06-07 19:13:58'),
(335, 41, 'to_qty_unit', 'plants', 1, 1, '2018-06-07 19:13:58'),
(336, 41, 'substance', 'fresh', 1, 1, '2018-06-07 19:13:58'),
(337, 41, 'proof_of_purchase', 'receipt-2018.png', 1, 1, '2018-06-07 19:13:58'),
(338, 41, 'upload_id', '7', 1, 1, '2018-06-07 19:13:58'),
(339, 41, 'to_qty', '500', 1, 1, '2018-06-07 19:13:58'),
(340, 41, 'brand', 'Frozen Buds', 1, 1, '2018-06-07 19:13:58'),
(341, 41, 'variety', 'Romulan', 1, 1, '2018-06-07 19:13:58'),
(342, 42, 'to_inventory_id', '25', 1, 1, '2018-06-07 19:15:53'),
(343, 42, 'to_qty', '1', 1, 1, '2018-06-07 19:15:53'),
(344, 42, 'from_inventory_id', '23', 1, 1, '2018-06-07 19:15:53'),
(345, 42, 'from_qty', '1', 1, 1, '2018-06-07 19:15:53'),
(346, 42, 'variety', 'Cotton Candy Kush', 1, 1, '2018-06-07 19:15:53'),
(347, 42, 'to_qty_unit', 'seeds', 1, 1, '2018-06-07 19:15:53'),
(348, 42, 'from_qty_unit', 'seeds', 1, 1, '2018-06-07 19:15:53'),
(349, 42, 'strain', 'Hybrid', 1, 1, '2018-06-07 19:15:53'),
(350, 43, 'to_inventory_id', '26', 1, 1, '2018-06-07 19:15:56'),
(351, 43, 'to_qty', '1', 1, 1, '2018-06-07 19:15:56'),
(352, 43, 'from_inventory_id', '23', 1, 1, '2018-06-07 19:15:56'),
(353, 43, 'from_qty', '1', 1, 1, '2018-06-07 19:15:56'),
(354, 43, 'variety', 'Cotton Candy Kush', 1, 1, '2018-06-07 19:15:56'),
(355, 43, 'to_qty_unit', 'seeds', 1, 1, '2018-06-07 19:15:56'),
(356, 43, 'from_qty_unit', 'seeds', 1, 1, '2018-06-07 19:15:56'),
(357, 43, 'strain', 'Hybrid', 1, 1, '2018-06-07 19:15:56'),
(358, 44, 'to_inventory_id', '27', 1, 1, '2018-06-07 19:16:13'),
(359, 44, 'to_qty', '1', 1, 1, '2018-06-07 19:16:13'),
(360, 44, 'from_inventory_id', '24', 1, 1, '2018-06-07 19:16:13'),
(361, 44, 'from_qty', '1', 1, 1, '2018-06-07 19:16:13'),
(362, 44, 'variety', 'Romulan', 1, 1, '2018-06-07 19:16:13'),
(363, 44, 'to_qty_unit', 'plants', 1, 1, '2018-06-07 19:16:13'),
(364, 44, 'from_qty_unit', 'plants', 1, 1, '2018-06-07 19:16:13'),
(365, 44, 'strain', 'Indica', 1, 1, '2018-06-07 19:16:13'),
(366, 45, 'to_inventory_id', '28', 1, 1, '2018-06-07 19:16:15'),
(367, 45, 'to_qty', '1', 1, 1, '2018-06-07 19:16:15'),
(368, 45, 'from_inventory_id', '24', 1, 1, '2018-06-07 19:16:15'),
(369, 45, 'from_qty', '1', 1, 1, '2018-06-07 19:16:15'),
(370, 45, 'variety', 'Romulan', 1, 1, '2018-06-07 19:16:15'),
(371, 45, 'to_qty_unit', 'plants', 1, 1, '2018-06-07 19:16:15'),
(372, 45, 'from_qty_unit', 'plants', 1, 1, '2018-06-07 19:16:15'),
(373, 45, 'strain', 'Indica', 1, 1, '2018-06-07 19:16:15'),
(374, 46, 'variety', 'Cotton Candy Kush', 1, 3, '2018-06-07 19:19:18'),
(375, 46, 'strain', 'Hybrid', 1, 3, '2018-06-07 19:19:18'),
(376, 46, 'inventory_id', '29', 1, 3, '2018-06-07 19:19:18'),
(377, 47, 'to_qty', '100', 1, 3, '2018-06-07 19:23:45'),
(378, 47, 'from_inventory_id', '23', 1, 3, '2018-06-07 19:23:45'),
(379, 47, 'variety', 'Cotton Candy Kush', 1, 3, '2018-06-07 19:23:45'),
(380, 47, 'from_qty', '100', 1, 3, '2018-06-07 19:23:45'),
(381, 47, 'to_inventory_id', '29', 1, 3, '2018-06-07 19:23:45'),
(382, 47, 'to_qty_unit', 'seeds', 1, 3, '2018-06-07 19:23:45'),
(383, 47, 'from_qty_unit', 'seeds', 1, 3, '2018-06-07 19:23:45'),
(384, 47, 'strain', 'Hybrid', 1, 3, '2018-06-07 19:23:45'),
(385, 48, 'to_qty', '40', 1, 3, '2018-06-07 19:26:35'),
(386, 48, 'from_inventory_id', '29', 1, 3, '2018-06-07 19:26:35'),
(387, 48, 'from_qty', '40', 1, 3, '2018-06-07 19:26:35'),
(388, 48, 'to_inventory_id', '29', 1, 3, '2018-06-07 19:26:35'),
(389, 48, 'to_qty_unit', 'plants', 1, 3, '2018-06-07 19:26:35'),
(390, 48, 'from_qty_unit', 'seeds', 1, 3, '2018-06-07 19:26:35'),
(391, 49, 'to_qty', '60', 1, 3, '2018-06-07 19:27:44'),
(392, 49, 'from_inventory_id', '29', 1, 3, '2018-06-07 19:27:44'),
(393, 49, 'from_qty', '60', 1, 3, '2018-06-07 19:27:44'),
(394, 49, 'to_inventory_id', '29', 1, 3, '2018-06-07 19:27:44'),
(395, 49, 'to_qty_unit', 'plants', 1, 3, '2018-06-07 19:27:44'),
(396, 49, 'from_qty_unit', 'seeds', 1, 3, '2018-06-07 19:27:44'),
(397, 50, 'from_qty', '20', 1, 3, '2018-06-07 19:33:46'),
(398, 50, 'destroyed_qty', '2000', 1, 3, '2018-06-07 19:33:46'),
(399, 50, 'from_qty_unit', 'plants', 1, 3, '2018-06-07 19:33:46'),
(400, 50, 'witness_qualification_1', 'Expert checker', 1, 3, '2018-06-07 19:33:46'),
(401, 50, 'from_inventory_id', '29', 1, 3, '2018-06-07 19:33:46'),
(402, 50, 'destroyed_at_location', '123 Woodstock Lane', 1, 3, '2018-06-07 19:33:46'),
(403, 50, 'witness_name_1', 'Mr Checkers', 1, 3, '2018-06-07 19:33:46'),
(404, 50, 'destroyed_qty_unit', 'g-wet', 1, 3, '2018-06-07 19:33:46'),
(405, 50, 'witness_name_2', 'Chad Dicey', 1, 3, '2018-06-07 19:33:46'),
(406, 50, 'witness_qualification_2', 'Never risky with Chad', 1, 3, '2018-06-07 19:33:46'),
(407, 51, 'from_qty', '5', 1, 3, '2018-06-07 19:35:23'),
(408, 51, 'destroyed_qty', '500', 1, 3, '2018-06-07 19:35:23'),
(409, 51, 'from_qty_unit', 'plants', 1, 3, '2018-06-07 19:35:23'),
(410, 51, 'witness_qualification_1', 'Expert checker', 1, 3, '2018-06-07 19:35:23'),
(411, 51, 'from_inventory_id', '29', 1, 3, '2018-06-07 19:35:23'),
(412, 51, 'destroyed_at_location', '123 Woodstock Lane', 1, 3, '2018-06-07 19:35:23'),
(413, 51, 'witness_name_1', 'Mr Checkers', 1, 3, '2018-06-07 19:35:23'),
(414, 51, 'destroyed_qty_unit', 'g-wet', 1, 3, '2018-06-07 19:35:23'),
(415, 51, 'witness_name_2', 'Chad Dicey', 1, 3, '2018-06-07 19:35:23'),
(416, 51, 'witness_qualification_2', 'Never risky with Chad', 1, 3, '2018-06-07 19:35:23'),
(417, 52, 'to_qty', '5000', 1, 3, '2018-06-07 19:36:47'),
(418, 52, 'from_inventory_id', '29', 1, 3, '2018-06-07 19:36:47'),
(419, 52, 'from_qty', '50', 1, 3, '2018-06-07 19:36:47'),
(420, 52, 'to_inventory_id', '29', 1, 3, '2018-06-07 19:36:47'),
(421, 52, 'to_qty_unit', 'g-wet', 1, 3, '2018-06-07 19:36:47'),
(422, 52, 'from_qty_unit', 'plants', 1, 3, '2018-06-07 19:36:47'),
(423, 53, 'to_qty', '2500', 1, 3, '2018-06-07 19:37:47'),
(424, 53, 'from_inventory_id', '29', 1, 3, '2018-06-07 19:37:47'),
(425, 53, 'from_qty', '25', 1, 3, '2018-06-07 19:37:47'),
(426, 53, 'to_inventory_id', '29', 1, 3, '2018-06-07 19:37:47'),
(427, 53, 'to_qty_unit', 'g-wet', 1, 3, '2018-06-07 19:37:47'),
(428, 53, 'from_qty_unit', 'plants', 1, 3, '2018-06-07 19:37:47'),
(429, 54, 'from_qty', '3000', 1, 3, '2018-06-07 19:39:36'),
(430, 54, 'destroyed_qty', '500', 1, 3, '2018-06-07 19:39:36'),
(431, 54, 'from_qty_unit', 'g-wet', 1, 3, '2018-06-07 19:39:36'),
(432, 54, 'witness_qualification_1', 'Expert checker', 1, 3, '2018-06-07 19:39:36'),
(433, 54, 'from_inventory_id', '29', 1, 3, '2018-06-07 19:39:36'),
(434, 54, 'destroyed_at_location', '123 Woodstock Lane', 1, 3, '2018-06-07 19:39:36'),
(435, 54, 'witness_name_1', 'Mr Checkers', 1, 3, '2018-06-07 19:39:36'),
(436, 54, 'destroyed_qty_unit', 'g-wet', 1, 3, '2018-06-07 19:39:36'),
(437, 54, 'witness_name_2', 'Chad Dicey', 1, 3, '2018-06-07 19:39:36'),
(438, 54, 'witness_qualification_2', 'Never risky with Chad', 1, 3, '2018-06-07 19:39:36'),
(439, 55, 'to_qty', '900', 1, 3, '2018-06-07 19:47:17'),
(440, 55, 'from_inventory_id', '29', 1, 3, '2018-06-07 19:47:17'),
(441, 55, 'from_qty', '4500', 1, 3, '2018-06-07 19:47:17'),
(442, 55, 'to_inventory_id', '29', 1, 3, '2018-06-07 19:47:17'),
(443, 55, 'to_qty_unit', 'g-dry', 1, 3, '2018-06-07 19:47:17'),
(444, 55, 'from_qty_unit', 'g-wet', 1, 3, '2018-06-07 19:47:17'),
(445, 56, 'variety', 'Romulan', 1, 1, '2018-06-07 19:52:28'),
(446, 56, 'strain', 'Indica', 1, 1, '2018-06-07 19:52:28'),
(447, 56, 'inventory_id', '30', 1, 1, '2018-06-07 19:52:28'),
(448, 57, 'to_qty', '80', 1, 1, '2018-06-07 19:52:28'),
(449, 57, 'from_inventory_id', '27', 1, 1, '2018-06-07 19:52:28'),
(450, 57, 'variety', 'Romulan', 1, 1, '2018-06-07 19:52:28'),
(451, 57, 'source_count', '1', 1, 1, '2018-06-07 19:52:28'),
(452, 57, 'to_inventory_id', '30', 1, 1, '2018-06-07 19:52:28'),
(453, 57, 'to_qty_unit', 'plants', 1, 1, '2018-06-07 19:52:28'),
(454, 57, 'strain', 'Indica', 1, 1, '2018-06-07 19:52:28'),
(455, 58, 'to_qty', '120', 1, 1, '2018-06-07 19:52:28'),
(456, 58, 'from_inventory_id', '28', 1, 1, '2018-06-07 19:52:28'),
(457, 58, 'variety', 'Romulan', 1, 1, '2018-06-07 19:52:28'),
(458, 58, 'source_count', '1', 1, 1, '2018-06-07 19:52:28'),
(459, 58, 'to_inventory_id', '30', 1, 1, '2018-06-07 19:52:28'),
(460, 58, 'to_qty_unit', 'plants', 1, 1, '2018-06-07 19:52:28'),
(461, 58, 'strain', 'Indica', 1, 1, '2018-06-07 19:52:28'),
(462, 59, 'from_qty', '30', 1, 3, '2018-06-07 19:56:59'),
(463, 59, 'destroyed_qty', '3000', 1, 3, '2018-06-07 19:56:59'),
(464, 59, 'from_qty_unit', 'plants', 1, 3, '2018-06-07 19:56:59'),
(465, 59, 'witness_qualification_1', 'Expert checker', 1, 3, '2018-06-07 19:56:59'),
(466, 59, 'from_inventory_id', '30', 1, 3, '2018-06-07 19:56:59'),
(467, 59, 'destroyed_at_location', '123 Woodstock Lane', 1, 3, '2018-06-07 19:56:59'),
(468, 59, 'witness_name_1', 'Mr Checkers', 1, 3, '2018-06-07 19:56:59'),
(469, 59, 'destroyed_qty_unit', 'g-wet', 1, 3, '2018-06-07 19:56:59'),
(470, 59, 'witness_name_2', 'Chad Dicey', 1, 3, '2018-06-07 19:56:59'),
(471, 59, 'witness_qualification_2', 'Never risky with Chad', 1, 3, '2018-06-07 19:56:59'),
(472, 60, 'to_qty', '1700', 1, 3, '2018-06-07 19:59:05'),
(473, 60, 'from_inventory_id', '30', 1, 3, '2018-06-07 19:59:05'),
(474, 60, 'from_qty', '170', 1, 3, '2018-06-07 19:59:05'),
(475, 60, 'to_inventory_id', '30', 1, 3, '2018-06-07 19:59:05'),
(476, 60, 'to_qty_unit', 'g-wet', 1, 3, '2018-06-07 19:59:05'),
(477, 60, 'from_qty_unit', 'plants', 1, 3, '2018-06-07 19:59:05'),
(478, 61, 'from_qty', '1000', 1, 3, '2018-06-07 20:00:12'),
(479, 61, 'destroyed_qty', '3000', 1, 3, '2018-06-07 20:00:12'),
(480, 61, 'from_qty_unit', 'g-wet', 1, 3, '2018-06-07 20:00:12'),
(481, 61, 'witness_qualification_1', 'Expert checker', 1, 3, '2018-06-07 20:00:12'),
(482, 61, 'from_inventory_id', '30', 1, 3, '2018-06-07 20:00:12'),
(483, 61, 'destroyed_at_location', '123 Woodstock Lane', 1, 3, '2018-06-07 20:00:12'),
(484, 61, 'witness_name_1', 'Mr Checkers', 1, 3, '2018-06-07 20:00:12'),
(485, 61, 'destroyed_qty_unit', 'g-wet', 1, 3, '2018-06-07 20:00:12'),
(486, 61, 'witness_name_2', 'Chad Dicey', 1, 3, '2018-06-07 20:00:12'),
(487, 61, 'witness_qualification_2', 'Never risky with Chad', 1, 3, '2018-06-07 20:00:12'),
(488, 62, 'to_qty', '140', 1, 3, '2018-06-07 20:02:17'),
(489, 62, 'from_inventory_id', '30', 1, 3, '2018-06-07 20:02:17'),
(490, 62, 'from_qty', '700', 1, 3, '2018-06-07 20:02:17'),
(491, 62, 'to_inventory_id', '30', 1, 3, '2018-06-07 20:02:17'),
(492, 62, 'to_qty_unit', 'ml', 1, 3, '2018-06-08 12:27:34'),
(493, 62, 'from_qty_unit', 'g-wet', 1, 3, '2018-06-07 20:02:17'),
(509, 65, 'from_inventory_id', '29', 1, 3, '2018-06-11 17:51:50'),
(510, 65, 'from_qty', '75', 1, 3, '2018-06-11 17:51:50'),
(511, 65, 'from_qty_unit', 'g-dry', 1, 3, '2018-06-11 17:51:50'),
(581, 76, 'lab_result', 'passed', 1, 3, '2018-06-19 18:54:04'),
(582, 76, 'lab_sample_sent_activity_id', '65', 1, 3, '2018-06-19 18:54:04'),
(583, 76, 'inventory_id', '29', 1, 3, '2018-06-19 18:54:04');

-- --------------------------------------------------------

--
-- Table structure for table `clients`
--

DROP TABLE IF EXISTS `clients`;
CREATE TABLE IF NOT EXISTS `clients` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `organization_id` int(11) NOT NULL,
  `created_by` int(11) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `organization_id` (`organization_id`,`name`) USING BTREE,
  KEY `created_by` (`created_by`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `clients_meta`
--

DROP TABLE IF EXISTS `clients_meta`;
CREATE TABLE IF NOT EXISTS `clients_meta` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `client_id` int(11) NOT NULL,
  `meta_name` varchar(250) NOT NULL,
  `meta_value` text NOT NULL,
  `organization_id` int(11) NOT NULL,
  `created_by` int(11) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `client_id_2` (`client_id`,`meta_name`,`organization_id`) USING BTREE,
  KEY `created_by` (`created_by`),
  KEY `organization_id` (`organization_id`),
  KEY `client_id` (`client_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `inventories`
--

DROP TABLE IF EXISTS `inventories`;
CREATE TABLE IF NOT EXISTS `inventories` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `organization_id` int(11) NOT NULL,
  `created_by` int(11) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `organization_id` (`organization_id`),
  KEY `created_by` (`created_by`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `inventories`
--

INSERT INTO `inventories` (`id`, `name`, `organization_id`, `created_by`, `timestamp`) VALUES
(23, 'Hybrid Cotton Candy Kush seeds', 1, 1, '2018-01-01 20:09:59'),
(24, 'Indica Romulan plants', 1, 1, '2018-01-15 20:13:58'),
(25, 'Hybrid Cotton Candy Kush Mother', 1, 1, '2018-02-01 20:15:53'),
(26, 'Hybrid Cotton Candy Kush Mother', 1, 1, '2018-02-03 20:15:56'),
(27, 'Indica Romulan Mother', 1, 1, '2018-02-15 20:16:13'),
(28, 'Indica Romulan Mother', 1, 1, '2018-02-16 20:16:15'),
(29, '2018-03-Cotton Candy Kush', 1, 3, '2018-03-01 20:21:27'),
(30, '2018-23-Romulan', 1, 1, '2018-04-01 19:52:28');

-- --------------------------------------------------------

--
-- Table structure for table `inventories_meta`
--

DROP TABLE IF EXISTS `inventories_meta`;
CREATE TABLE IF NOT EXISTS `inventories_meta` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `inventory_id` int(11) NOT NULL,
  `meta_name` varchar(250) NOT NULL,
  `meta_value` text NOT NULL,
  `organization_id` int(11) NOT NULL,
  `created_by` int(11) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `inventory_id` (`inventory_id`,`meta_name`,`organization_id`),
  KEY `taxonomy_id` (`inventory_id`),
  KEY `created_by` (`created_by`),
  KEY `organization_id` (`organization_id`)
) ENGINE=InnoDB AUTO_INCREMENT=91 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `inventories_meta`
--

INSERT INTO `inventories_meta` (`id`, `inventory_id`, `meta_name`, `meta_value`, `organization_id`, `created_by`, `timestamp`) VALUES
(67, 23, 'strain', 'Hybrid', 1, 1, '2018-06-07 19:09:59'),
(68, 23, 'variety', 'Cotton Candy Kush', 1, 1, '2018-06-07 19:09:59'),
(69, 23, 'type', 'received inventory', 1, 1, '2018-06-07 19:09:59'),
(70, 24, 'strain', 'Indica', 1, 1, '2018-06-07 19:13:58'),
(71, 24, 'variety', 'Romulan', 1, 1, '2018-06-07 19:13:58'),
(72, 24, 'type', 'received inventory', 1, 1, '2018-06-07 19:13:58'),
(73, 25, 'strain', 'Hybrid', 1, 1, '2018-06-07 19:15:53'),
(74, 25, 'variety', 'Cotton Candy Kush', 1, 1, '2018-06-07 19:15:53'),
(75, 25, 'type', 'mother', 1, 1, '2018-06-07 19:15:53'),
(76, 26, 'strain', 'Hybrid', 1, 1, '2018-06-07 19:15:56'),
(77, 26, 'variety', 'Cotton Candy Kush', 1, 1, '2018-06-07 19:15:56'),
(78, 26, 'type', 'mother', 1, 1, '2018-06-07 19:15:56'),
(79, 27, 'strain', 'Indica', 1, 1, '2018-06-07 19:16:13'),
(80, 27, 'variety', 'Romulan', 1, 1, '2018-06-07 19:16:13'),
(81, 27, 'type', 'mother', 1, 1, '2018-06-07 19:16:13'),
(82, 28, 'strain', 'Indica', 1, 1, '2018-06-07 19:16:15'),
(83, 28, 'variety', 'Romulan', 1, 1, '2018-06-07 19:16:15'),
(84, 28, 'type', 'mother', 1, 1, '2018-06-07 19:16:15'),
(85, 29, 'variety', 'Cotton Candy Kush', 1, 3, '2018-06-07 19:19:18'),
(86, 29, 'strain', 'Hybrid', 1, 3, '2018-06-07 19:19:18'),
(87, 29, 'type', 'batch', 1, 3, '2018-06-07 19:19:18'),
(88, 30, 'variety', 'Romulan', 1, 1, '2018-06-07 19:52:28'),
(89, 30, 'strain', 'Indica', 1, 1, '2018-06-07 19:52:28'),
(90, 30, 'type', 'batch', 1, 1, '2018-06-07 19:52:28');

-- --------------------------------------------------------

--
-- Table structure for table `organizations`
--

DROP TABLE IF EXISTS `organizations`;
CREATE TABLE IF NOT EXISTS `organizations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `created_by` int(11) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `created_by` (`created_by`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `organizations`
--

INSERT INTO `organizations` (`id`, `name`, `created_by`, `timestamp`) VALUES
(1, 'Wilcompute Growers', 1, '2018-03-27 14:58:37'),
(2, 'Demo Growers', 1, '2018-04-09 13:37:26');

-- --------------------------------------------------------

--
-- Table structure for table `organizations_meta`
--

DROP TABLE IF EXISTS `organizations_meta`;
CREATE TABLE IF NOT EXISTS `organizations_meta` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `organization_id` int(11) NOT NULL,
  `meta_name` varchar(250) NOT NULL,
  `meta_value` text NOT NULL,
  `created_by` int(11) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `organization_id` (`organization_id`,`meta_name`),
  KEY `created_by` (`created_by`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
CREATE TABLE IF NOT EXISTS `products` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `organization_id` int(11) NOT NULL,
  `created_by` int(11) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `organization_id` (`organization_id`,`name`),
  KEY `created_by` (`created_by`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `products_meta`
--

DROP TABLE IF EXISTS `products_meta`;
CREATE TABLE IF NOT EXISTS `products_meta` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `product_id` int(11) NOT NULL,
  `meta_name` varchar(250) NOT NULL,
  `meta_value` text NOT NULL,
  `organization_id` int(11) NOT NULL,
  `created_by` int(11) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `product_id` (`product_id`,`meta_name`,`organization_id`),
  KEY `taxonomy_id` (`product_id`),
  KEY `created_by` (`created_by`),
  KEY `organization_id` (`organization_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
CREATE TABLE IF NOT EXISTS `roles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `organization_id` int(11) NOT NULL,
  `created_by` int(11) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_roles_per_org` (`name`,`organization_id`),
  KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `roles`
--

INSERT INTO `roles` (`id`, `name`, `organization_id`, `created_by`, `timestamp`) VALUES
(1, 'admin', 1, 3, '2018-04-24 15:23:33'),
(2, 'admin2', 2, 1, '2018-04-09 13:40:54'),
(3, 'staff', 1, 1, '2018-04-04 18:18:27');

-- --------------------------------------------------------

--
-- Table structure for table `roles_meta`
--

DROP TABLE IF EXISTS `roles_meta`;
CREATE TABLE IF NOT EXISTS `roles_meta` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `role_id` int(11) NOT NULL,
  `meta_name` varchar(250) NOT NULL,
  `meta_value` text NOT NULL,
  `organization_id` int(11) NOT NULL,
  `created_by` int(11) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_meta_per_role` (`role_id`,`meta_name`),
  KEY `created_by` (`created_by`),
  KEY `organization_id` (`organization_id`),
  KEY `role_id` (`role_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `roles_meta`
--

INSERT INTO `roles_meta` (`id`, `role_id`, `meta_name`, `meta_value`, `organization_id`, `created_by`, `timestamp`) VALUES
(1, 1, 'permissions', '[\n	{\n		\"methods\" : [\n			\"GET\",\n			\"POST\",\n			\"PATCH\"\n		],\n		\"object\" : \"users\"\n	},\n	{\n		\"methods\" : [\n			\"POST\"\n		],\n		\"object\" : \"uploads\"\n	},\n	{\n		\"methods\" : [\n			\"GET\",\n			\"POST\",\n			\"PATCH\"\n		],\n		\"object\" : \"clients\"\n	},\n	{\n		\"methods\" : [\n			\"GET\",\n			\"POST\",\n			\"DELETE\",\n			\"PATCH\"\n		],\n		\"object\" : \"taxonomies\"\n	},\n	{\n		\"methods\" : [\n			\"GET\",\n			\"POST\",\n			\"DELETE\",\n			\"PATCH\"\n		],\n		\"object\" : \"taxonomy_options\"\n	},\n	{\n		\"methods\" : [\n			\"GET\",\n			\"POST\",\n			\"PATCH\"\n		],\n		\"object\" : \"inventories\"\n	},\n	{\n		\"methods\" : [\n			\"GET\",\n			\"POST\",\n			\"PATCH\"\n		],\n		\"object\" : \"products\"\n	},\n	{\n		\"methods\" : [\n			\"GET\",\n			\"POST\",\n			\"DELETE\",\n			\"PATCH\"\n		],\n		\"object\" : \"roles\"\n	},\n	{\n		\"methods\" : [\n			\"GET\",\n			\"POST\",\n			\"DELETE\",\n			\"PATCH\"\n		],\n		\"object\" : \"rooms\"\n	},\n	{\n		\"methods\" : [\n			\"GET\",\n			\"POST\",\n			\"DELETE\",\n			\"PATCH\"\n		],\n		\"object\" : \"rules\"\n	},\n	{\n		\"methods\" : [\n			\"GET\"\n		],\n		\"object\" : \"activities\"\n	},\n	{\n		\"action\" : \"receive_inventory\"\n	},\n	{\n		\"action\" : \"create_batch\"\n	},\n	{\n		\"action\" : \"transfer_inventory\"\n	},\n	{\n		\"action\" : \"create_mother\"\n	},\n	{\n		\"action\" : \"propagate_cuttings\"\n	},\n	{\n		\"action\" : \"propagate_seeds\"\n	},\n	{\n		\"action\" : \"germinate_seeds\"\n	},\n	{\n		\"action\" : \"destroy_material\"\n	},\n	{\n		\"action\" : \"harvest_plants\"\n	},\n	{\n		\"action\" : \"complete_drying\"\n	},\n	{\n		\"action\" : \"complete_oil_extraction\"\n	},\n	{\n		\"action\" : \"admin_adjustment\"\n	},\n	{\n		\"action\" : \"lab_sample_sent\"\n	},\n	{\n		\"action\" : \"lab_result_received\"\n	}\n]', 1, 3, '2018-06-19 18:47:03'),
(2, 2, 'permissions', '[  {    \"object\": \"users\",    \"methods\": [\"GET\", \"POST\"]  },{      \"object\": \"clients\",      \"methods\": [\"GET\", \"POST\"]  },  {      \"object\": \"taxonomies\",      \"methods\": [\"GET\", \"POST\"]  },{      \"object\": \"inventories\",      \"methods\": [\"GET\", \"POST\"]  },{      \"object\": \"products\",      \"methods\": [\"GET\", \"POST\"]  },{      \"object\": \"roles\",      \"methods\": [\"GET\", \"POST\", \"DELETE\"]  },{      \"object\": \"rules\",      \"methods\": [\"GET\", \"POST\", \"DELETE\"]  }]', 2, 1, '2018-04-09 13:41:10'),
(3, 3, 'permissions', '[\r\n   {\r\n     \"object\": \"users\",\r\n     \"methods\": [\"GET\", \"POST\"]\r\n   },{\r\n       \"object\": \"clients\",\r\n       \"methods\": [\"GET\", \"POST\"]\r\n   },\r\n  {\r\n       \"object\": \"taxonomies\",\r\n       \"methods\": [\"GET\", \"POST\", \"DELETE\"]\r\n   },\r\n  {\r\n       \"object\": \"taxonomy_options\",\r\n       \"methods\": [\"GET\", \"POST\", \"DELETE\"]\r\n   },\r\n \r\n {\r\n       \"object\": \"inventories\",\r\n       \"methods\": [\"GET\", \"POST\"]\r\n   },\r\n {\r\n       \"object\": \"products\",\r\n       \"methods\": [\"GET\", \"POST\"]\r\n   },\r\n {\r\n       \"object\": \"roles\",\r\n       \"methods\": [\"GET\", \"POST\", \"DELETE\"]\r\n   },\r\n   {\r\n     \"object\": \"rooms\",\r\n     \"methods\": [\"GET\", \"POST\", \"DELETE\"]\r\n   },\r\n {\r\n       \"object\": \"rules\",\r\n       \"methods\": [\"GET\", \"POST\", \"DELETE\"]\r\n   }\r\n]', 1, 1, '2018-04-27 19:24:16');

-- --------------------------------------------------------

--
-- Table structure for table `rooms`
--

DROP TABLE IF EXISTS `rooms`;
CREATE TABLE IF NOT EXISTS `rooms` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `organization_id` int(11) NOT NULL,
  `created_by` int(11) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `organization_id` (`organization_id`),
  KEY `created_by` (`created_by`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `rooms`
--

INSERT INTO `rooms` (`id`, `name`, `organization_id`, `created_by`, `timestamp`) VALUES
(1, 'The 401', 1, 3, '2018-05-25 18:08:58');

-- --------------------------------------------------------

--
-- Table structure for table `rooms_meta`
--

DROP TABLE IF EXISTS `rooms_meta`;
CREATE TABLE IF NOT EXISTS `rooms_meta` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `room_id` int(11) NOT NULL,
  `meta_name` varchar(250) NOT NULL,
  `meta_value` text NOT NULL,
  `organization_id` int(11) NOT NULL,
  `created_by` int(11) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `room_id` (`room_id`,`meta_name`,`organization_id`),
  UNIQUE KEY `single meta_name per room` (`room_id`,`meta_name`),
  KEY `created_by` (`created_by`),
  KEY `organization_id` (`organization_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `rooms_meta`
--

INSERT INTO `rooms_meta` (`id`, `room_id`, `meta_name`, `meta_value`, `organization_id`, `created_by`, `timestamp`) VALUES
(1, 1, 'zone', 'outside', 1, 3, '2018-05-25 18:08:58');

-- --------------------------------------------------------

--
-- Table structure for table `rules`
--

DROP TABLE IF EXISTS `rules`;
CREATE TABLE IF NOT EXISTS `rules` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `description` varchar(250) NOT NULL,
  `activity` varchar(50) NOT NULL,
  `conditions` mediumtext NOT NULL,
  `organization_id` int(11) NOT NULL,
  `created_by` int(11) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `organization_id` (`organization_id`),
  KEY `created_by` (`created_by`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `rules`
--

INSERT INTO `rules` (`id`, `name`, `description`, `activity`, `conditions`, `organization_id`, `created_by`, `timestamp`) VALUES
(1, 'Intake, Canada, ACMPR Div. 5, Sec. 152', 'Rules about intake', 'receive_inventory', '[\n	{\n		\"condition_type\" : \"upload_validation\",\n		\"field\" : \"upload_id\"\n	},\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"received_from_person\",\n		\"regex\" : \"[\\\\w\\\\s]+\"\n	},\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"received_at_address\",\n		\"regex\" : \"[\\\\w\\\\-,.\\\\s]+\"\n	},\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"date_received\",\n		\"regex\" : \"(19[0-9]{2}|2[0-9]{3})-(0[1-9]|1[012])-([123]0|[012][1-9]|31)\"\n	},\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"substance\",\n		\"regex\" : \"(fresh|dried|oil|other)\"\n	},\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"to_qty\",\n		\"regex\" : \"([1-9]\\\\d*\\\\.\\\\d*|0?\\\\.\\\\d*[1-9]\\\\d*|[1-9]\\\\d*)\"\n	},\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"to_qty_unit\",\n		\"regex\" : \"(g-dry|g-wet|ml|seeds|plants)\"\n	},\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"brand\",\n		\"regex\" : \"[\\\\w\\\\s]+\"\n	},\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"intended_use\",\n		\"regex\" : \"[\\\\w\\\\s]+\"\n	},\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"description\",\n		\"regex\" : \"[\\\\w\\\\s]+\"\n	},\n	{\n		\"condition_type\" : \"taxonomy_validation\",\n		\"field\" : \"strain\",\n		\"match\" : \"name\",\n		\"taxonomy_name\" : \"strains\"\n	},\n	{\n		\"condition_type\" : \"taxonomy_validation\",\n		\"field\" : \"variety\",\n		\"match\" : \"name\",\n		\"taxonomy_name\" : \"varieties\"\n	}\n]', 1, 1, '2018-05-11 14:51:32'),
(2, 'Create Batch', 'Rule to validate new batch object', 'create_batch', '[\n	{\n		\"condition_type\" : \"taxonomy_validation\",\n		\"field\" : \"variety\",\n		\"match\" : \"name\",\n		\"taxonomy_name\" : \"varieties\"\n	},\n	{\n		\"condition_type\" : \"taxonomy_validation\",\n		\"field\" : \"strain\",\n		\"match\" : \"name\",\n		\"taxonomy_name\" : \"strains\"\n	}\n]', 1, 1, '2018-05-11 15:28:56'),
(3, 'Transfer Batch', 'Rule to validate transfer between inventory types', 'transfer_inventory', '[\n	{\n		\"condition_type\" : \"inventory_match\",\n		\"inventory_id_field\" : \"from_inventory_id\",\n		\"match_fields\" : [\n			{\n				\"field\" : \"variety\",\n				\"match\" : \"variety\"\n			},\n			{\n				\"field\" : \"strain\",\n				\"match\" : \"strain\"\n			}\n		]\n	},\n	{\n		\"condition_type\" : \"inventory_match\",\n		\"inventory_id_field\" : \"to_inventory_id\",\n		\"match_fields\" : [\n			{\n				\"field\" : \"variety\",\n				\"match\" : \"variety\"\n			},\n			{\n				\"field\" : \"strain\",\n				\"match\" : \"strain\"\n			}\n		]\n	},\n{\n\"condition_type\": \"inventory_count\",\n\"inventory_id\": \"from_inventory_id\",\n\"qty_value\": \"from_qty\",\n\"qty_unit\": \"from_qty_unit\"\n}\n]', 1, 1, '2018-04-30 19:37:06'),
(4, 'Create Mother', 'Rule to validate creating mother(s)', 'create_mother', '[\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"from_qty_unit\",\n		\"regex\" : \"(seeds|plants)\"\n	},\n   {\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"to_qty_unit\",\n		\"regex\" : \"(seeds|plants)\"\n	},\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"from_qty\",\n		\"regex\" : \"1\"\n	},\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"to_qty\",\n		\"regex\" : \"1\"\n	},\n	{\n		\"condition_type\" : \"taxonomy_validation\",\n		\"field\" : \"strain\",\n		\"match\" : \"name\",\n		\"taxonomy_name\" : \"strains\"\n	},\n	{\n		\"condition_type\" : \"taxonomy_validation\",\n		\"field\" : \"variety\",\n		\"match\" : \"name\",\n		\"taxonomy_name\" : \"varieties\"\n	},\n	{\n		\"condition_type\" : \"inventory_match\",\n		\"inventory_id_field\" : \"from_inventory_id\",\n		\"match_fields\" : [\n			{\n				\"field\" : \"variety\",\n				\"match\" : \"variety\"\n			},\n			{\n				\"field\" : \"strain\",\n				\"match\" : \"strain\"\n			}\n		]\n	},\n	{\n		\"condition_type\" : \"inventory_count\",\n		\"inventory_id\" : \"from_inventory_id\",\n		\"qty_unit\" : \"from_qty_unit\",\n		\"qty_value\" : \"from_qty\"\n	}\n]', 1, 1, '2018-05-11 17:57:33'),
(5, 'Propagate Cuttings', 'Rule to validate propagating cuttings from a mother plant', 'propagate_cuttings', '[\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"to_qty_unit\",\n		\"regex\" : \"plants\"\n	},\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"to_qty\",\n		\"regex\" : \"[1-9]\\\\d*\"\n	},\n	{\n		\"condition_type\" : \"inventory_match\",\n		\"inventory_id_field\" : \"to_inventory_id\",\n		\"match_fields\" : [\n			{\n				\"match\" : \"type\",\n				\"regex\" : \"batch\"\n			}\n		]\n	},\n	{\n		\"condition_type\" : \"inventory_match\",\n		\"inventory_id_field\" : \"from_inventory_id\",\n		\"match_fields\" : [\n			{\n				\"match\" : \"type\",\n				\"regex\" : \"mother\"\n			}\n		]\n	},\n	{\n		\"condition_type\" : \"inventory_compare\",\n		\"first_inventory_id_field\" : \"to_inventory_id\",\n		\"match_fields\" : [\n			{\n				\"comparison\" : \"=\",\n				\"match\" : \"variety\"\n			}\n		],\n		\"second_inventory_id_field\" : \"from_inventory_id\"\n	},\n	{\n		\"condition_type\" : \"inventory_count\",\n		\"inventory_id\" : \"from_inventory_id\",\n		\"qty_unit\" : \"to_qty_unit\",\n		\"qty_value\" : \"source_count\"\n	}\n]', 1, 1, '2018-06-18 17:27:26'),
(6, 'Propagate Seeds', 'Validate propagating seeds from received_inventory to a batch', 'propagate_seeds', '[\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"to_qty_unit\",\n		\"regex\" : \"seeds\"\n	},\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"from_qty_unit\",\n		\"regex\" : \"seeds\"\n	},\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"to_qty\",\n		\"regex\" : \"[1-9]\\\\d*\"\n	},\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"from_qty\",\n		\"regex\" : \"[1-9]\\\\d*\"\n	},\n	{\n		\"condition_type\" : \"inventory_match\",\n		\"inventory_id_field\" : \"to_inventory_id\",\n		\"match_fields\" : [\n			{\n				\"match\" : \"type\",\n				\"regex\" : \"batch\"\n			}\n		]\n	},\n	{\n		\"condition_type\" : \"inventory_match\",\n		\"inventory_id_field\" : \"from_inventory_id\",\n		\"match_fields\" : [\n			{\n				\"match\" : \"type\",\n				\"regex\" : \"received inventory\"\n			}\n		]\n	},\n	{\n		\"condition_type\" : \"inventory_compare\",\n		\"first_inventory_id_field\" : \"to_inventory_id\",\n		\"match_fields\" : [\n			{\n				\"comparison\" : \"=\",\n				\"match\" : \"variety\"\n			}\n		],\n		\"second_inventory_id_field\" : \"from_inventory_id\"\n	},\n	{\n		\"condition_type\" : \"inventory_count\",\n		\"inventory_id\" : \"from_inventory_id\",\n		\"qty_unit\" : \"from_qty_unit\",\n		\"qty_value\" : \"from_qty\"\n	}\n]', 1, 1, '2018-06-18 17:34:56'),
(7, 'Germinate Seeds', 'Validate germinating seeds into plants', 'germinate_seeds', '[\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"to_qty_unit\",\n		\"regex\" : \"plants\"\n	},\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"from_qty_unit\",\n		\"regex\" : \"seeds\"\n	},\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"to_qty\",\n		\"regex\" : \"\\\\d+\"\n	},\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"from_qty\",\n		\"regex\" : \"\\\\d+\"\n	},\n	{\n		\"condition_type\" : \"inventory_count\",\n		\"inventory_id\" : \"from_inventory_id\",\n		\"qty_unit\" : \"from_qty_unit\",\n		\"qty_value\" : \"from_qty\"\n	},\n	{\n		\"condition_type\" : \"inventory_match\",\n		\"inventory_id_field\" : \"to_inventory_id\",\n		\"match_fields\" : [\n			{\n				\"match\" : \"type\",\n				\"regex\" : \"(batch|mother)\"\n			}\n		]\n	}\n]', 1, 1, '2018-06-05 18:28:38'),
(8, 'Destroy Material', 'Rule about destroying material', 'destroy_material', '[\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"destroyed_qty\",\n		\"regex\" : \"([0-9]*[.])?[0-9]+\"\n	},\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"destroyed_qty_unit\",\n		\"regex\" : \"g\"\n	},\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"destroyed_at_location\",\n		\"regex\" : \"[\\\\w\\\\-,.\\\\s]+\"\n	},\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"witness_name_1\",\n		\"regex\" : \"[\\\\w\\\\-,.\\\\s]+\"\n	},\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"witness_qualification_1\",\n		\"regex\" : \"[\\\\w\\\\-,.\\\\s]+\"\n	},\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"witness_name_2\",\n		\"regex\" : \"[\\\\w\\\\-,.\\\\s]+\"\n	},\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"witness_qualification_2\",\n		\"regex\" : \"[\\\\w\\\\-,.\\\\s]+\"\n	},\n	{\n		\"condition_type\" : \"conditional_has_field\",\n		\"conditions\" : [\n			{\n				\"condition_type\" : \"inventory_count\",\n				\"inventory_id\" : \"from_inventory_id\",\n				\"qty_unit\" : \"from_qty_unit\",\n				\"qty_value\" : \"from_qty\"\n			}\n		],\n		\"field\" : \"from_qty\"\n	}\n]', 1, 1, '2018-06-18 17:37:45'),
(9, 'Harvest Plants', 'Rule about harvesting plants', 'harvest_plants', '[\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"to_qty_unit\",\n		\"regex\" : \"g-wet\"\n	},\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"from_qty_unit\",\n		\"regex\" : \"plants\"\n	},\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"to_qty\",\n		\"regex\" : \"([0-9]*[.])?[0-9]+\"\n	},\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"from_qty\",\n		\"regex\" : \"\\\\d+\"\n	},\n	{\n		\"condition_type\" : \"inventory_count\",\n		\"inventory_id\" : \"from_inventory_id\",\n		\"qty_unit\" : \"from_qty_unit\",\n		\"qty_value\" : \"from_qty\"\n	},\n	{\n		\"condition_type\" : \"inventory_match\",\n		\"inventory_id_field\" : \"to_inventory_id\",\n		\"match_fields\" : [\n			{\n				\"match\" : \"type\",\n				\"regex\" : \"batch\"\n			}\n		]\n	}\n]', 1, 1, '2018-06-05 18:37:09'),
(10, 'Complete Drying', 'Complete the drying process', 'complete_drying', '[\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"to_qty_unit\",\n		\"regex\" : \"g-dry\"\n	},\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"from_qty_unit\",\n		\"regex\" : \"g-wet\"\n	},\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"to_qty\",\n		\"regex\" : \"([0-9]*[.])?[0-9]+\"\n	},\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"from_qty\",\n		\"regex\" : \"([0-9]*[.])?[0-9]+\"\n	},\n	{\n		\"condition_type\" : \"inventory_count\",\n		\"inventory_id\" : \"from_inventory_id\",\n		\"qty_unit\" : \"from_qty_unit\",\n		\"qty_value\" : \"from_qty\",\n		\"operator\": \"=\"\n	},\n	{\n		\"condition_type\" : \"inventory_match\",\n		\"inventory_id_field\" : \"to_inventory_id\",\n		\"match_fields\" : [\n			{\n				\"match\" : \"type\",\n				\"regex\" : \"batch\"\n			}\n		]\n	}\n]', 1, 1, '2018-06-06 12:21:22'),
(11, 'Complete Oil Extraction', 'Complete the oil extraction process', 'complete_oil_extraction', '[\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"to_qty_unit\",\n		\"regex\" : \"ml\"\n	},\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"from_qty_unit\",\n		\"regex\" : \"g-wet\"\n	},\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"to_qty\",\n		\"regex\" : \"([0-9]*[.])?[0-9]+\"\n	},\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"from_qty\",\n		\"regex\" : \"([0-9]*[.])?[0-9]+\"\n	},\n	{\n		\"condition_type\" : \"inventory_count\",\n		\"inventory_id\" : \"from_inventory_id\",\n		\"operator\" : \"=\",\n		\"qty_unit\" : \"from_qty_unit\",\n		\"qty_value\" : \"from_qty\"\n	},\n	{\n		\"condition_type\" : \"inventory_match\",\n		\"inventory_id_field\" : \"to_inventory_id\",\n		\"match_fields\" : [\n			{\n				\"match\" : \"type\",\n				\"regex\" : \"batch\"\n			}\n		]\n	}\n]', 1, 1, '2018-06-07 16:33:30'),
(12, 'Admin Adjustment', 'Constraint-free activity allowing arbitrary inventory and status adjustments', 'admin_adjustment', '[]', 1, 1, '2018-06-11 04:00:00'),
(13, 'Send Lab Sample', 'Record sending a lab sample', 'lab_sample_sent', '[\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"from_qty_unit\",\n		\"regex\" : \"(g-dry|ml)\"\n	},\n	{\n		\"condition_type\" : \"data_validation\",\n		\"field\" : \"from_qty\",\n		\"regex\" : \"([0-9]*[.])?[0-9]+\"\n	},\n	{\n		\"condition_type\" : \"inventory_count\",\n		\"inventory_id\" : \"from_inventory_id\",\n		\"qty_unit\" : \"from_qty_unit\",\n		\"qty_value\" : \"from_qty\"\n	},\n	{\n		\"condition_type\" : \"inventory_match\",\n		\"inventory_id_field\" : \"from_inventory_id\",\n		\"match_fields\" : [\n			{\n				\"match\" : \"type\",\n				\"regex\" : \"batch\"\n			}\n		]\n	}\n]', 1, 1, '2018-06-11 17:50:12'),
(14, 'Receive Lab Result', 'Record receiving a lab result', 'lab_result_received', '[\n	{\n		\"activity_id_field\" : \"lab_sample_sent_activity_id\",\n		\"condition_type\" : \"activity_match\",\n		\"match_fields\" : [\n			{\n				\"field\" : \"inventory_id\",\n				\"match\" : \"from_inventory_id\"\n			},\n			{\n				\"regex\" : \"lab_sample_sent\",\n				\"match\" : \"name\"\n			}\n		]\n	}\n]', 1, 1, '2018-06-19 18:53:38');

-- --------------------------------------------------------

--
-- Table structure for table `taxonomies`
--

DROP TABLE IF EXISTS `taxonomies`;
CREATE TABLE IF NOT EXISTS `taxonomies` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `organization_id` int(11) NOT NULL,
  `created_by` int(11) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `organization_id` (`organization_id`,`name`),
  KEY `created_by` (`created_by`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8 COMMENT='Refers to the list of objects that will appear in the system';

--
-- Dumping data for table `taxonomies`
--

INSERT INTO `taxonomies` (`id`, `name`, `organization_id`, `created_by`, `timestamp`) VALUES
(1, 'strains', 1, 1, '2018-04-10 15:05:49'),
(2, 'strains', 2, 1, '2018-04-10 15:48:01'),
(3, 'varieties', 1, 3, '2018-04-24 14:48:02');

-- --------------------------------------------------------

--
-- Table structure for table `taxonomy_options`
--

DROP TABLE IF EXISTS `taxonomy_options`;
CREATE TABLE IF NOT EXISTS `taxonomy_options` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `taxonomy_id` int(11) NOT NULL,
  `name` varchar(250) NOT NULL,
  `organization_id` int(11) NOT NULL,
  `created_by` int(11) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique option name per taxonomy` (`taxonomy_id`,`name`) USING BTREE,
  KEY `taxonomy_id` (`taxonomy_id`),
  KEY `created_by` (`created_by`),
  KEY `organization_id` (`organization_id`)
) ENGINE=InnoDB AUTO_INCREMENT=54 DEFAULT CHARSET=utf8 COMMENT='Lists properties of each object in the system';

--
-- Dumping data for table `taxonomy_options`
--

INSERT INTO `taxonomy_options` (`id`, `taxonomy_id`, `name`, `organization_id`, `created_by`, `timestamp`) VALUES
(1, 1, 'Hybrid', 1, 3, '2018-05-25 14:32:54'),
(2, 1, 'Indica', 1, 3, '2018-05-25 14:33:07'),
(3, 1, 'Sativa', 1, 3, '2018-05-25 14:33:17'),
(4, 3, 'Blue Dream', 1, 3, '2018-05-25 14:34:01'),
(5, 3, 'OG Kush', 1, 3, '2018-05-25 14:34:09'),
(6, 3, 'White Widow', 1, 3, '2018-05-25 14:34:17'),
(7, 3, 'Pineapple Express', 1, 3, '2018-05-25 14:34:25'),
(8, 3, 'AK-47', 1, 3, '2018-05-25 14:34:32'),
(9, 3, 'Cherry Pie', 1, 3, '2018-05-25 14:34:39'),
(10, 3, 'Cheese', 1, 3, '2018-05-25 14:34:47'),
(11, 3, 'Platinum GSC', 1, 3, '2018-05-25 14:34:58'),
(12, 3, 'Lemon Kush', 1, 3, '2018-05-25 14:35:06'),
(13, 3, 'Golden Goat', 1, 3, '2018-05-25 14:35:14'),
(14, 3, 'Agent Orange', 1, 3, '2018-05-25 14:35:21'),
(15, 3, 'Mango Kush', 1, 3, '2018-05-25 14:35:27'),
(16, 3, 'Dutch Treat', 1, 3, '2018-05-25 14:35:35'),
(17, 3, 'Bruce Banner', 1, 3, '2018-05-25 14:35:42'),
(18, 3, 'Fire OG', 1, 3, '2018-05-25 14:35:50'),
(19, 3, 'NYC Diesel', 1, 3, '2018-05-25 14:35:55'),
(20, 3, 'Animal Cookies', 1, 3, '2018-05-25 14:36:01'),
(21, 3, 'Cotton Candy Kush', 1, 3, '2018-05-25 14:36:07'),
(22, 3, 'Bubba Kush', 1, 3, '2018-05-25 14:36:29'),
(23, 3, 'Northern Lights', 1, 3, '2018-05-25 14:36:36'),
(24, 3, 'Blue Cheese', 1, 3, '2018-05-25 14:36:44'),
(25, 3, 'Purple Kush', 1, 3, '2018-05-25 14:36:51'),
(26, 3, 'Blueberry', 1, 3, '2018-05-25 14:36:58'),
(27, 3, 'Grape Ape', 1, 3, '2018-05-25 14:37:03'),
(28, 3, 'God\'s Gift', 1, 3, '2018-05-25 14:37:10'),
(29, 3, 'Death Star', 1, 3, '2018-05-25 14:37:16'),
(30, 3, 'LA Confidential', 1, 3, '2018-05-25 14:37:24'),
(31, 3, 'Purple Urkle', 1, 3, '2018-05-25 14:37:31'),
(32, 3, 'Afghan Kush', 1, 3, '2018-05-25 14:37:39'),
(33, 3, 'Hindu Kush', 1, 3, '2018-05-25 14:37:46'),
(34, 3, 'White Rhino', 1, 3, '2018-05-25 14:37:53'),
(35, 3, 'G13', 1, 3, '2018-05-25 14:38:03'),
(36, 3, 'Berry White', 1, 3, '2018-05-25 14:38:09'),
(37, 3, 'Blueberry Kush', 1, 3, '2018-05-25 14:38:15'),
(38, 3, 'Mr. Nice', 1, 3, '2018-05-25 14:38:22'),
(39, 3, 'Romulan', 1, 3, '2018-05-25 14:38:28'),
(40, 3, 'Sour Diesel', 1, 3, '2018-05-25 14:38:44'),
(41, 3, 'Jack Herer', 1, 3, '2018-05-25 14:38:51'),
(42, 3, 'Durban Poison', 1, 3, '2018-05-25 14:38:58'),
(43, 3, 'Lemon Haze', 1, 3, '2018-05-25 14:39:04'),
(44, 3, 'Strawberry Cough', 1, 3, '2018-05-25 14:39:10'),
(45, 3, 'Super Lemon Haze', 1, 3, '2018-05-25 14:39:17'),
(46, 3, 'Amnesia Haze', 1, 3, '2018-05-25 14:39:25'),
(47, 3, 'Harlequin', 1, 3, '2018-05-25 14:39:31'),
(48, 3, 'Purple Haze', 1, 3, '2018-05-25 14:39:39'),
(49, 3, 'Cinex', 1, 3, '2018-05-25 14:39:45'),
(50, 3, 'Candyland', 1, 3, '2018-05-25 14:39:51'),
(51, 3, 'Tangie', 1, 3, '2018-05-25 14:40:04'),
(52, 3, 'Lamb\'s Bread', 1, 3, '2018-05-25 14:40:10'),
(53, 3, 'Ghost Train Haze', 1, 3, '2018-05-25 14:40:18');

-- --------------------------------------------------------

--
-- Table structure for table `taxonomy_options_meta`
--

DROP TABLE IF EXISTS `taxonomy_options_meta`;
CREATE TABLE IF NOT EXISTS `taxonomy_options_meta` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `taxonomy_option_id` int(11) NOT NULL,
  `meta_name` varchar(250) COLLATE utf8_bin NOT NULL,
  `meta_value` text COLLATE utf8_bin NOT NULL,
  `organization_id` int(11) NOT NULL,
  `created_by` int(11) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique meta_name per option per organization` (`taxonomy_option_id`,`meta_name`,`organization_id`),
  KEY `option_id` (`taxonomy_option_id`),
  KEY `created_by` (`created_by`),
  KEY `organization_id` (`organization_id`)
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

--
-- Dumping data for table `taxonomy_options_meta`
--

INSERT INTO `taxonomy_options_meta` (`id`, `taxonomy_option_id`, `meta_name`, `meta_value`, `organization_id`, `created_by`, `timestamp`) VALUES
(1, 4, 'strain', 'Hybrid', 1, 3, '2018-05-25 14:34:01'),
(2, 5, 'strain', 'Hybrid', 1, 3, '2018-05-25 14:34:09'),
(3, 6, 'strain', 'Hybrid', 1, 3, '2018-05-25 14:34:17'),
(4, 7, 'strain', 'Hybrid', 1, 3, '2018-05-25 14:34:25'),
(5, 8, 'strain', 'Hybrid', 1, 3, '2018-05-25 14:34:32'),
(6, 9, 'strain', 'Hybrid', 1, 3, '2018-05-25 14:34:39'),
(7, 10, 'strain', 'Hybrid', 1, 3, '2018-05-25 14:34:47'),
(8, 11, 'strain', 'Hybrid', 1, 3, '2018-05-25 14:34:58'),
(9, 12, 'strain', 'Hybrid', 1, 3, '2018-05-25 14:35:06'),
(10, 13, 'strain', 'Hybrid', 1, 3, '2018-05-25 14:35:14'),
(11, 14, 'strain', 'Hybrid', 1, 3, '2018-05-25 14:35:21'),
(12, 15, 'strain', 'Hybrid', 1, 3, '2018-05-25 14:35:27'),
(13, 16, 'strain', 'Hybrid', 1, 3, '2018-05-25 14:35:35'),
(14, 17, 'strain', 'Hybrid', 1, 3, '2018-05-25 14:35:42'),
(15, 18, 'strain', 'Hybrid', 1, 3, '2018-05-25 14:35:50'),
(16, 19, 'strain', 'Hybrid', 1, 3, '2018-05-25 14:35:55'),
(17, 20, 'strain', 'Hybrid', 1, 3, '2018-05-25 14:36:01'),
(18, 21, 'strain', 'Hybrid', 1, 3, '2018-05-25 14:36:07'),
(19, 22, 'strain', 'Indica', 1, 3, '2018-05-25 14:36:29'),
(20, 23, 'strain', 'Indica', 1, 3, '2018-05-25 14:36:36'),
(21, 24, 'strain', 'Indica', 1, 3, '2018-05-25 14:36:44'),
(22, 25, 'strain', 'Indica', 1, 3, '2018-05-25 14:36:51'),
(23, 26, 'strain', 'Indica', 1, 3, '2018-05-25 14:36:58'),
(24, 27, 'strain', 'Indica', 1, 3, '2018-05-25 14:37:03'),
(25, 28, 'strain', 'Indica', 1, 3, '2018-05-25 14:37:10'),
(26, 29, 'strain', 'Indica', 1, 3, '2018-05-25 14:37:16'),
(27, 30, 'strain', 'Indica', 1, 3, '2018-05-25 14:37:24'),
(28, 31, 'strain', 'Indica', 1, 3, '2018-05-25 14:37:31'),
(29, 32, 'strain', 'Indica', 1, 3, '2018-05-25 14:37:39'),
(30, 33, 'strain', 'Indica', 1, 3, '2018-05-25 14:37:46'),
(31, 34, 'strain', 'Indica', 1, 3, '2018-05-25 14:37:53'),
(32, 35, 'strain', 'Indica', 1, 3, '2018-05-25 14:38:03'),
(33, 36, 'strain', 'Indica', 1, 3, '2018-05-25 14:38:09'),
(34, 37, 'strain', 'Indica', 1, 3, '2018-05-25 14:38:15'),
(35, 38, 'strain', 'Indica', 1, 3, '2018-05-25 14:38:22'),
(36, 39, 'strain', 'Indica', 1, 3, '2018-05-25 14:38:28'),
(37, 40, 'strain', 'Sativa', 1, 3, '2018-05-25 14:38:44'),
(38, 41, 'strain', 'Sativa', 1, 3, '2018-05-25 14:38:51'),
(39, 42, 'strain', 'Sativa', 1, 3, '2018-05-25 14:38:58'),
(40, 43, 'strain', 'Sativa', 1, 3, '2018-05-25 14:39:04'),
(41, 44, 'strain', 'Sativa', 1, 3, '2018-05-25 14:39:10'),
(42, 45, 'strain', 'Sativa', 1, 3, '2018-05-25 14:39:17'),
(43, 46, 'strain', 'Sativa', 1, 3, '2018-05-25 14:39:25'),
(44, 47, 'strain', 'Sativa', 1, 3, '2018-05-25 14:39:31'),
(45, 48, 'strain', 'Sativa', 1, 3, '2018-05-25 14:39:39'),
(46, 49, 'strain', 'Sativa', 1, 3, '2018-05-25 14:39:45'),
(47, 50, 'strain', 'Sativa', 1, 3, '2018-05-25 14:39:51'),
(48, 51, 'strain', 'Sativa', 1, 3, '2018-05-25 14:40:04'),
(49, 52, 'strain', 'Sativa', 1, 3, '2018-05-25 14:40:10'),
(50, 53, 'strain', 'Sativa', 1, 3, '2018-05-25 14:40:18');

-- --------------------------------------------------------

--
-- Table structure for table `uploads`
--

DROP TABLE IF EXISTS `uploads`;
CREATE TABLE IF NOT EXISTS `uploads` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `organization_id` int(11) NOT NULL,
  `created_by` int(11) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `organization_id` (`organization_id`),
  KEY `created_by` (`created_by`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `uploads`
--

INSERT INTO `uploads` (`id`, `name`, `organization_id`, `created_by`, `timestamp`) VALUES
(1, 'receipt-2018.png', 1, 1, '2018-05-25 17:16:25'),
(2, 'receipt-2018.png', 1, 1, '2018-05-25 17:16:46'),
(3, 'receipt-2018.png', 1, 1, '2018-05-25 17:21:24'),
(4, 'receipt-2018.png', 1, 1, '2018-05-25 17:24:08'),
(5, 'receipt-2018.png', 1, 1, '2018-05-25 17:26:58'),
(6, 'receipt-2018.png', 1, 1, '2018-06-07 19:09:57'),
(7, 'receipt-2018.png', 1, 1, '2018-06-07 19:13:57');

-- --------------------------------------------------------

--
-- Table structure for table `uploads_meta`
--

DROP TABLE IF EXISTS `uploads_meta`;
CREATE TABLE IF NOT EXISTS `uploads_meta` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `upload_id` int(11) NOT NULL,
  `meta_name` varchar(250) NOT NULL,
  `meta_value` text NOT NULL,
  `organization_id` int(11) NOT NULL,
  `created_by` int(11) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `upload_id` (`upload_id`,`meta_name`,`organization_id`),
  UNIQUE KEY `single meta_name per upload` (`upload_id`,`meta_name`),
  KEY `created_by` (`created_by`),
  KEY `organization_id` (`organization_id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `uploads_meta`
--

INSERT INTO `uploads_meta` (`id`, `upload_id`, `meta_name`, `meta_value`, `organization_id`, `created_by`, `timestamp`) VALUES
(1, 1, 'content_type', 'image/png', 1, 1, '2018-05-25 17:16:25'),
(3, 2, 'content_type', 'image/png', 1, 1, '2018-05-25 17:16:46'),
(5, 3, 'content_type', 'image/png', 1, 1, '2018-05-25 17:21:24'),
(6, 3, 'upload_exists', '1', 1, 1, '2018-05-25 17:21:25'),
(7, 4, 'content_type', 'image/png', 1, 1, '2018-05-25 17:24:08'),
(8, 4, 'upload_exists', '1', 1, 1, '2018-05-25 17:24:09'),
(9, 5, 'content_type', 'image/png', 1, 1, '2018-05-25 17:26:58'),
(10, 5, 'upload_exists', '1', 1, 1, '2018-05-25 17:26:58'),
(11, 6, 'content_type', 'image/png', 1, 1, '2018-06-07 19:09:57'),
(12, 6, 'upload_exists', '1', 1, 1, '2018-06-07 19:09:59'),
(13, 7, 'content_type', 'image/png', 1, 1, '2018-06-07 19:13:57'),
(14, 7, 'upload_exists', '1', 1, 1, '2018-06-07 19:13:58');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
CREATE TABLE IF NOT EXISTS `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `organization_id` int(11) NOT NULL,
  `created_by` int(11) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `name`, `organization_id`, `created_by`, `timestamp`) VALUES
(1, 'daniel.favand@wilcompute.com', 1, 1, '2018-04-02 15:25:25'),
(2, 'andrew.wilson@wilcompute.com', 1, 1, '2018-04-02 15:25:25'),
(3, 'tests+s2s-dev@wilcompute.com', 1, 1, '2018-04-06 14:18:27'),
(4, 'daniel.favand+demo@wilcompute.com', 2, 1, '2018-04-09 13:42:02'),
(5, 'hareen.peiris@wilcompute.com', 1, 1, '2018-04-09 14:16:58'),
(6, 'william.buttenham@wilcompute.com', 1, 1, '2018-04-09 16:32:42'),
(7, 'shila.regmi.atreya@wilcompute.com', 1, 1, '2018-05-25 12:45:39'),
(8, 'daniel.kain@wilcompute.com', 1, 1, '2018-06-08 12:55:43'),
(9, 'aneesa.guerra.khan@wilcompute.com', 1, 1, '2018-06-08 12:56:08');

-- --------------------------------------------------------

--
-- Table structure for table `users_meta`
--

DROP TABLE IF EXISTS `users_meta`;
CREATE TABLE IF NOT EXISTS `users_meta` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `meta_name` varchar(250) NOT NULL,
  `meta_value` text NOT NULL,
  `organization_id` int(11) NOT NULL,
  `created_by` int(11) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_meta_per_user` (`user_id`,`meta_name`),
  KEY `user_id` (`user_id`),
  KEY `created_by` (`created_by`),
  KEY `organization_id` (`organization_id`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `users_meta`
--

INSERT INTO `users_meta` (`id`, `user_id`, `meta_name`, `meta_value`, `organization_id`, `created_by`, `timestamp`) VALUES
(1, 1, 'enabled', 'True', 1, 1, '2018-03-29 19:24:27'),
(2, 1, 'auth0_id', 'auth0|5ab26f288bd5067ff5787c89', 1, 1, '2018-03-29 18:44:12'),
(3, 1, 'role_id', '1', 1, 1, '2018-04-02 15:25:25'),
(4, 2, 'enabled', 'True', 1, 1, '2018-03-29 19:24:27'),
(5, 2, 'auth0_id', 'auth0|5a9efa307a392148fa27df14', 1, 1, '2018-03-29 18:44:12'),
(6, 2, 'role_id', '1', 1, 1, '2018-04-02 15:25:25'),
(7, 3, 'enabled', 'True', 1, 1, '2018-04-06 14:18:27'),
(8, 3, 'role_id', '1', 1, 1, '2018-04-06 14:18:27'),
(9, 3, 'auth0_id', 'auth0|5ac781b6fcdc016ee9ee751b', 1, 1, '2018-04-06 14:18:28'),
(10, 4, 'enabled', 'True', 2, 1, '2018-04-09 13:42:15'),
(11, 4, 'role_id', '2', 2, 1, '2018-04-09 13:42:33'),
(12, 4, 'auth0_id', 'auth0|5acb6d9fa33e56128a547d67', 2, 1, '2018-04-09 13:42:30'),
(13, 5, 'enabled', 'True', 1, 1, '2018-04-09 14:16:58'),
(14, 5, 'role_id', '1', 1, 1, '2018-04-09 14:16:58'),
(15, 5, 'auth0_id', 'auth0|5acb75dda33e56128a547fac', 1, 1, '2018-04-09 14:17:00'),
(18, 6, 'role_id', '1', 1, 1, '2018-04-09 16:32:10'),
(19, 6, 'enabled', 'True', 1, 1, '2018-04-09 16:32:10'),
(20, 6, 'auth0_id', 'auth0|5acb958da33e56128a548837', 1, 1, '2018-04-09 16:32:11'),
(21, 7, 'enabled', 'True', 1, 1, '2018-05-25 12:45:39'),
(22, 7, 'auth0_id', 'auth0|5b04355c42f10e18ba74ed31', 1, 1, '2018-05-25 12:45:39'),
(23, 7, 'role_id', '1', 1, 1, '2018-05-25 12:45:39'),
(24, 8, 'enabled', 'True', 1, 1, '2018-06-08 12:55:43'),
(25, 8, 'role_id', '1', 1, 1, '2018-06-08 12:55:43'),
(26, 8, 'auth0_id', 'auth0|5b1a7cd2157859716f2d1f76', 1, 1, '2018-06-08 12:55:45'),
(27, 9, 'enabled', 'True', 1, 1, '2018-06-08 12:56:08'),
(28, 9, 'role_id', '1', 1, 1, '2018-06-08 12:56:08'),
(29, 9, 'auth0_id', 'auth0|5b1a7cea55f2302168ff85cd', 1, 1, '2018-06-08 12:56:09');

--
-- Constraints for dumped tables
--

--
-- Constraints for table `activities`
--
ALTER TABLE `activities`
  ADD CONSTRAINT `activities_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `activities_ibfk_2` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`);

--
-- Constraints for table `activities_meta`
--
ALTER TABLE `activities_meta`
  ADD CONSTRAINT `activities_meta_ibfk_1` FOREIGN KEY (`activity_id`) REFERENCES `activities` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `activities_meta_ibfk_2` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`),
  ADD CONSTRAINT `activities_meta_ibfk_3` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`);

--
-- Constraints for table `clients`
--
ALTER TABLE `clients`
  ADD CONSTRAINT `clients_ibfk_1` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`),
  ADD CONSTRAINT `clients_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`);

--
-- Constraints for table `clients_meta`
--
ALTER TABLE `clients_meta`
  ADD CONSTRAINT `clients_meta_ibfk_1` FOREIGN KEY (`client_id`) REFERENCES `clients` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `clients_meta_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `clients_meta_ibfk_3` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`);

--
-- Constraints for table `inventories`
--
ALTER TABLE `inventories`
  ADD CONSTRAINT `inventories_ibfk_1` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`),
  ADD CONSTRAINT `inventories_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`);

--
-- Constraints for table `inventories_meta`
--
ALTER TABLE `inventories_meta`
  ADD CONSTRAINT `inventories_meta_ibfk_1` FOREIGN KEY (`inventory_id`) REFERENCES `inventories` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `inventories_meta_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `inventories_meta_ibfk_3` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`);

--
-- Constraints for table `organizations`
--
ALTER TABLE `organizations`
  ADD CONSTRAINT `organizations_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`);

--
-- Constraints for table `organizations_meta`
--
ALTER TABLE `organizations_meta`
  ADD CONSTRAINT `organizations_meta_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `organizations_meta_ibfk_2` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `products`
--
ALTER TABLE `products`
  ADD CONSTRAINT `products_ibfk_1` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`),
  ADD CONSTRAINT `products_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`);

--
-- Constraints for table `products_meta`
--
ALTER TABLE `products_meta`
  ADD CONSTRAINT `products_meta_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `products_meta_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `products_meta_ibfk_3` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`);

--
-- Constraints for table `roles_meta`
--
ALTER TABLE `roles_meta`
  ADD CONSTRAINT `roles_meta_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `roles_meta_ibfk_2` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`),
  ADD CONSTRAINT `roles_meta_ibfk_3` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `rooms`
--
ALTER TABLE `rooms`
  ADD CONSTRAINT `room_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `rooms_ibfk_1` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`);

--
-- Constraints for table `rooms_meta`
--
ALTER TABLE `rooms_meta`
  ADD CONSTRAINT `rooms_meta_ibfk_1` FOREIGN KEY (`room_id`) REFERENCES `rooms` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `rooms_meta_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `rooms_meta_ibfk_3` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`);

--
-- Constraints for table `rules`
--
ALTER TABLE `rules`
  ADD CONSTRAINT `rules_ibfk_1` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`),
  ADD CONSTRAINT `rules_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`);

--
-- Constraints for table `taxonomies`
--
ALTER TABLE `taxonomies`
  ADD CONSTRAINT `taxonomies_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `taxonomies_ibfk_2` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`);

--
-- Constraints for table `taxonomy_options`
--
ALTER TABLE `taxonomy_options`
  ADD CONSTRAINT `taxonomy_options_ibfk_1` FOREIGN KEY (`taxonomy_id`) REFERENCES `taxonomies` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `taxonomy_options_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `taxonomy_options_ibfk_3` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`);

--
-- Constraints for table `taxonomy_options_meta`
--
ALTER TABLE `taxonomy_options_meta`
  ADD CONSTRAINT `created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `organization_id` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`),
  ADD CONSTRAINT `taxonomy_option_id` FOREIGN KEY (`taxonomy_option_id`) REFERENCES `taxonomy_options` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `uploads`
--
ALTER TABLE `uploads`
  ADD CONSTRAINT `upload_ibfk_1` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`),
  ADD CONSTRAINT `upload_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`);

--
-- Constraints for table `uploads_meta`
--
ALTER TABLE `uploads_meta`
  ADD CONSTRAINT `uploads_meta_ibfk_1` FOREIGN KEY (`upload_id`) REFERENCES `uploads` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `uploads_meta_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `uploads_meta_ibfk_3` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`);

--
-- Constraints for table `users_meta`
--
ALTER TABLE `users_meta`
  ADD CONSTRAINT `users_meta_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `users_meta_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `users_meta_ibfk_3` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`);
SET FOREIGN_KEY_CHECKS=1;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
