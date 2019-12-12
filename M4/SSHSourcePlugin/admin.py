from django.contrib import admin

from M4.SSHSourcePlugin.models import SSHSourcePlugin


@admin.register(SSHSourcePlugin)
class SSHSourcePluginAdmin(admin.ModelAdmin):
    pass
