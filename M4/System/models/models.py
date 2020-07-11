from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from M4.settings import DATAPOINT_TYPES
from djangoplugins.fields import PluginField


class SourcePlugin(models.Model):
    name = models.SlugField('Name')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):  # __unicode__ on Python 2
        return self.name

    class Meta:
        ordering = ['-name']


class HookPlugin(models.Model):
    name = models.SlugField('Name')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):  # __unicode__ on Python 2
        return self.name

    class Meta:
        ordering = ['-name']


class DisplayPlugin(models.Model):
    name = models.SlugField('Name')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):  # __unicode__ on Python 2
        return self.name

    class Meta:
        ordering = ['-name']


class TriggerPlugin(models.Model):
    name = models.SlugField('Name')
    datatype = models.CharField(max_length=8, choices=DATAPOINT_TYPES, default='string', verbose_name=_('Data type'),
                                help_text=_('The data datatype this trigger supports.'))
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):  # __unicode__ on Python 2
        return self.name

    class Meta:
        ordering = ['-name']


class CustomField(models.Model):
    name = models.SlugField('Name')
    content = models.CharField('Content', max_length=4096)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):  # __unicode__ on Python 2
        return self.name

    class Meta:
        verbose_name = _('Custom Field')
        verbose_name_plural = _('Custom Fields')
        ordering = ['-name']


class Datapoint(models.Model):
    """
    This model stores the datapoints that interests us,
    """
    name = models.SlugField(max_length=64, unique=True, blank=True, verbose_name=_('Datapoint Name'),
                            help_text=_('Internal name for the Datapoint.'))
    title = models.CharField(max_length=256, verbose_name=_('Datapoint Title'),
                             help_text=_('Verbose name for display purposes'))
    datatype = models.CharField(max_length=8, choices=DATAPOINT_TYPES, default='string', verbose_name=_('Data type'),
                                help_text=_('The internal type for this datapoint.'))
    datasource = models.ForeignKey('Asset', related_name='asset', verbose_name=_('Data Source'), blank=True, null=True, help_text=_(
        'The asset selected here will be used to for polling this datapoint.'), on_delete=models.CASCADE)
    source = models.ForeignKey(SourcePlugin, related_name='source', verbose_name=_('Source Plugin'), help_text=_(
        'Select the plugin configuration that will be used to source the data for this datapoint. If the list is empty, it means you need to create a plugin configuration first.'), on_delete=models.CASCADE)
    trigger = models.ForeignKey(TriggerPlugin, blank=True, null=True, related_name='trigger',
                                verbose_name=_('Trigger Plugin'), help_text=_(
            'Select the plugin configuration that will be used to decide if the datapoint is failing. If the list is empty, it means you need to create a plugin configuration first.'), on_delete=models.CASCADE)
    hook = models.ForeignKey(HookPlugin, blank=True, null=True, related_name='hook', verbose_name=_('Hook Plugin'),
                             help_text=_(
                                 'Select the plugin configuration that will be executed when the status of the datapoint changes. If the list is empty, it means you need to create a plugin configuration first.'), on_delete=models.CASCADE)
    display = models.ForeignKey(DisplayPlugin, blank=True, null=True, related_name='display',
                                verbose_name=_('Display Plugin'), help_text=_(
            'Select the plugin configuration that will be used to display this datapoint on the frontends. If the list is empty, it means you need to create a plugin configuration first.'), on_delete=models.CASCADE)
    custom_fields = GenericRelation(CustomField, related_query_name='datapoint', verbose_name=_('Custom Fields'),
                                    help_text=_('You can set custom fields for complex scenarios.'))

    def save(self, *args, **kwargs):
        if self.name == '':
            self.name = slugify(self.title)
        super(Datapoint, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = _('Data Point')
        verbose_name_plural = _('Data Points')
        ordering = ['-name']


class Asset(models.Model):
    """
    This model stores the assets that we will be managing.
    related to :model:`System.Datapoint`
    """
    name = models.SlugField(max_length=64, unique=True, blank=True, verbose_name=_('Asset Name'),
                            help_text=_('Internal name for the Asset.'))
    title = models.CharField(max_length=256, verbose_name=_('Asset Title'),
                             help_text=_('Verbose name for display purposes'))
    datapoints = models.ManyToManyField(Datapoint, blank=True, verbose_name=_('Datapoints which link to this assets.'),
                                        help_text=_(
                                            'Assign datapoints to assets here.  You can then assign an SLA and start monitoring availibility.'))
    custom_fields = GenericRelation(CustomField, related_query_name='asset', verbose_name=_('Custom Fields'),
                                    help_text=_('You can set custom fields for complex scenarios.'))

    def save(self, *args, **kwargs):
        if self.name == '':
            self.name = slugify(self.title)
        super(Asset, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = _('Asset')
        verbose_name_plural = _('Assets')
        ordering = ['-name']


class Sla(models.Model):
    """
    This model stores SLA data,
    related to :model:`System.Asset`
    related to :model:`System.Datapoint`
    """
    name = models.SlugField(max_length=64, unique=True, blank=True, verbose_name=_('SLA Name'),
                            help_text=_('Internal name for the SLA.'))
    title = models.CharField(max_length=256, verbose_name=_('SLA Title'),
                             help_text=_('Verbose name for display purposes'))
    assets = models.ManyToManyField(Asset, verbose_name=_('Assigned Assets'),
                                    help_text=_('Assets assigned to this SLA.'))
    datapoints = models.ManyToManyField(Datapoint, verbose_name=_('Assigned Datapoints'),
                                        help_text=_('Datapoints assigned to this SLA.'))
    custom_fields = GenericRelation(CustomField, related_query_name='sla', verbose_name=_('Custom Fields'),
                                    help_text=_('You can set custom fields for complex scenarios.'))

    def save(self, *args, **kwargs):
        if self.name == '':
            self.name = slugify(self.title)
        super(Sla, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = _('SLA')
        verbose_name_plural = _('SLAs')
        ordering = ['-name']


class Setting(models.Model):
    key = models.SlugField(_('Name'), max_length=64, unique=True, help_text=_('Setting name'))
    value = models.CharField(_('Value'), max_length=1024, help_text=_('Setting value'))

    def __str__(self):
        return str(self.key)

    class Meta:
        verbose_name = _('Setting')
        verbose_name_plural = _('Settings')
        ordering = ['-key']


class Frontend(models.Model):
    """
    This model stores FrontEnd data,
    """
    from M4.System.plugins import FrontEndPlugin
    name = models.SlugField(_('Name'), max_length=64, unique=True, blank=True,
                            help_text=_('Internal name for the frontend.'))
    title = models.CharField(_('Title'), max_length=256, help_text=_('Verbose name for display purposes.'))
    plugin = PluginField(FrontEndPlugin, editable=True)

    def get_absolute_url(self):
        return self.plugin.get_plugin().get_absolute_url(self)

    def save(self, *args, **kwargs):
        if self.name == '':
            self.name = slugify(self.title)
        super(Frontend, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = _('Front-End')
        verbose_name_plural = _('Front-Ends')
        ordering = ['-name']
