from django.contrib import admin
from .models import Hosts, HostChecks, Thresholds, Historical, Sla, EventLog, SlaLog, ErrorLog, Metadata, Trap, Template
from reversion.admin import VersionAdmin


class HostsAdmin(VersionAdmin):
    fields = ('name', 'address', 'community', 'enabled', 'note', )
    list_display = ('name', 'address', 'community', 'enabled', 'note',)
    list_display_links = ('name', 'address', 'community',)
    list_filter = ('community', 'enabled', )
    search_fields = ['name', 'address', 'community', 'enabled', 'note',]


class HostChecksAdmin(VersionAdmin):
    fields = ('name', 'verbosename', 'hosts', 'checktype', 'interval', 'arg', 'unit', 'quotient', 'threshold', 'sla', 'allhosts', 'colorizesla', 'status', 'statsinterval', 'enabled', 'note', )
    list_display = ('name', 'verbosename', 'checktype', 'interval', 'arg', 'unit', 'quotient', 'allhosts', 'colorizesla', 'status', 'statsinterval', 'enabled', )
    list_display_links = ('name', 'verbosename',)
    list_filter = ('hosts', 'checktype', 'interval', 'unit', 'quotient', 'threshold', 'sla', 'allhosts', 'colorizesla', 'status', 'statsinterval', 'enabled', )
    search_fields = ['name', 'verbosename', 'checktype', 'interval', 'arg', 'unit', 'quotient', 'allhosts', 'colorizesla', 'status', 'statsinterval', 'enabled', 'note', ]



class HistoricalAdmin(VersionAdmin):
    fields = ('hostcheck', 'host', 'value', 'data', 'timestamp', 'exported', )
    date_hierarchy = 'timestamp'
    list_display = ('hostcheck', 'host', 'value', 'timestamp', 'exported', )
    list_display_links = ('hostcheck', 'host', 'value', 'timestamp',)
    list_filter = ('hostcheck', 'host', 'value', 'timestamp', 'exported', )
    readonly_fields = ('hostcheck', 'host', 'value', 'data', 'timestamp', 'exported', )
    search_fields = ['value', 'data', 'timestamp',]


class ThresholdsAdmin(VersionAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'verbosename','type', 'note', 'enabled')
        }),
        ('Alerting options', {
            'fields': ('critgroups', 'crittpl', 'critrepeat', 'okgroups', 'oktpl', 'warngroups', 'warntpl', 'warnrepeat', 'errgroups', 'errtpl', )
        }),
        ('Fill *ONLY* one of the three sections below: INT / BOOL / STR', {
            'fields': ('lowwarn', 'lowcrit', 'highwarn', 'highcrit', 'boolgood', 'boolbad', 'boolwarn','strgood', 'strwarn', 'strbad'),
        }),
    )
    list_display = ('name', 'verbosename', 'type', 'note', 'enabled')
    list_display_links = ('name', 'verbosename')
    list_filter = ('enabled', 'critgroups', 'warngroups', 'crittpl', 'warntpl', 'oktpl', 'okgroups', 'warnrepeat')
    search_fields = ['name', 'verbosename','type', 'note', 'enabled']

class SlaAdmin(VersionAdmin):
    fieldsets = (
        (None, {
             'fields': ('name', 'verbosename', 'currentvalue', 'status', 'critical', 'allchecks', 'enabled', 'note', 'data')
        }),
        ('Alerting options', {
            'fields': ('critgroups', 'crittpl', 'warngroups', 'warntpl','okgroups', 'oktpl')
        }),        
    )
    readonly_fields = ('currentvalue',)
    list_display = ('name', 'currentvalue', 'status', 'critical', 'allchecks', 'enabled',)
    list_display_links = ('name', 'currentvalue', 'status', 'critical')
    list_filter = ('status', 'critgroups', 'warngroups', 'crittpl', 'warntpl', 'oktpl', 'okgroups', 'allchecks', 'enabled',)
    search_fields = ['name', 'verbosename', 'currentvalue', 'status', 'critical', 'data', 'allchecks', 'enabled', 'note']


