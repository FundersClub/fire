web: cd src && gunicorn firebot.wsgi --log-file -
worker: cd src && celery -A firebot worker
beat: cd src && celery -A firebot beat
