PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS answers;
DROP TABLE IF EXISTS game;
CREATE TABLE user (
user_id INTEGER PRIMARY KEY AUTOINCREMENT,
username varchar not null,
password varchar not null);
CREATE TABLE answers (
word_id INTEGER PRIMARY KEY AUTOINCREMENT,
correct_answers varchar not null,
possible_answers varchar not null);
CREATE TABLE game (
game_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
user_id INT NOT NULL,
word_id INT NOT NULL,
guess STRING (5) DEFAULT 'null',
guesses_left INT DEFAULT 6,
correct_spot STRING (5) DEFAULT 'null',
wrong_spot STRING (5) DEFAULT 'null',
condition STRING DEFAULT 'IP',
FOREIGN KEY (user_id) REFERENCES user (user_id),
FOREIGN KEY (word_id) REFERENCES answers (word_id));
INSERT INTO game VALUES(1,1,1,'hello',6,'null','null','IP');
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('game',1);
COMMIT;
