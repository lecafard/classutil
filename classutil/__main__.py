#!/usr/bin/python3
# Standalone scraping script
from scrape import scrape, ROOT_URI
import json
import argparse

CONCURRENCY = 4

ap = argparse.ArgumentParser(description='Scrape classutil')
ap.add_argument('output', action='store', help='output filename')
ap.add_argument('-r', '--root-uri', default=ROOT_URI, help='root uri')
ap.add_argument('-t', '--threads', default=CONCURRENCY, type=int, help='number of concurrent threads')
ap.add_argument('-q', '--quiet', action='store_true', default=False, help='quiet mode')
args = ap.parse_args()

with open(args.output, 'w') as f:
    data = scrape(args.root_uri, args.threads, not args.quiet)
    f.write(json.dumps(data))

