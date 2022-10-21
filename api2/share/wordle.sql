PRAGMA foreign_keys=ON;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS game;
DROP TABLE IF EXISTS answers;
BEGIN TRANSACTION;
CREATE TABLE user (
user_id INTEGER PRIMARY KEY AUTOINCREMENT,
username varchar not null,
password varchar not null);
CREATE TABLE game (
game_id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
word_id INTEGER,
guesses_left INTEGER, 
guess STRING (5), 
guess_valid BOOL, 
correct_spot STRING, 
wrong_spot STRING,
FOREIGN KEY (user_id) REFERENCES user (user_id),
FOREIGN KEY (word_id) REFERENCES answers (word_id));
CREATE TABLE answers (
word_id INTEGER PRIMARY KEY AUTOINCREMENT,
correct_answers varchar not null,
possible_answers varchar not null);
DELETE FROM sqlite_sequence;
COMMIT;
