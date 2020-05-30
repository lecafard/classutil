classutil scraper
=================

My attempt at a [classutil](http://classutil.unsw.edu.au). It downloads the current UNSW class
allocations into a JSON file.

## Installation
```bash
# optional: use virtualenv
virtualenv -p python3 venv
. venv/bin/activate

pip3 install -r requirements.txt
```
## Run
```sh
python scrape.py output.json
```

The options are configurable, run with `--help` for more options.


## Library Usage
```py3
from classutil import scrape

# Scrape data
# Arguments don't need to be specified as these are the defaults.
data = scrape(
	root="https://classutil.unsw.edu.au",
	concurrency=1,
	logging=False)
```
