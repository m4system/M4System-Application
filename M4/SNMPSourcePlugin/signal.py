from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from M4.System.models.models import Datapoint
from django_celery_beat.models import IntervalSchedule, PeriodicTask
import json
from pprint import pprint


@receiver(post_save, sender=Datapoint, dispatch_uid="setup_datapoint_task_snmp")
def setup_task(sender, instance, **kwargs):
    if instance.source.content_type.model == 'snmpsourceplugin':
        schedule = IntervalSchedule.objects.get(pk=1)
        # try:
        pprint(instance.datasource.custom_fields.filter(name="ip")[0])
        ptask = PeriodicTask.objects.update_or_create(
            name=instance.name,
            interval=schedule,
            task='snmp_source',
            kwargs=json.dumps({'oid': instance.source.content_object.oid, 'version': instance.source.content_object.version, 'datatype': instance.datatype, 'datasource': instance.datasource.custom_fields.filter(name="ip")[0].content, 'datapoint': instance.name})
        )

        # except Exception as e:
        #     print(e)
        # else:
        #     print("identical task exists")
        return ptask
    else:
        return True
