from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class SystemConfig(AppConfig):
    name = 'System'
    verbose_name = _('Configuration')
