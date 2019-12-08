START /B c:\Python35\python.exe manage.py celery -A scheduler worker --heartbeat-interval 10 -E -c1

START /B c:\Python35\python.exe manage.py celery -A scheduler beat

START /B c:\Python35\python.exe manage.py celerycam --frequency=10.0