class EventLogAdmin(VersionAdmin):
    fields = ('hostcheck', 'host', 'event', 'sla', 'value', 'data', 'timestamp', 'threshold', )
    date_hierarchy = 'timestamp'
    list_display = ('hostcheck', 'host', 'event', 'sla', 'value', 'timestamp', 'threshold',)
    list_display_links = ('hostcheck', 'host', 'event', 'sla', 'value', 'timestamp', 'threshold',)
    list_filter = ('hostcheck', 'host', 'event', 'sla', 'timestamp', 'threshold',)
    readonly_fields = ('hostcheck', 'host', 'event', 'sla', 'value', 'data', 'timestamp', 'threshold')
    search_fields = ['hostcheck', 'host', 'event', 'sla', 'value', 'data', 'timestamp', 'threshold',]


class SlaLogAdmin(VersionAdmin):
    fields = ('event', 'sla', 'timestamp', 'data', )
    date_hierarchy = 'timestamp'
    list_display = ('event', 'sla', 'timestamp',)
    list_display_links = ('event', 'sla', 'timestamp', )
    list_filter = ('event', 'sla', 'timestamp',)
    readonly_fields = ('event', 'sla', 'timestamp', 'data',)
    search_fields = ['event', 'sla', 'timestamp', 'data',]


class ErrorLogAdmin(VersionAdmin):
    fields = ('hostcheck', 'host', 'event', 'error', 'value', 'data', 'timestamp')
    date_hierarchy = 'timestamp'
    list_display = ('hostcheck', 'host', 'event', 'error', 'value', 'timestamp')
    list_display_links = ('hostcheck', 'host', 'event', 'error', 'value', 'timestamp')
    list_filter = ('hostcheck', 'host', 'event', 'timestamp')
    readonly_fields = ('hostcheck', 'host', 'event', 'error', 'value', 'data', 'timestamp')
    search_fields = ['hostcheck__name', 'host__name', 'event', 'error', 'value', 'data']

class MetadataAdmin(VersionAdmin):
    fields = ('key', 'data', 'timestamp')
    date_hierarchy = 'timestamp'
    list_display = ('key', 'data', 'timestamp')
    list_display_links = ('key',)
    list_filter = ('key', 'timestamp')
    readonly_fields = ('key', 'timestamp')
    search_fields = ['key', 'data', 'timestamp']


class TrapAdmin(VersionAdmin):
    fields = ('host', 'oid', 'value', 'timestamp')
    date_hierarchy = 'timestamp'
    list_display = ('oid', 'value', 'timestamp')
    list_display_links = ('oid',)
    list_filter = ('oid', 'timestamp')
    readonly_fields = ('host', 'oid', 'timestamp')
    search_fields = ['oid', 'value', 'timestamp']


class TemplateAdmin(VersionAdmin):
    fields = ('name', 'verbosename', 'obj', 'event', 'subject', 'content')
    date_hierarchy = 'timestamp'
    list_display = ('name', 'verbosename', 'obj', 'event', 'timestamp')
    list_display_links = ('name',)
    list_filter = ('timestamp','obj', 'event')
    readonly_fields = ('timestamp',)
    search_fields = ['name', 'verbosename', 'obj', 'event', 'content', 'subject']


admin.site.register(Hosts, HostsAdmin)
admin.site.register(HostChecks, HostChecksAdmin)
admin.site.register(Thresholds, ThresholdsAdmin)
admin.site.register(Historical, HistoricalAdmin)
admin.site.register(Sla, SlaAdmin)
admin.site.register(EventLog, EventLogAdmin)
admin.site.register(SlaLog, SlaLogAdmin)
admin.site.register(ErrorLog, ErrorLogAdmin)
admin.site.register(Metadata, MetadataAdmin)
admin.site.register(Trap, TrapAdmin)
admin.site.register(Template, TemplateAdmin)