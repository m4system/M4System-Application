from django.db import models
from django.utils.translation import ugettext_lazy as _

from M4.System.models.base_models import BaseSourcePlugin


class SNMPSourcePlugin(BaseSourcePlugin):
    VERSION_TYPES = (('1', 'Version 1'), ('2c', 'Version 2c'), ('3', 'Version 3'))
    oid = models.CharField(verbose_name=_('The OID'),
                           help_text=_('Enter the OID you wish to poll, in dotted number form.'), max_length=256)
    version = models.CharField(verbose_name=_('SNMP Version'),
                               help_text=_('Select the SNMP version the remote assets is configured to use.'),
                               choices=VERSION_TYPES, max_length=8, default='1')

    def poll(self):
        return self

    poll.short_description = _('Poll this SNMP source.')

    class Meta:
        verbose_name = _('SNMP Source')
        verbose_name_plural = _('SNMP Sources')
