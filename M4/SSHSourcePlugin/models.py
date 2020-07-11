from django.db import models
from django.utils.translation import ugettext_lazy as _
from M4.System.models.base_models import BaseSourcePlugin


class SSHSourcePlugin(BaseSourcePlugin):
    shell = models.CharField(verbose_name=_('Remote Shell'), default='/bin/bash',
                             help_text=_('This is usually /bin/bash on linux.'),
                             max_length=256)
    content = models.CharField(verbose_name=_('The Script'), help_text=_(
        'Put the script content here.  It will be executed by the shell you select.'), max_length=4096,
                               default='echo 1')

    def fetch(self):
        return self

    fetch.short_description = _('fetch this SSH Source.')

    class Meta:
        verbose_name = _('Source: SSH')
        verbose_name_plural = _('Sources: SSH')

