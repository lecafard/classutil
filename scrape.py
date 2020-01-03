import os
import re
import requests
from bs4 import BeautifulSoup
from db import get_database
from data_types import Course, Component
from dateutil import parser
import sys
from multiprocessing.pool import ThreadPool

ROOT_URI = 'http://classutil.unsw.edu.au/'
CONCURRENCY = 8

def do_scrape(file):
    log(f'Getting {file}')
    courses = []

    req = requests.get(f'{ROOT_URI}{file}')
    soup = BeautifulSoup(req.text, features='html.parser')
    term_date = soup.find('p', class_='classSearchMinorHeading').text.split(' - ')[-1]

    term = file[-7:-5]
    year = term_date.split(" ")[-1]

    table = soup.find_all('table')[2]
    course_name = ''
    course_code = ''
    course = None

    for i in table.find_all('tr'):
        if i.text == '^ top ^':
            break

        if_course = i.find_all('td', class_='cucourse')
        if len(if_course) == 2:
            course_code = if_course[0].text.strip()
            course_name = if_course[1].text.strip()
            course = Course(course_code, course_name, term, year)
            courses.append(course)

        elif 'class' in i.attrs and (i['class'][0].startswith('row') or i['class'][0] == 'stub'):
            comp, sect, cid, typ, status, cap, _, times = map(lambda x: x.text.strip(), i.find_all('td'))
            component = Component(int(cid), comp, typ, sect, status, cap, times)
            course.components.append(component)

    return courses
def log(*message):
    print(*message, file=sys.stderr)

def do_scrape(file):
    log(f'Getting {file}')
    courses = []

    req = requests.get(f'{ROOT_URI}{file}')
    soup = BeautifulSoup(req.text, features='html.parser')
    term_date = soup.find('p', class_='classSearchMinorHeading').text.split(' - ')[-1]

    term = file[-7:-5]
    year = term_date.split(" ")[-1]

    table = soup.find_all('table')[2]
    course_name = ''
    course_code = ''
    course = None

    for i in table.find_all('tr'):
        if i.text == '^ top ^':
            break

        if_course = i.find_all('td', class_='cucourse')
        if len(if_course) == 2:
            course_code = if_course[0].text.strip()
            course_name = if_course[1].text.strip()
            course = Course(course_code, course_name, term, year)
            courses.append(course)

        elif 'class' in i.attrs and (i['class'][0].startswith('row') or i['class'][0] == 'stub'):
            comp, sect, cid, typ, status, cap, _, times = map(lambda x: x.text.strip(), i.find_all('td'))
            res = re.search(r'(\d+)/(\d+)', cap)
            if res != None:
                filled = res[1]
                maximum = res[2]
            else:
                filled = 0
                maximum = 0
            component = Component(int(cid), comp, typ, sect, status, filled, maximum, times)
            course.components.append(component)

    return courses

def do_update(data, correct_dt, db):
    c = db.cursor()

    c.execute('INSERT INTO updates (time) VALUES (?)', (correct_dt, ))
    update_id = c.lastrowid

    for fac in data:
        for course in fac:
            # check to see if course exists
            c.execute('SELECT id FROM courses WHERE code=? AND term=? AND year=? LIMIT 1', (course.code, course.term, course.year))
            res = c.fetchone()
            if res == None:
                c.execute('INSERT INTO courses (code, name, term, year) VALUES(?,?,?,?)', (course.code, course.name, course.term, course.year))
                course_id = c.lastrowid
            else:
                course_id = res[0]

            for cmp in course.components:
                # check if component has been created
                c.execute('SELECT id FROM components WHERE unsw_id=? AND course_id=? LIMIT 1', (cmp.id, course_id))
                res = c.fetchone()
                if res == None:
                    c.execute('INSERT INTO components(course_id, unsw_id, cmp_type, type, section, times) VALUES (?,?,?,?,?,?)',
                              (course_id, cmp.id, cmp.cmp_type, cmp.type, cmp.section, cmp.times))
                    cmp_id = c.lastrowid
                else:
                    c.execute('UPDATE components SET times=? WHERE id=?', (cmp.times, res[0]))
                    cmp_id = res[0]

                c.execute('INSERT INTO capacities (component_id, update_id, status, filled, maximum) VALUES (?,?,?,?,?)',
                          (cmp_id, update_id, cmp.status, cmp.filled, cmp.maximum))
    c.close()
    db.commit()


if __name__ == '__main__':
    r = requests.get(ROOT_URI)
    files = re.findall(r'[A-Z]{4}_[TU]\d\.html', r.text)
    correct = re.search('correct as at <strong>(.*)</strong>', r.text).group(1)
    correct_dt = int(parser.parse(correct).timestamp())
    db = get_database()

    c = db.cursor()
    # check if classutil data has been updated
    if c.execute('SELECT COUNT() FROM updates WHERE time=?', (correct_dt, )).fetchone()[0] != 0:
        log('classutil data has not been updated yet')
        log(f'last update: {correct}')
        c.close()
        sys.exit(0)

    c.close()

    pool = ThreadPool(CONCURRENCY)

    res = pool.map(do_scrape, files)
    do_update(res, correct_dt, db)
    db.close()

