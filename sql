CREATE DATABASE web_info_db;

USE web_info_db;

CREATE TABLE website_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    url VARCHAR(255),
    social_media_links JSON,
    tech_stack VARCHAR(255),
    meta_title VARCHAR(255),
    meta_description TEXT,
    payment_gateways VARCHAR(255),
    website_language VARCHAR(50),
    category VARCHAR(100)
);

USE web_info_db;
SELECT * FROM website_info;
