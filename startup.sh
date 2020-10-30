#!/bin/bash
source /antenv/bin/activate

python manage.py migrate

python manage.py createcachetable

python manage.py collectstatic --no-input

gunicorn --workers 8 --threads 4 --timeout 60 --access-logfile \
    '-' --error-logfile '-' --bind=0.0.0.0:8000  -k uvicorn.workers.UvicornWorker \
     --chdir=/home/site/wwwroot cloud_analysis_manager.asgi