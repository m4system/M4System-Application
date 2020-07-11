from celery import shared_task
# from M4.System.models.base_models import BaseTask


@shared_task(bind=True, name='snmp_source')
def snmp_source(self, params):
    # do snmp get here
    for i in [params]:
        print(repr(i))
    print("here")

    return self.name
