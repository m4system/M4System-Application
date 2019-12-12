from django.db import models
from django.utils.translation import ugettext_lazy as _

from M4.System.models.base_models import BaseDisplayPlugin


class DashboardDisplayPlugin(BaseDisplayPlugin):
    logo = models.CharField(verbose_name=_('Company Logo'),
                            help_text=_('Enter the path to your logo relative to /static/'), blank=True, max_length=256)
    slogan = models.CharField(verbose_name=_('Company Slogan'), help_text=_('Tag Line on the dashboard.'), blank=True,
                              max_length=1024)
    template = models.CharField(verbose_name=_('Template Prefix'),
                                help_text=_('On-disk template prefix.  There must be one template per type.'),
                                blank=True, max_length=128)

    def render_widget(self, data_type):
        return self.template + '_' + data_type + '.html'

    class Meta:
        verbose_name = _('Dashboard')
        verbose_name_plural = _('Dashboard Widgets')
