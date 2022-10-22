#!/usr/bin/env python3
import sqlite3
import json
#This establishes the connection to wordle.db
#Make sure to keep in the same directoy as wordle.db or else
#a new database will be created instead
conn = sqlite3.connect('wordle.db')
c = conn.cursor()

def population():
    #make sure correct.json and valid.json are in the same directory as
    #populate.py or else there will be errors
    with open('correct.json',) as e:
        info = json.load(e)
        for j in range(len(info)):
            c.execute("INSERT INTO correct_answers(answers) VALUES(?)",[info[j]])
    with open('valid.json',) as f:
            data = json.load(f)
            for j in range(len(data)):
                c.execute("INSERT INTO possible_answers(answers) VALUES(?)",[data[j]])

    #This closes any connection to the database
    conn.commit()
    c.close()
    conn.close()

population()
