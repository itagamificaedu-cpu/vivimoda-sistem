web: gunicorn confec_system.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
worker: celery -A confec_system worker --loglevel=info --concurrency=2
beat: celery -A confec_system beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
