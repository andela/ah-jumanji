release: ./release-tasks.sh
web: gunicorn authors.wsgi —-log-file -
worker: python manage.py qcluster
