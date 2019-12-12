from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class EmailalerthookpluginConfig(AppConfig):
    name = 'EmailAlertHookPlugin'
    verbose_name = _('Hook Plugin - Email Alerting')
