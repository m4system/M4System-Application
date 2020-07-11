from celery import shared_task
import sh
from M4.settings import DATAPOINT_TYPES
import os
from M4.System.signals import post_fetch



@shared_task(bind=True, name='ssh_source')
def ssh_source(self, shell, content, datatype, datasource, datapoint):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # debug = self.request
    print("here ssh")
    run = sh.Command(BASE_DIR + "/runthis.sh")
    retval = str(run(content))
    post_fetch.send(sender='M4.SSHSourcePlugin', retval=retval, datatype=datatype, datapoint=datapoint)
    return retval
