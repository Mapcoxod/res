# my-elearning [![Build Status](https://travis-ci.org/delitamakanda/elearning.svg?branch=master)](https://travis-ci.org/delitamakanda/elearning)
e-learning django app (django, python3)

## TODO
* Nice layout
* Login via Google
* ~~API~~
* ~~Celery worker~~
* ~~Reset Password~~
* ~~Search Form~~

load csv

```bash
python3 load_reviews.py data/review.csv
```

start celery

```bash
celery -A myelearning  worker -l info -B
```