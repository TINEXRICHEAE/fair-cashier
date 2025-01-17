--Link to ER diagram: https://dbdiagram.io/d/678823fe6b7fa355c3038eed
-- Create Users Table
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,  -- Changed from VARCHAR to INT for consistency with Django's AutoField
    email VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(128) NOT NULL,  -- Increased length to match Django's default password field
    role VARCHAR(50) NOT NULL CHECK (role IN ('end_user', 'admin', 'superadmin')),  -- Updated role choices
    admin_email VARCHAR(50),  -- Added admin_email field
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,  -- Added is_active field
    is_staff BOOLEAN DEFAULT FALSE,  -- Added is_staff field
    is_superuser BOOLEAN DEFAULT FALSE  -- Added is_superuser field
);

-- Create Groups Table
CREATE TABLE groups (
    group_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE,  -- Added name field for group name
    admin_id INT,  -- Added admin_id field
    superadmin_id INT,  -- Added superadmin_id field
    FOREIGN KEY (admin_id) REFERENCES users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (superadmin_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- Create Points Table
CREATE TABLE points (
    points_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    points_balance INT DEFAULT 1000,
    points_earned INT DEFAULT 0,
    points_used INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Create Transactions Table
CREATE TABLE transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT NOT NULL,
    receiver_id INT NOT NULL,
    transaction_type VARCHAR(50) NOT NULL CHECK (
        transaction_type IN ('Buy Points', 'Sell Points', 'Share Points')  -- Updated transaction type choices
    ),
    points INT NOT NULL,  -- Changed from 'amount' to 'points' to match the model
    payment_channel VARCHAR(50) NOT NULL CHECK (
        payment_channel IN ('MTN', 'Airtel', 'Bank', 'Internal')  -- Updated payment channel choices
    ),
    status VARCHAR(50) NOT NULL CHECK (
        status IN ('Completed', 'Processing', 'Failed')  -- Updated status choices
    ),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES users(user_id) ON DELETE CASCADE
);