import os
import re
import requests
from functools import reduce
from bs4 import BeautifulSoup
from classutil.data_types import Course, Component
from dateutil import parser
import sys
from multiprocessing.pool import ThreadPool

ROOT_URI = 'http://classutil.unsw.edu.au/'

def log(*message, enabled=True):
    if enabled:
        print(*message, file=sys.stderr)

def _scrape_subject(root, filename, logging=False):
    log('Getting {}'.format(filename), enabled=logging)
    courses = []

    req = requests.get('{}{}'.format(root, filename))
    soup = BeautifulSoup(req.text, features='html.parser')

    term = filename[-7:-5]
    year = int(soup.find('title').text.split()[2])

    table = None

    for i in soup.find_all('table'):
        if i.find('td', class_='cucourse'):
            table = i
            break

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
                filled = int(res[1])
                maximum = int(res[2])
            else:
                filled = 0
                maximum = 0
            component = Component(int(cid), comp, typ, sect, status, filled, maximum, times)
            course.components.append(component)

    return courses

def scrape(root=ROOT_URI, last_updated=0, concurrency=1, logging=False):
    if root[-1] != '/':
        root += '/'
    r = requests.get(root)
    files = re.findall(r'[A-Z]{4}_[A-Z]\d\.html', r.text)
    correct = re.search('correct as at <(?:b|strong)>(.*)</(?:b|strong)>', r.text).group(1).replace(' EST ',' AEST ')
    correct_dt = int(parser.parse(correct, tzinfos={"AEST": "UTC+10", "AEDT": "UTC+11"}).timestamp())
    if correct_dt == last_updated:
        return {
            'correct_at': correct_dt, 
            'courses': []
        }
    if concurrency != 1:
        pool = ThreadPool(concurrency)
        courses = pool.starmap(_scrape_subject, [(root, i, logging) for i in files])
    else:
        courses = [_scrape_subject(root, i, logging) for i in files]

    return {
        'courses': [i.toJSON() for i in reduce(lambda x, y: x + y, courses)],
        'correct_at': correct_dt
    }
