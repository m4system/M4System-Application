from django.db import models

from M4.System.models.base_models import BaseTriggerPlugin
from M4.settings import DATAPOINT_TYPES


class NumberThresholdTriggerPlugin(BaseTriggerPlugin):
    datatype = models.CharField('Data Type', max_length=8, choices=DATAPOINT_TYPES, default='number', editable=False,
                                help_text='The data datatype this trigger supports.')
    number_low = models.CharField('Alert When Number Under', blank=True, max_length=4096)
    number_high = models.CharField('Alert When Number Above', blank=True, max_length=4096)

    def set_datatype(self):
        self.datatype = 'number'

    def trigger(self):
        return self

    def save(self, *args, **kwargs):
        self.set_datatype()
        super(NumberThresholdTriggerPlugin, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Number Threshold'
        verbose_name_plural = 'Number Thresholds'


class StringThresholdTriggerPlugin(BaseTriggerPlugin):
    datatype = models.CharField('Data Type', max_length=8, choices=DATAPOINT_TYPES, default='string', editable=False,
                                help_text='The data datatype this trigger supports.')
    string_good = models.CharField('Alert When String Does Not Match', blank=True, max_length=4096)
    string_bad = models.CharField('Alert When String Matches', blank=True, max_length=4096)

    def set_datatype(self):
        self.datatype = 'string'

    def trigger(self):
        return self

    def save(self, *args, **kwargs):
        self.set_datatype()
        super(StringThresholdTriggerPlugin, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'String Threshold'
        verbose_name_plural = 'String Thresholds'


class BooleanThresholdTriggerPlugin(BaseTriggerPlugin):
    datatype = models.CharField('Data Type', max_length=8, choices=DATAPOINT_TYPES, default='boolean', editable=False,
                                help_text='The data datatype this trigger supports.')
    boolean_good = models.CharField('Alert When Boolean Does Not Match', blank=True, max_length=4096)
    boolean_bad = models.CharField('Alert When Boolean Matches', blank=True, max_length=4096)

    def set_datatype(self):
        self.datatype = 'boolean'

    def trigger(self):
        return self

    def save(self, *args, **kwargs):
        self.set_datatype()
        super(BooleanThresholdTriggerPlugin, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Boolean Threshold'
        verbose_name_plural = 'Boolean Thresholds'
