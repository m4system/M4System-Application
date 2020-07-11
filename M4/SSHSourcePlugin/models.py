from django.db import models
from django.utils.translation import ugettext_lazy as _
from M4.System.models.base_models import BaseSourcePlugin
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from M4.System.models.models import Datapoint
from django_celery_beat.models import IntervalSchedule, PeriodicTask
import json


class SSHSourcePlugin(BaseSourcePlugin):
    shell = models.CharField(verbose_name=_('Remote Shell'), default='/bin/bash',
                             help_text=_('This is usually /bin/bash on linux.'),
                             max_length=256)
    content = models.CharField(verbose_name=_('The Script'), help_text=_(
        'Put the script content here.  It will be executed by the shell you select.'), max_length=4096,
                               default='echo 1')

    def fetch(self):
        return self

    fetch.short_description = _('fetch this SSH Source.')

    class Meta:
        verbose_name = _('Source: SSH')
        verbose_name_plural = _('Sources: SSH')


@receiver(post_save, sender=Datapoint, dispatch_uid="setup_datapoint_task_ssh")
def setup_task(sender, instance, **kwargs):
    if instance.source.content_type.model == 'sshsourceplugin':
        schedule = IntervalSchedule.objects.get(pk=1)
        # try:
        ptask = PeriodicTask.objects.update_or_create(
            name=instance.name,
            interval=schedule,
            task='ssh_source',
            kwargs=json.dumps({'shell': instance.source.content_object.shell, 'content': instance.source.content_object.content, 'datatype': instance.datatype, 'datasource': instance.datasource.custom_fields.filter(name="ip")})
        )
        # except Exception as e:
        #     print(e)
        # else:
        #     print("identical task exists")
        return ptask
    else:
        return True
