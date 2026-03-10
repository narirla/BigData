-- DB 생성 + 문자셋 고정
CREATE DATABASE IF NOT EXISTS mydb
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_general_ci;

USE mydb;

-- 테이블 생성 (문자셋 명시)
CREATE TABLE IF NOT EXISTS product (
    pname VARCHAR(100),
    quantity INT,
    mfg_date DATE NOT NULL
) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

-- 초기 데이터 (중복 방지)
INSERT IGNORE INTO product (pname, quantity, mfg_date) VALUES
('Product 1', 100, '2023-01-01'),
('Product 2', 200, '2023-02-01'),
('Product 3', 300, '2023-03-01');
