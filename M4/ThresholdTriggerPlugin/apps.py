from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ThresholdtriggerpluginConfig(AppConfig):
    name = 'M4.ThresholdTriggerPlugin'
    label = 'ThresholdTriggerPlugin'
    verbose_name = _('Trigger Plugin - Thresholds')
