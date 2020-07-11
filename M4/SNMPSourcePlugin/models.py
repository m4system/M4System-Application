from django.db import models
from django.utils.translation import ugettext_lazy as _
from M4.System.models.base_models import BaseSourcePlugin
# from M4.SNMPSourcePlugin.tasks import SNMPSourceTask
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from M4.System.models.models import Datapoint
from django_celery_beat.models import IntervalSchedule, PeriodicTask
import json


class SNMPSourcePlugin(BaseSourcePlugin):
    VERSION_TYPES = (('1', 'Version 1'), ('2c', 'Version 2c'), ('3', 'Version 3'))
    oid = models.CharField(verbose_name=_('The OID'),
                           help_text=_('Enter the OID you wish to poll, in dotted number form.'), max_length=256)
    version = models.CharField(verbose_name=_('SNMP Version'),
                               help_text=_('Select the SNMP version the remote assets is configured to use.'),
                               choices=VERSION_TYPES, max_length=8, default='1')
    # community = string
    # query = choice of get, walk
    # interval = time between request

    def fetch(self):
        return self

    fetch.short_description = _('Fetch this SNMP source.')

    class Meta:
        verbose_name = _('SNMP Source')
        verbose_name_plural = _('SNMP Sources')


@receiver(post_save, sender=Datapoint, dispatch_uid="setup_datapoint_task")
def setup_task(sender, instance, **kwargs):
    source = SNMPSourcePlugin.objects.get(pk=instance.source.object_id)
    schedule = IntervalSchedule.objects.get(pk=1)
    # try:
    ptask = PeriodicTask.objects.update_or_create(
        name=instance.name,
        interval=schedule,
        task='snmp_source',
        kwargs=json.dumps({'oid': source.oid, 'version': source.version})
    )
    # except Exception as e:
    #     print(e)
    # else:
    #     print("identical task exists")
    return ptask

