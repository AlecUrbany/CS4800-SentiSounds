CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS user_auth(
    email_address VARCHAR(320) PRIMARY KEY NOT NULL,
    hashed_password VARCHAR(72) NOT NULL,

    display_name VARCHAR(32) NOT NULL DEFAULT '',

    spotify_client TEXT DEFAULT NULL
);