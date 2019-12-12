from django.contrib import admin

from M4.ThresholdTriggerPlugin.models import NumberThresholdTriggerPlugin, StringThresholdTriggerPlugin, \
    BooleanThresholdTriggerPlugin


@admin.register(NumberThresholdTriggerPlugin)
class NumberThresholdTriggerPluginAdmin(admin.ModelAdmin):
    pass


@admin.register(StringThresholdTriggerPlugin)
class StringThresholdTriggerPluginAdmin(admin.ModelAdmin):
    pass


@admin.register(BooleanThresholdTriggerPlugin)
class BooleanThresholdTriggerPluginAdmin(admin.ModelAdmin):
    pass
