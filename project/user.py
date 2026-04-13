# -*- coding: utf-8 -*-

import sqlite3
import json
import random

class User:
    def __init__(self, id, first_name, last_name, age, language="eng", schedule=[], session = None):
        
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.full_name = "{} {}".format(self.first_name, self.last_name)
        self.age = age
        self.language = language                           
        
        #default initialization
        self.stress_session = [     ["N_sessions" , 0], 
                                    ["N_cycles" , 5], 
                                    ["preferred_volume" , 1], # qualcosa del tipo 1 2 ... 
                                    ["preferred_pace" , 1],   # qualcosa del tipo 1 2 ... 
                                    ["preference_speed" , 1], # qualcosa del tipo 1 2 3 4 ... 
                                    ["take_hand", 0],
                                    ["last_session" , True]   # True: andata bene ; False: andata male
        ]
        if session is not None:
            self.stress_session = session 
        
        self.schedule = sorted(schedule)
      

    def __str__(self):
        return "User ID: {}\n\t{}, Age: {}, Language: {} Schedule: {} --- Stress session: {}".format(self.id, self.full_name, self.age, self.language, json.dumps(self.schedule), json.dumps(self.stress_session))




DB_PATH = "/home/robot/playground/project/users.db"

def get_connection():
    # create the file on first use, enable row‐factory
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Create the users table if it doesn't exist.
    Call this once at startup of main.py and subsystem.py.
    """
    with get_connection() as db:
        db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY,
            first_name  TEXT NOT NULL,
            last_name   TEXT NOT NULL,
            age         INTEGER NOT NULL,
            language    TEXT NOT NULL, 
            schedule    TEXT NOT NULL,
            stress_session TEXT NOT NULL
        )
        """)
        db.commit()

def add_user(u):
    sql = """
      INSERT INTO users(id, first_name, last_name, age, language, schedule, stress_session)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    with get_connection() as db:
        db.execute(sql, (u.id, u.first_name, u.last_name, u.age, u.language, json.dumps(u.schedule), json.dumps(u.stress_session)))
        db.commit()

def get_next_id():
    with get_connection() as db:
        id = db.execute("SELECT MAX(id) FROM users").fetchone()
    id = id[0]
    if id is None: 
        return 1 
    return id+1
    

def get_all_users():
    with get_connection() as db:
        rows = db.execute("SELECT * FROM users").fetchall()
    users = []
    for r in rows:
        users.append(User(
            r["id"],
            r["first_name"],
            r["last_name"],
            r["age"],
            r["language"],
            json.loads(r["schedule"]),
            json.loads(r["stress_session"])
        ))
    return users

def get_user_by_id(uid):
    with get_connection() as db:
        r = db.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
    if not r:
        return None
    return User(
        r["id"], r["first_name"], r["last_name"],
        r["age"], r["language"], json.loads(r["schedule"]), json.loads(r["stress_session"])
    )

def get_user_by_fullname(first_name, last_name):
    with get_connection() as db:
        r = db.execute("SELECT * FROM users WHERE UPPER(first_name) = UPPER(?) AND UPPER(last_name) = UPPER(?)", (first_name, last_name)).fetchone()
    if not r:
        return None
    return User(
        r["id"], r["first_name"], r["last_name"],
        r["age"], r["language"], json.loads(r["schedule"]), json.loads(r["stress_session"])
    )    
    
    

def update_user(u):
    """
    Returns True if a row was updated, False if no such id existed.
    """
    sql = """
      UPDATE users
         SET first_name = ?, last_name = ?, age = ?, language = ?, schedule = ?, stress_session = ?
       WHERE id = ?
    """
    with get_connection() as db:
        cur = db.execute(sql, (
            u.first_name, u.last_name, u.age, u.language, json.dumps(u.schedule),json.dumps(u.stress_session), u.id
        ))
        db.commit()
    return cur.rowcount > 0

def remove_user_by_id(uid):
    with get_connection() as db:
        cur = db.execute("DELETE FROM users WHERE id = ?", (uid,))
        db.commit()
    return cur.rowcount > 0


def random_schedule():
    schedule = []
    
    n_schedule = random.randint(1,10)
    
    for i in range(n_schedule):
        
        
        schedule.append(["Event {}".format(i), 2025, random.randint(1,12), random.randint(1,28), random.randint(0,24), 0])
    
    
    return schedule


if __name__ == '__main__':
         
    sched = sorted(random_schedule())
    
    print(random_schedule())
    