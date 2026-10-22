-- TECH AI | Smart Way - Database Initialization Script for MySQL 8.x
CREATE DATABASE IF NOT EXISTS tech_ai_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE tech_ai_db;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(191) NOT NULL UNIQUE,
    full_name VARCHAR(191) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'student',
    language_pref VARCHAR(20) DEFAULT 'en',
    theme_pref VARCHAR(20) DEFAULT 'dark',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Student Profiles table (for Auto Form Filler and personalization)
CREATE TABLE IF NOT EXISTS user_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    roll_number VARCHAR(100),
    father_name VARCHAR(191),
    mother_name VARCHAR(191),
    dob VARCHAR(50),
    gender VARCHAR(30),
    category VARCHAR(50) DEFAULT 'General',
    village VARCHAR(191),
    district VARCHAR(191),
    state VARCHAR(191),
    pin_code VARCHAR(20),
    college VARCHAR(255),
    branch VARCHAR(191),
    section VARCHAR(50),
    academic_year VARCHAR(50),
    phone_number VARCHAR(30),
    annual_income VARCHAR(50),
    aadhar_last4 VARCHAR(10),
    bank_account VARCHAR(100),
    ifsc_code VARCHAR(50),
    verified_docs_meta JSON,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Learning Sessions table
CREATE TABLE IF NOT EXISTS learning_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    content_type VARCHAR(50) DEFAULT 'pdf',
    source_text LONGTEXT,
    current_index INT DEFAULT 0,
    speed FLOAT DEFAULT 1.0,
    difficulty VARCHAR(50) DEFAULT 'medium',
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Smart Notesbook table
CREATE TABLE IF NOT EXISTS smart_notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    original_snippet LONGTEXT,
    teacher_explanation LONGTEXT,
    summary TEXT,
    key_points JSON,
    tags VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Form Analysis table (for Auto Form Filler)
CREATE TABLE IF NOT EXISTS form_analyses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    form_source VARCHAR(255),
    detected_fields JSON,
    matched_profile JSON,
    missing_fields JSON,
    document_requirements JSON,
    status VARCHAR(50) DEFAULT 'analyzed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Processed Documents table
CREATE TABLE IF NOT EXISTS processed_documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    original_name VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    file_size_kb INT,
    operations_applied JSON,
    extracted_equations JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Quiz Records table
CREATE TABLE IF NOT EXISTS quiz_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    topic VARCHAR(255) NOT NULL,
    score INT NOT NULL,
    total_questions INT NOT NULL,
    questions_data JSON,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
