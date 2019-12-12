from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class SshsourcepluginConfig(AppConfig):
    name = 'SSHSourcePlugin'
    verbose_name = _('Source Plugin - SSH')
