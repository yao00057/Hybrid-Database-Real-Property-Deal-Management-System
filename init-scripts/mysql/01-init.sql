-- Create databases
CREATE DATABASE IF NOT EXISTS real_estate;
CREATE DATABASE IF NOT EXISTS real_estate_financial;

-- Create user with full access
DROP USER IF EXISTS 'reuser'@'%';
CREATE USER 'reuser'@'%' IDENTIFIED WITH mysql_native_password BY 'repassword';

-- Grant permissions
GRANT ALL PRIVILEGES ON real_estate.* TO 'reuser'@'%';
GRANT ALL PRIVILEGES ON real_estate_financial.* TO 'reuser'@'%';
FLUSH PRIVILEGES;

-- Select the main database
USE real_estate_financial;

-- Create tables for financial transactions
CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    deal_id VARCHAR(24) NOT NULL,
    type ENUM('deposit', 'commission', 'legal_fee', 'tax', 'adjustment', 'disbursement') NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    from_party VARCHAR(100),
    to_party VARCHAR(100),
    description TEXT,
    status ENUM('pending', 'completed', 'cancelled', 'refunded') DEFAULT 'pending',
    reference_number VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    created_by VARCHAR(24),
    INDEX idx_deal_id (deal_id),
    INDEX idx_status (status),
    INDEX idx_type (type)
);

CREATE TABLE IF NOT EXISTS trust_accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_name VARCHAR(100) NOT NULL,
    account_number VARCHAR(50) UNIQUE NOT NULL,
    bank_name VARCHAR(100),
    balance DECIMAL(15, 2) DEFAULT 0.00,
    holder_type ENUM('lawyer', 'brokerage') NOT NULL,
    holder_id VARCHAR(24) NOT NULL,
    status ENUM('active', 'frozen', 'closed') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_holder (holder_type, holder_id)
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    old_values JSON,
    new_values JSON,
    performed_by VARCHAR(24),
    performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    INDEX idx_entity (entity_type, entity_id),
    INDEX idx_performed_at (performed_at)
);
