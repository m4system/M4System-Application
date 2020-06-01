from django.conf.urls import url
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

# from M4.DashboardDisplayPlugin.views import index, dashboard
from M4.DashboardDisplayPlugin.urls import urlpatterns
from M4.System.plugins import FrontEndPlugin


class DefaultDashboardFrontEnd(FrontEndPlugin):
    title = _('M4System Default Dashboard')
    name = 'dashboard'

    urls = urlpatterns

    def get_absolute_url(self):
        return reverse('dashboard-index')
