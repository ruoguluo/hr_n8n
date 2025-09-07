-- MySQL数据库表结构用于存储Position Information表单数据

CREATE DATABASE IF NOT EXISTS hr_jd_system;
USE hr_jd_system;

-- Company Registration表（一个公司可以有多个JD）
CREATE TABLE IF NOT EXISTS company_registration (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id VARCHAR(255) UNIQUE NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    website VARCHAR(500) NOT NULL,
    contact_person VARCHAR(255) NOT NULL,
    contact_number VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Position Information表（JD表，关联到公司）
CREATE TABLE IF NOT EXISTS position_information (
    id INT AUTO_INCREMENT PRIMARY KEY,
    jd_id VARCHAR(255) UNIQUE NOT NULL,
    company_id VARCHAR(255) NOT NULL,
    job_title VARCHAR(255) NOT NULL,
    location VARCHAR(500) NOT NULL,
    team_structure TEXT,
    position_type ENUM('new', 'replacement') NOT NULL,
    new_reason TEXT,
    reason_leave TEXT,
    background_last TEXT,
    compliments_concerns TEXT,
    hiring_when VARCHAR(255),
    hiring_problems TEXT,
    emergency_level ENUM('low', 'medium', 'high', 'critical'),
    interview_rounds TEXT,
    compensation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES company_registration(company_id) ON DELETE CASCADE
);

-- 创建索引以提高查询性能
-- Company Registration表索引
CREATE INDEX idx_company_id ON company_registration(company_id);
CREATE INDEX idx_company_name ON company_registration(company_name);
CREATE INDEX idx_company_created_at ON company_registration(created_at);

-- Position Information表索引
CREATE INDEX idx_jd_id ON position_information(jd_id);
CREATE INDEX idx_position_company_id ON position_information(company_id);
CREATE INDEX idx_position_type ON position_information(position_type);
CREATE INDEX idx_emergency_level ON position_information(emergency_level);
CREATE INDEX idx_position_created_at ON position_information(created_at);