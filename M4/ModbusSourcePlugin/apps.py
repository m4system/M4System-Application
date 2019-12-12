from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ModbussourcepluginConfig(AppConfig):
    name = 'ModbusSourcePlugin'
    verbose_name = _('Source Plugin - Modbus')
