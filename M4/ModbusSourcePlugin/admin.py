from django.contrib import admin

from M4.ModbusSourcePlugin.models import ModbusSourcePlugin


@admin.register(ModbusSourcePlugin)
class CheckModbusAdmin(admin.ModelAdmin):
    pass
