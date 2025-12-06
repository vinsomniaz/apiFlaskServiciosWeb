CREATE DATABASE fintech_api
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER 'fintech_user'@'localhost' IDENTIFIED BY '123456';
GRANT ALL PRIVILEGES ON fintech_api.* TO 'fintech_user'@'localhost';
FLUSH PRIVILEGES;

USE fintech_api;

-- Tabla de usuarios (para login + JWT)
CREATE TABLE users (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(120),
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de transacciones
CREATE TABLE transactions (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  id_transaccion VARCHAR(64) NOT NULL UNIQUE,
  user_id BIGINT UNSIGNED NOT NULL,
  monto DECIMAL(12,2) NOT NULL,
  moneda CHAR(3) NOT NULL,
  origen_tipo VARCHAR(40) NOT NULL,
  origen_id VARCHAR(80) NOT NULL,
  destino_tipo VARCHAR(40) NOT NULL,
  destino_id VARCHAR(80) NOT NULL,
  status ENUM('OK','FAILED') NOT NULL,
  error_code VARCHAR(50),
  error_message VARCHAR(255),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  INDEX idx_transactions_user_created (user_id, created_at),
  INDEX idx_transactions_status_created (status, created_at),

  CONSTRAINT fk_transactions_user
    FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Cola simple para notificaciones por email (se manda en segundo plano)
CREATE TABLE email_notifications (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  transaction_id BIGINT UNSIGNED NOT NULL,
  to_email VARCHAR(255) NOT NULL,
  subject VARCHAR(255) NOT NULL,
  body TEXT NOT NULL,
  status ENUM('PENDING','SENT','FAILED') NOT NULL DEFAULT 'PENDING',
  attempts INT NOT NULL DEFAULT 0,
  last_error VARCHAR(255),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  sent_at TIMESTAMP NULL,

  INDEX idx_email_status_created (status, created_at),

  CONSTRAINT fk_email_tx
    FOREIGN KEY (transaction_id) REFERENCES transactions(id)
    ON DELETE CASCADE ON UPDATE CASCADE
);
