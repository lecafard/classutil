classutil scraper
=================

My attempt at a [classutil](http://classutil.unsw.edu.au). It downloads the current UNSW class
allocations and puts it into a database (for easy querying). Not really sure what to do with
this data yet.

## Installation
```bash
# optional: use virtualenv
virtualenv -p python3 venv
. venv/bin/activate

pip3 install -r requirements.txt
```

## Usage
Just run the python script, and the database will be automatically created.
