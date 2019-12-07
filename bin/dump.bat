c:\Python35\python.exe manage.py dumpdata auth.user auth.group -o fixtures\user.json
c:\Python35\python.exe manage.py dumpdata auth --natural-primary --natural-foreign -o fixtures\auth.json
c:\Python35\python.exe manage.py dumpdata djcelery -e=djcelery.taskmeta -o fixtures\djcelery.json
c:\Python35\python.exe manage.py dumpdata webview -o fixtures\webview.json
c:\Python35\python.exe manage.py dumpdata scheduler -e=scheduler.historical -o fixtures\scheduler.json