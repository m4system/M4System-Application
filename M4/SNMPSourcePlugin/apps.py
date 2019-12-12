from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class SnmpsourcepluginConfig(AppConfig):
    name = 'SNMPSourcePlugin'
    verbose_name = _('Source Plugin - SNMP')
