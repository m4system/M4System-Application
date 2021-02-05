from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group
from reversion.admin import VersionAdmin

from .models import UserProfile, Widgets, UserView, UIMsg


# add all admin with reversion
class UserProfileAdmin(VersionAdmin):
    pass


class WidgetsAdmin(VersionAdmin):
    fields = ('name', 'verbosename', 'active', 'hostcheck', 'host', 'unit', 'template', 'note',)
    list_display = ('name', 'verbosename', 'active', 'unit', 'template', 'note',)
    list_display_links = ('name', 'verbosename',)
    list_filter = ('name', 'verbosename', 'active', 'hostcheck', 'host', 'unit', 'template',)
    search_fields = ['name', 'verbosename', 'note', 'unit', ]


class UserViewAdmin(VersionAdmin):
    pass


class UIMsgAdmin(VersionAdmin):
    pass


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Widgets, WidgetsAdmin)
admin.site.register(UserView, UserViewAdmin)
admin.site.register(UIMsg, UIMsgAdmin)

admin.site.unregister(User)


@admin.register(User)
class MyUserAdmin(VersionAdmin, UserAdmin):
    pass


admin.site.unregister(Group)


@admin.register(Group)
class MyGroupAdmin(VersionAdmin, GroupAdmin):
    pass


# from reversion.helpers import patch_admin
# from djcelery.models import PeriodicTask, IntervalSchedule, CrontabSchedule
# from djcelery.admin import PeriodicTaskAdmin

# Add reversion to djcelery
# admin.site.unregister(PeriodicTask)


# @admin.register(PeriodicTask)
# class MyPeriodicTaskAdmin(VersionAdmin, PeriodicTaskAdmin):
#     search_fields = ['name', ]
#     pass
#
#
# admin.site.unregister(IntervalSchedule)
#
#
# @admin.register(IntervalSchedule)
# class MyIntervalScheduleAdmin(VersionAdmin):
#     pass
#
#
# admin.site.unregister(CrontabSchedule)
#
#
# @admin.register(CrontabSchedule)
# class MyCrontabScheduleAdmin(VersionAdmin):
#     pass


# Ovverride the default text in the admin
admin.site.site_header = 'globo.tech'
admin.site.site_title = 'Monitoring'
