DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS users;

CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
);

INSERT INTO posts (title, content) VALUES ('Hello World', 'This is my first post, I love sqlite!!!');
INSERT INTO posts (title, content) VALUES ('Recent', 'Being tired though...');
INSERT INTO posts (title, content) VALUES ('Eat', 'Taiwanese food are gr8');

INSERT INTO users (username, password) VALUES ('Julian_Laup', '3f24aac267377d2f8a53f1ebb3d49223');
INSERT INTO users (username, password) VALUES ('Shiro', '29463cb4cc302022ca386fe44776f9fc');
INSERT INTO users (username, password) VALUES ('twitter_pwd', 'f79975048e623bce754379568af584a3');
