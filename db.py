import sqlite3
from os import path, system

def create_db(filename):
    fp = f'data/{filename}'
    if path.exists(fp):
        raise FileExistsError("data has not been updated")
    system('mkdir -p data')

    conn = sqlite3.connect(f'data/{filename}')
    # create tables
    c = conn.cursor()
    c.execute('''CREATE TABLE courses (
              id    INTEGER PRIMARY KEY AUTOINCREMENT,
              code  VARCHAR(8),
              name  VARCHAR(255),
              term  VARCHAR(2),
              year  INTEGER)''')
    c.execute('''CREATE TABLE components(
              component_id  INTEGER,
              course_id     INTEGER,
              cmp_type      VARCHAR(3),
              type          VARCHAR(4),
              section       VARCHAR(4),
              status        VARCHAR(6),
              capacity      VARCHAR(10),
              times         VARCHAR(255))''')
    c.close()

    return conn
