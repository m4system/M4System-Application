from django.contrib import admin

from M4.DashboardDisplayPlugin.models import DashboardDisplayPlugin


@admin.register(DashboardDisplayPlugin)
class WidgetBasicAdmin(admin.ModelAdmin):
    pass
