import sqlite3
from os import system

DB_CLASSUTIL = 'data/classutil.db'

def get_database():
    system('mkdir -p data')
    conn = sqlite3.connect(DB_CLASSUTIL)
    # create tables
    c = conn.cursor()

    # database already created
    if c.execute('SELECT COUNT() FROM sqlite_master WHERE type=\'table\' AND name=\'updates\'').fetchone()[0] != 0:
        c.close()
        return conn

    c.execute('''CREATE TABLE updates (
              id            INTEGER PRIMARY KEY AUTOINCREMENT,
              time          TIMESTAMP)''')

    c.execute('''CREATE TABLE courses (
              id    INTEGER PRIMARY KEY AUTOINCREMENT,
              code  VARCHAR(8),
              name  VARCHAR(255),
              term  VARCHAR(2),
              year  INTEGER,
              UNIQUE(code, year, term))''')
    c.execute('CREATE INDEX idx_courses_year_term ON courses (year, term)')

    c.execute('''CREATE TABLE components (
              id            INTEGER PRIMARY KEY AUTOINCREMENT,
              unsw_id       INTEGER,
              course_id     INTEGER,
              cmp_type      VARCHAR(3),
              type          VARCHAR(4),
              section       VARCHAR(4),
              times         VARCHAR(255),
              UNIQUE(unsw_id, course_id))''')

    c.execute('''CREATE TABLE capacities (
              component_id  INTEGER,
              update_id     INTEGER,
              status        VARCHAR(6),
              filled        INTEGER,
              maximum       INTEGER)''')
    c.execute('CREATE INDEX idx_capacities_component_id ON capacities (component_id)')

    c.close()

    return conn
