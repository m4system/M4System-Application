from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from M4.System.models.models import DisplayPlugin, HookPlugin, SourcePlugin, TriggerPlugin
from M4.settings import DATAPOINT_TYPES
from django_celery_beat.models import IntervalSchedule, PeriodicTask
import json


class BaseDisplayPlugin(models.Model):
    name = models.SlugField(_('Name'), max_length=64, unique=True, blank=True,
                            help_text=_('Internal name, leave empty to autopopulate.'))
    title = models.CharField(_('Title'), max_length=256, help_text=_('Verbose name for display purposes'))
    display_instance = GenericRelation(DisplayPlugin, related_query_name='displayplugin')

    def render_widget(self, data_type):
        raise NotImplementedError

    def save(self, *args, **kwargs):
        if self.name == '':
            self.name = slugify(self.title)
        super(BaseDisplayPlugin, self).save(*args, **kwargs)
        self.display_instance.update_or_create(object_id=self.pk, defaults={
            'name': '({}) {}'.format(self.display_instance.content_type.model, self.name)})

    def delete(self, *args, **kwargs):
        self.display_instance.all().delete()
        super(BaseDisplayPlugin, self).delete(*args, **kwargs)

    def __str__(self):
        return str(self.name)

    class Meta:
        abstract = True
        ordering = ['-name']


class BaseHookPlugin(models.Model):
    name = models.SlugField('Name', max_length=64, unique=True, blank=True,
                            help_text=_('Internal name, leave empty to autopopulate.'))
    title = models.CharField('Title', max_length=256, help_text=_('Verbose name for display purposes'))
    hook_instance = GenericRelation(HookPlugin, related_query_name='hookplugin')

    def execute(self):
        raise NotImplementedError

    def save(self, *args, **kwargs):
        if self.name == '':
            self.name = slugify(self.title)
        super(BaseHookPlugin, self).save(*args, **kwargs)
        self.hook_instance.update_or_create(object_id=self.pk, defaults={
            'name': '({}) {}'.format(self.hook_instance.content_type.model, self.name)})

    def delete(self, *args, **kwargs):
        self.hook_instance.all().delete()
        super(BaseHookPlugin, self).delete(*args, **kwargs)

    def __str__(self):
        return str(self.name)

    class Meta:
        abstract = True
        ordering = ['-name']


class BaseSourcePlugin(models.Model):
    name = models.SlugField('Name', max_length=64, unique=True, blank=True,
                            help_text=_('Internal name, leave empty to autopopulate.'))
    title = models.CharField('Title', max_length=256, help_text=_('Verbose name for display purposes'))
    source_instance = GenericRelation(SourcePlugin, related_query_name='sourceplugin')

    def fetch(self):
        raise NotImplementedError

    def task(self):
        raise NotImplementedError

    def save(self, *args, **kwargs):
        if self.name == '':
            self.name = slugify(self.title)
        super(BaseSourcePlugin, self).save(*args, **kwargs)
        self.source_instance.update_or_create(object_id=self.pk, defaults={
            'name': '({}) {}'.format(self.source_instance.content_type.name, self.name)})

    def delete(self, *args, **kwargs):
        self.source_instance.all().delete()
        super(BaseSourcePlugin, self).delete(*args, **kwargs)

    def __str__(self):
        return str(self.name)

    class Meta:
        abstract = True
        ordering = ['-name']


class BaseTriggerPlugin(models.Model):
    name = models.SlugField('Name', max_length=64, unique=True, blank=True,
                            help_text=_('Internal name, leave empty to autopopulate.'))
    title = models.CharField('Title', max_length=256, help_text=_('Verbose name for display purposes'))
    datatype = models.CharField('Data Type', max_length=8, choices=DATAPOINT_TYPES, default='string',
                                help_text='The data datatype this trigger supports.')
    trigger_instance = GenericRelation(TriggerPlugin, related_query_name='triggerplugin')

    def trigger(self):
        raise NotImplementedError

    def set_datatype(self):
        raise NotImplementedError

    def save(self, *args, **kwargs):
        if self.name == '':
            self.name = slugify(self.title)
        super(BaseTriggerPlugin, self).save(*args, **kwargs)
        self.trigger_instance.update_or_create(object_id=self.pk, defaults={
            'name': '({}) {}'.format(self.trigger_instance.content_type.model, self.name),
            'datatype': self.datatype})

    def delete(self, *args, **kwargs):
        self.trigger_instance.all().delete()
        super(BaseTriggerPlugin, self).delete(*args, **kwargs)

    def __str__(self):
        return str(self.name)

    class Meta:
        abstract = True
        ordering = ['-name']


# class BaseTask(object):
#     """
#     Not a base_model, but we don't have other base clases, so it seems to fit better here.
#
#     Plugin celery task should inherit from this base object in order to interact properly with the system.
#     """
#
#     def __init__(self, task=None, params={}):
#         self.task = task
#         self.params = params
#
#     def schedule(self, **kwargs):
#         """
#         add this task to the celery tasks
#
#         :return: success or failure
#         """
#         # find the task, create it if it doesnt exist.
#         schedule = IntervalSchedule.objects.get(pk=1)
#         ptask = PeriodicTask.objects.update_or_create(
#             name=self.params['datapoint'].objects.all()[0].name,
#             interval=schedule,
#             task=self.name,
#             args=json.dumps([self.task.version, self.task.oid])
#         )
#         return ptask
#
#     def unschedule(self):
#         """
#         remove this task to the celery tasks
#
#         :return: success or failure
#         """
#         pass
#
#     def run(self, name, param=None):
#         """
#         Execute the task with the set parameters.
#
#         :return: the output from the task.
#         """
#         raise NotImplementedError
#
#     def get_task_name(self):
#         return self.name
#
#     def get_task_info(self):
#         return self.name
#
#     def get_task_params(self):
#         return self.name
#
#     class Meta:
#         abstract = True
