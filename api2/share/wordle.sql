-- $ sqlite3 ./var/wordle.db < ./share/wordle.sql

PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS answers;
DROP TABLE IF EXISTS game;
CREATE TABLE user (
user_id INTEGER PRIMARY KEY AUTOINCREMENT,
username varchar not null,
password varchar not null);
CREATE TABLE game (
game_id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
word_id INTEGER, guesses_left INTEGER, guess STRING (5), guess_valid BOOL, correct_spot STRING, wrong_spot STRING,
FOREIGN KEY (user_id) REFERENCES user (user_id),
FOREIGN KEY (word_id) REFERENCES answers (word_id));
CREATE TABLE answers (
word_id INTEGER PRIMARY KEY AUTOINCREMENT,
correct_answers varchar not null,
possible_answers varchar not null);
COMMIT;
