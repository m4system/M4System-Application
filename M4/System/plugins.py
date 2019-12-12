from django.conf.urls import url
from django.core.urlresolvers import reverse

from M4.System.views import index
from djangoplugins.point import PluginPoint


class FrontEndPlugin(PluginPoint):
    urls = [
        url(r'^$', index, name='index'),
    ]

    def get_absolute_url(self):
        return reverse('index')
