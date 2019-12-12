from django.contrib import admin

from M4.EmailAlertHookPlugin.models import EmailAlertHookPlugin, EmailTemplate


@admin.register(EmailAlertHookPlugin)
class EmailAlertHookPluginAdmin(admin.ModelAdmin):
    pass


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    pass
