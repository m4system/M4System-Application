from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class SystemConfig(AppConfig):
    name = 'System'
    verbose_name = _('Configuration')

    # def ready(self):
    #     import M4.System.signals     #noqa

