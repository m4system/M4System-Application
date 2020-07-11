from django.contrib import admin

from M4.SNMPSourcePlugin.models import SNMPSourcePlugin


@admin.register(SNMPSourcePlugin)
class SNMPSourcePluginAdmin(admin.ModelAdmin):
    pass

