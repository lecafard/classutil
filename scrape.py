import os
import re
import requests
from bs4 import BeautifulSoup
from db import create_db
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
            component = Component(int(cid), comp, typ, sect, status, cap, times)
            course.components.append(component)

    return courses

def do_insert(data, db):
    c = db.cursor()
    for fac in data:
        for course in fac:
            c.execute('INSERT INTO courses (code, name, term, year) VALUES(?,?,?,?)', (course.code, course.name, course.term, course.year))
            course_id = c.lastrowid
            for cmp in course.components:
                c.execute('INSERT INTO components (course_id, component_id, cmp_type, type, section, status, capacity, times) VALUES (?,?,?,?,?,?,?,?)',
                          (course_id, cmp.id, cmp.cmp_type, cmp.type, cmp.section, cmp.status, cmp.capacity, cmp.times))
    c.close()
    db.commit()


if __name__ == '__main__':
    r = requests.get(ROOT_URI)
    files = re.findall(r'[A-Z]{4}_[TU]\d\.html', r.text)
    correct = re.search('correct as at <strong>(.*)</strong>', r.text).group(1)
    correct_dt = int(parser.parse(correct).timestamp())
    db = create_db(f'classutil-{correct_dt}.db')

    pool = ThreadPool(CONCURRENCY)

    res = pool.map(do_scrape, files)
    do_insert(res, db)
    db.close()

