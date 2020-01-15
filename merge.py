import sqlite3

conn1 = sqlite3.connect('classutil.db')
conn2 = sqlite3.connect('classutil_latest.db')

cur1 = conn1.cursor()
cur2 = conn2.cursor()

updates = {}
# add update times
cur2.execute('SELECT id, time FROM updates')
for i in cur2.fetchall():
    cur1.execute('INSERT INTO updates (time) VALUES (?)', i[1:])
    updates[i[0]] = cur1.lastrowid

cur2.execute("SELECT id, name, code, term, year FROM courses")
for i in cur2.fetchall():
    cur1.execute('INSERT INTO courses (name, code, term, year) VALUES (?,?,?,?)', i[1:])
    orig_course_id = i[0]
    course_id = cur1.lastrowid

    cur2.execute('SELECT id, unsw_id, cmp_type, type, section, times FROM components WHERE course_id=?', (orig_course_id,))
    for j in cur2.fetchall():
        cur1.execute('INSERT INTO components (course_id, unsw_id, cmp_type, type, section, times) VALUES (?,?,?,?,?,?)', (course_id,) + j[1:])
        orig_component_id = j[0]
        component_id = cur1.lastrowid

        cur2.execute('SELECT update_id, status, filled, maximum FROM capacities WHERE component_id=?', (orig_component_id, ))
        for k in cur2.fetchall():
            cur1.execute('INSERT INTO capacities (component_id, update_id, status, filled, maximum) VALUES (?,?,?,?,?)', (component_id, updates[k[0]]) +  k[1:])



conn1.commit()
conn1.close()
conn2.close()
