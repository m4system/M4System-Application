from celery import shared_task
import sh
from M4.settings import DATAPOINT_TYPES
import os

@shared_task(bind=True, name='ssh_source')
def ssh_source(self, shell, content, datatype, datasource):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # debug = self.request
    print("here ssh")
    run = sh.Command(BASE_DIR + "/runthis.sh")
    return str(run(content))
