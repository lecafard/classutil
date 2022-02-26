import re
import asyncio
import aiohttp
from functools import reduce
from bs4 import BeautifulSoup
from classutil.data_types import Course, Component
from dateutil import parser
import logging

ROOT_URI = 'http://classutil.unsw.edu.au/'
logger = logging.getLogger('classutil.scrape')

def _parse_subject(filename, data):
    courses = []
    soup = BeautifulSoup(data, features='html.parser')

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

async def _scrape_subject(client: aiohttp.ClientSession, root, filename):
    async with client.get('{}{}'.format(root, filename)) as resp:
        logger.info('Retrieved %s', filename)
        return _parse_subject(filename, await resp.text())

def scrape(root=ROOT_URI, last_updated=0, concurrency=8):
    return asyncio.run(scrape_async(root, last_updated, concurrency))

async def scrape_async(root=ROOT_URI, last_updated=0, concurrency=8):
    logger.info('Creating scraper with root=%s, last_updated=%s and concurrency=%s', root, last_updated, concurrency)
    connector = aiohttp.TCPConnector(limit=concurrency)
    client = aiohttp.ClientSession(connector=connector)
    if root[-1] != '/':
        root += '/'
    async with client.get(root) as resp:
        data = await resp.text()
        files = re.findall(r'[A-Z]{4}_[A-Z]\d\.html', data)
        correct = re.search('correct as at <(?:b|strong)>(.*)</(?:b|strong)>', data).group(1).replace(' EST ',' AEST ')
        correct_dt = int(parser.parse(correct, tzinfos={"AEST": "UTC+10", "AEDT": "UTC+11"}).timestamp())
        if correct_dt == last_updated:
            await client.close()
            return {
                'correct_at': correct_dt, 
                'courses': []
            }

    courses = await asyncio.gather(*[_scrape_subject(client, root, i) for i in files])
    await client.close()

    return {
        'courses': [i.toJSON() for i in reduce(lambda x, y: x + y, courses)],
        'correct_at': correct_dt
    }
