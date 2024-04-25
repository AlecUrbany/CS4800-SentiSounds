CREATE EXTENSION IF NOT EXISTS pgcrypto;

SET timezone = 'UTC';

CREATE TABLE IF NOT EXISTS user_auth(
    email_address VARCHAR(320) PRIMARY KEY NOT NULL,
    hashed_password VARCHAR(72) NOT NULL,

    authenticated BOOLEAN DEFAULT False,
    time_created TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS spotify_auth(
    email_address VARCHAR(320) PRIMARY KEY NOT NULL,
    spotify_token TEXT DEFAULT NULL,

    FOREIGN KEY (email_address)
        REFERENCES user_auth(email_address)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_info(
    email_address VARCHAR(320) PRIMARY KEY NOT NULL,
    display_name VARCHAR(32) NOT NULL DEFAULT '',


    FOREIGN KEY (email_address)
        REFERENCES user_auth(email_address)
        ON DELETE CASCADE
);