from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class DashboarddisplaypluginConfig(AppConfig):
    name = 'M4.DashboardDisplayPlugin'
    label = 'DashboardDisplayPlugin'
    verbose_name = _('Display Plugin - Default Dashboard')
