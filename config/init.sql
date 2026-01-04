-- Create user
CREATE USER crypto WITH PASSWORD 'crypto123';

-- Create database
CREATE DATABASE cryptodb OWNER crypto;

-- Connect to database
\c cryptodb

-- Prices table
CREATE TABLE IF NOT EXISTS crypto_prices (
    symbol TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    price FLOAT NOT NULL
);

-- Predictions table
CREATE TABLE IF NOT EXISTS crypto_prediction (
    symbol TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    predicted_price FLOAT NOT NULL
);

-- Permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO crypto;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO crypto;

