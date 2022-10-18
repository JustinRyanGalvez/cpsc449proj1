#!/usr/bin/env python3
import sqlite3

#establishing connections.
conn = sqlite3.connect('wordle.db')
c = conn.cursor()

#simple create table functions
def create_table():
    c.execute('CREATE TABLE IF NOT EXISTS user(username TEXT, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS answers(correct_answers TEXT, valid_answers TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS score(username TEXT, correct_answers TEXT, score INT)')

#This function is meant for populating the user table. 
def data_entry():
    c.execute("INSERT INTO user VALUES('Joe_Shmoe', 'stinky_lion35')")
    conn.commit()
    c.close()
    conn.close()

#As of right now I am unsure how to dump the json files into the answers table
#But I am guessing that we would have to use variables in order to fit them in.
#I will probably use this function after I figure out how to populate that table.
def dynamic_data_entry():

create_table()
data_entry()
