START /B c:\Python35\python.exe manage.py celery -A scheduler worker --heartbeat-interval 10 -E -l debug -f logs\worker.log -c1
START /B c:\Python35\python.exe manage.py celery -A scheduler beat -f logs\beat.log -l debug
START /B c:\Python35\python.exe manage.py celerycam --frequency=10.0 -f logs\cam.log -l debug