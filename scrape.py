import os
import re
import requests
from bs4 import BeautifulSoup
from data_types import Course, Component
from dateutil import parser
import sys
from multiprocessing.pool import ThreadPool

ROOT_URI = 'http://classutil.unsw.edu.au/'
CONCURRENCY = 4

if len(sys.argv) > 1:
    ROOT_URI = sys.argv[1]

def log(*message):
    print(*message, file=sys.stderr)

def _scrape_course(root, file):
    log(f'Getting {file}')
    courses = []

    req = requests.get(f'{ROOT_URI}{file}')
    soup = BeautifulSoup(req.text, features='html.parser')

    term = file[-7:-5]
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
                filled = res[1]
                maximum = res[2]
            else:
                filled = 0
                maximum = 0
            component = Component(int(cid), comp, typ, sect, status, filled, maximum, times)
            course.components.append(component)

    return courses

def scrape(root, concurrency):
    r = requests.get(root)
    files = re.findall(r'[A-Z]{4}_[A-Z]\d\.html', r.text)
    correct = re.search('correct as at <(?:b|strong)>(.*)</(?:b|strong)>', r.text).group(1).replace(' EST ',' AEST ')
    correct_dt = int(parser.parse(correct).timestamp())
    pool = ThreadPool(concurrency)

    courses = pool.starmap(_scrape_course, [(root, i) for i in files])
    return {
        'courses': courses,
        'correct_at': correct_dt
    }

if __name__ == '__main__':
    print(scrape(ROOT_URI, CONCURRENCY))
