import os
import re
import requests
from functools import reduce
from bs4 import BeautifulSoup
from data_types import Course, Component
from dateutil import parser
import sys
from multiprocessing.pool import ThreadPool
import json
import argparse


ROOT_URI = 'http://classutil.unsw.edu.au/'
CONCURRENCY = 4

def log(*message, enabled=True):
    if enabled:
        print(*message, file=sys.stderr)

def _scrape_subject(root, file, logging=False):
    log(f'Getting {file}', enabled=logging)
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

def scrape(root, concurrency=1, logging=False):
    r = requests.get(root)
    files = re.findall(r'[A-Z]{4}_[A-Z]\d\.html', r.text)
    correct = re.search('correct as at <(?:b|strong)>(.*)</(?:b|strong)>', r.text).group(1).replace(' EST ',' AEST ')
    correct_dt = int(parser.parse(correct).timestamp())
    pool = ThreadPool(concurrency)

    courses = pool.starmap(_scrape_subject, [(root, i, logging) for i in files])
    return {
        'courses': [i.toJSON() for i in reduce(lambda x, y: x + y, courses)],
        'correct_at': correct_dt
    }

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='Scrape classutil')
    ap.add_argument('output', action='store', help='output filename')
    ap.add_argument('-r', '--root-uri', default=ROOT_URI, help='root uri')
    ap.add_argument('-t', '--threads', default=CONCURRENCY, type=int, help='number of concurrent threads')
    ap.add_argument('-q', '--quiet', action='store_true', default=False, help='quiet mode')
    args = ap.parse_args()

    with open(args.output, 'w') as f:
        data = scrape(args.root_uri, args.threads, not args.quiet)
        f.write(json.dumps(data))

