CREATE DATABASE IF NOT EXISTS college_chatbot;
USE college_chatbot;

-- =========================
-- COLLEGES TABLE
-- =========================
CREATE TABLE colleges (
    id INT AUTO_INCREMENT PRIMARY KEY,
    college_name VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    avg_fee INT,
    avg_placement_salary INT,
    type VARCHAR(20),
    map_link TEXT,
    image_link TEXT,
    campus_tour TEXT
);

-- =========================
-- BRANCHES TABLE
-- =========================
CREATE TABLE branches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    college_id INT,
    branch_name VARCHAR(50),
    min_percentage INT,
    min_jee INT,
    FOREIGN KEY (college_id) REFERENCES colleges(id)
);

-- =========================
-- HOSTEL TABLE
-- =========================
CREATE TABLE hostel (
    id INT AUTO_INCREMENT PRIMARY KEY,
    college_id INT,
    ac_fee INT,
    non_ac_fee INT,
    FOREIGN KEY (college_id) REFERENCES colleges(id)
);

-- =========================
-- CONTACT TABLE
-- =========================
CREATE TABLE contact (
    id INT AUTO_INCREMENT PRIMARY KEY,
    college_id INT,
    phone VARCHAR(15),
    email VARCHAR(100),
    website VARCHAR(255),
    FOREIGN KEY (college_id) REFERENCES colleges(id)
);

-- =========================
-- FACULTY TABLE
-- =========================
CREATE TABLE faculty (
    id INT AUTO_INCREMENT PRIMARY KEY,
    branch_id INT,
    faculty_name VARCHAR(255),
    designation VARCHAR(100),
    FOREIGN KEY (branch_id) REFERENCES branches(id)
);

-- =========================
-- SCHOLARSHIP TABLE
-- =========================
CREATE TABLE scholarship (
    id INT AUTO_INCREMENT PRIMARY KEY,
    branch_id INT,
    scholarship_name VARCHAR(255),
    eligibility TEXT,
    amount INT,
    FOREIGN KEY (branch_id) REFERENCES branches(id)
);

-- =========================
-- PLACEMENTS TABLE
-- =========================
CREATE TABLE placements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    college_id INT,
    branch_id INT,
    year YEAR,
    avg_package INT,
    min_package INT,
    highest_package INT,
    total_placed INT,
    total_eligible INT,
    FOREIGN KEY (college_id) REFERENCES colleges(id),
    FOREIGN KEY (branch_id) REFERENCES branches(id)
);