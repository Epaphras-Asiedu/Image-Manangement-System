-- Drop tables if they exist (to start fresh)
DROP TABLE IF EXISTS image;
DROP TABLE IF EXISTS user;

-- Users table
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

-- Images table
CREATE TABLE image (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    tags TEXT,
    category TEXT,
    filename TEXT NOT NULL,
    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    deleted BOOLEAN DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES user(id)
);

        visibility TEXT DEFAULT 'public', 

