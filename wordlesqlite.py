#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('wordle.db')
c = conn.cursor()
def create_table():
    c.execute('CREATE TABLE IF NOT EXISTS user(username TEXT, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS answers(correct_answers TEXT, valid_answers TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS score(username TEXT, correct_answers TEXT, score INT)')

def data_entry():
    c.execute("INSERT INTO user VALUES('Joe_Shmoe', 'stinky_lion35')")
    conn.commit()
    c.close()
    conn.close()

create_table()
data_entry()
