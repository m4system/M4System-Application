from django.db import models
from django.utils.translation import ugettext_lazy as _

from M4.System.models.base_models import BaseSourcePlugin


class ModbusSourcePlugin(BaseSourcePlugin):
    REGISTER_TYPES = (('int16', _('Integer')), ('uint16', _('Unsigned Integer')), ('float', _('Float')))
    ENDIAN_TYPES = (('little', _('Little Endian')), ('big', _('Big Endian')))
    start = models.CharField(verbose_name=_('Start Register'),
                             help_text=_('The first register where we will start polling.'), max_length=4096)
    count = models.CharField(verbose_name=_('Amount of registers to poll sequentially.'),
                             help_text=_('This should match your data type.'), max_length=4096)
    remote_type = models.CharField(verbose_name=_('Remote Data Type'), help_text=_(
        'Select the data format which matches the documentation of the device you are polling.'), max_length=32,
                                   choices=REGISTER_TYPES, default='int16')
    byte_endian = models.CharField(verbose_name=_('Byte Endian'),
                                   help_text=_('Little Endian is least significant bit first.'), max_length=8,
                                   choices=ENDIAN_TYPES, default='little')
    word_endian = models.CharField(verbose_name=_('Word Endian'), help_text=_(
        'When there are more than 1 count (i.e. data types bigger than 16bit), this decides the order they are processed.'),
                                   max_length=8, choices=ENDIAN_TYPES, default='little')

    def fetch(self):
        return self

    fetch.short_description = _('fetch this modbus source.')

    class Meta:
        verbose_name = _('Modbus Source')
        verbose_name_plural = _('Modbus Sources')
