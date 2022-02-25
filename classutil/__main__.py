#!/usr/bin/python3
# Standalone scraping script
from classutil.scrape import scrape, ROOT_URI
import json
import argparse
import logging

CONCURRENCY = 4

ap = argparse.ArgumentParser(description='Scrape classutil')
ap.add_argument('output', action='store', help='output filename')
ap.add_argument('-r', '--root-uri', default=ROOT_URI, help='root uri')
ap.add_argument('-t', '--threads', default=CONCURRENCY, type=int, help='number of concurrent threads')
ap.add_argument('-q', '--quiet', action='store_true', default=False, help='quiet mode')
args = ap.parse_args()

with open(args.output, 'w') as f:
    if not args.quiet:
        logging.basicConfig(level=logging.INFO)
    data = scrape(root=args.root_uri, last_updated=0, concurrency=args.threads)
    f.write(json.dumps(data))

