from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class SnmpsourcepluginConfig(AppConfig):
    name = 'M4.SNMPSourcePlugin'
    label = 'SNMPSourcePlugin'
    verbose_name = _('Source Plugin - SNMP')

    def ready(self):
        import M4.SNMPSourcePlugin.signal  #noqa
