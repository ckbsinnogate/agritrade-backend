release: python manage.py migrate --noinput
web: gunicorn --worker-tmp-dir /dev/shm myapiproject.wsgi:application --bind 0.0.0.0:$PORT --workers 2
