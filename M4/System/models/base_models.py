from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from M4.System.models.models import DisplayPlugin, HookPlugin, SourcePlugin, TriggerPlugin
from M4.settings import DATAPOINT_TYPES


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
            'name': '(' + self.display_instance.content_type.model + ') ' + self.name})

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
            'name': '(' + self.hook_instance.content_type.model + ') ' + self.name})

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

    def poll(self):
        raise NotImplementedError

    def save(self, *args, **kwargs):
        if self.name == '':
            self.name = slugify(self.title)
        super(BaseSourcePlugin, self).save(*args, **kwargs)
        self.source_instance.update_or_create(object_id=self.pk, defaults={
            'name': '(' + self.source_instance.content_type.model + ') ' + self.name})

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
            'name': '(' + self.trigger_instance.content_type.model + ') ' + self.name,
            'datatype': self.datatype})

    def delete(self, *args, **kwargs):
        self.trigger_instance.all().delete()
        super(BaseTriggerPlugin, self).delete(*args, **kwargs)

    def __str__(self):
        return str(self.name)

    class Meta:
        abstract = True
        ordering = ['-name']
