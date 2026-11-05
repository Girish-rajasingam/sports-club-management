CREATE DATABASE IF NOT EXISTS sports_club;
USE sports_club;

CREATE TABLE IF NOT EXISTS coaches (
  coach_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(60) NOT NULL,
  phone VARCHAR(15),
  speciality VARCHAR(40)
);
CREATE TABLE IF NOT EXISTS sports (
  sport_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(40) NOT NULL,
  monthly_fee DECIMAL(8,2) NOT NULL,
  coach_id INT,
  FOREIGN KEY (coach_id) REFERENCES coaches(coach_id) ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS members (
  member_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(60) NOT NULL,
  age INT,
  gender VARCHAR(10),
  phone VARCHAR(15),
  join_date DATE
);
CREATE TABLE IF NOT EXISTS enrollments (
  enroll_id INT AUTO_INCREMENT PRIMARY KEY,
  member_id INT NOT NULL,
  sport_id INT NOT NULL,
  FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE,
  FOREIGN KEY (sport_id) REFERENCES sports(sport_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS payments (
  payment_id INT AUTO_INCREMENT PRIMARY KEY,
  member_id INT NOT NULL,
  amount DECIMAL(8,2) NOT NULL,
  pay_date DATE,
  for_month VARCHAR(20),
  FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE
);

INSERT INTO coaches (name, phone, speciality) VALUES
 ('Ravi Kumar','9876543210','Cricket'),('Meena Devi','9123456780','Badminton');
INSERT INTO sports (name, monthly_fee, coach_id) VALUES
 ('Cricket',800,1),('Badminton',600,2);
INSERT INTO members (name, age, gender, phone, join_date) VALUES
 ('Arun',16,'Male','9000000001','2026-01-10'),('Divya',15,'Female','9000000002','2026-02-05');
INSERT INTO enrollments (member_id, sport_id) VALUES (1,1),(2,2);
INSERT INTO payments (member_id, amount, pay_date, for_month) VALUES
 (1,800,'2026-10-02','October'),(2,600,'2026-10-03','October');
