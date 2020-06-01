from django.contrib.auth.models import User, Group
from django.db import models
# from django.template import loader, Context
from django.template.loader import render_to_string


# FIXME: to remove when not longer using sqlite
from django.db.backends.sqlite3.features import DatabaseFeatures

# File "djcelery/db.py", line 52, in commit_on_success
# if connection.features.autocommits_when_autocommit_is_off:
# WARNING/MainProcess] AttributeError: 'DatabaseFeatures' object has no attribute 'autocommits_when_autocommit_is_off'

# So hardcoded the attribute here (doing it elsewhere would cause a crash,
# forcing an import of django.db.models too early causes a circular import problem)
from M4.System.tools import getMetadata

DatabaseFeatures.autocommits_when_autocommit_is_off = True


# User profile for the webui used to store info
class UserProfile(models.Model):
    """
    This model stores the user profile and his credentials, related to :model:`auth.User`.
    * We need to add user timezone eventually
    * We need to add a signal handler for the automated creation of the profile when a new user is created
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    loggedin = models.BooleanField('Currently logged-in.', default=False,
                                   help_text='Is this user currentely logged-in ?')
    notifemail = models.EmailField('Notification Email', blank=True, null=True, default=None,
                                   help_text='Fill this field to receive email alerts')
    notifcallback = models.URLField('Notification URL', max_length=1024, null=True, blank=True,
                                    help_text='Fill this field to receive POST callbacks to the specified URL')
    prefs = models.CharField('Settings', max_length=4096, blank=True,
                             help_text='JSON Object containing all of the UI\'s settings.')

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = 'User profile'
        verbose_name_plural = 'Users profiles Editor'
        permissions = (
            ("view_traps", "Can see received  traps"),
            ("silence_check", "Can silence a check"),
            ("view_sla", "Can view the SLA window"),
            ("view_slalog", "Can view the SLA log window"),
            ("view_thresholdlog", "Can view the threshold log window"),
            ("view_notifs", "Can receive notifications"),
        )


# User profile for the webui used to store info
class Widgets(models.Model):
    from M4.scheduler.models import Hosts, HostChecks
    """
    This model stores the widgets to display, related to :model:`scheduler.HostChecks` and :model:`scheduler.Hosts`
    """
    TEMPLATE_CHOICES = (('snmpgetint', 'SNMP Integer Check'), ('snmpgetintgraph', 'SNMP Integer Graph'),
                        ('snmpgetintinfo', 'SNMP Integer Info'), ('snmpgetbool', 'SNMP Boolean Check'),
                        ('snmpgetboolgraph', 'SNMP Boolean Graph'), ('snmpgetboolinfo', 'SNMP Boolean Info'),
                        ('snmpgetstr', 'SNMP String Check'), ('snmpgetstrgraph', 'SNMP String Graph'),
                        ('snmpgetstrinfo', 'SNMP String Info'), ('execint', 'Exec Int Check'),
                        ('execintgraph', 'Exec Int Graph'), ('execintinfo', 'Exec Int Info'),
                        ('execstr', 'Exec String Check'), ('execstrgraph', 'Exec String Graph'),
                        ('execstrinfo', 'Exec String Info'), ('execbool', 'Exec Bool Check'),
                        ('execboolgraph', 'Exec Bool Graph'), ('execboolinfo', 'Exec Bool Info'))
    name = models.SlugField('Name', max_length=128, unique=True, help_text='Name of the widget.')
    verbosename = models.CharField('Full Name', max_length=128, help_text='Name of the widget as rendered on the page.')
    active = models.BooleanField('Enabled', default=True, help_text='Is this widget available ?')
    hostcheck = models.ForeignKey(HostChecks, on_delete=models.SET_NULL, null=True, blank=True,
                                  help_text='Which check does this widget refers to ?')
    host = models.ForeignKey(Hosts, on_delete=models.SET_NULL, null=True, blank=True,
                             help_text='Which host does this widget refers to ?')
    unit = models.CharField('Unit', max_length=4, default='A', blank=True,
                            help_text='Unit used for the check in the widget, i.e. A')
    template = models.CharField('Template', max_length=32, choices=TEMPLATE_CHOICES, default='snmpgetint',
                                help_text='The template to use to display the widget.')
    note = models.CharField('Note', max_length=4096, null=True, blank=True, default=None,
                            help_text='Additional information that could be usefull.')

    def __str__(self):
        return str(self.name)

    def renderWidget(self, user=None):
        from M4.scheduler.models import Historical
        from M4.scheduler.utils import strtobool, booltostr
        t = 'widgets/' + self.template + '.html'
        value = getMetadata(self.host.name + ':' + self.hostcheck.name + '::value', 'No Data')
        error = getMetadata(self.host.name + ':' + self.hostcheck.name + '::error', 'No Data')
        notifs = getMetadata(self.host.name + ':' + self.hostcheck.name + '::notifs', True)
        if error == 'ok':
            color = 'bg-green-400'
        elif error == 'crit':
            color = 'bg-danger-400'
        elif error == 'warn':
            color = 'bg-orange-400'
        else:
            color = 'bg-teal-400'
        hostcheckmd = {}
        if self.hostcheck.checktype == 'snmpgetbool' or self.hostcheck.checktype == 'execbool':
            value = booltostr(strtobool(str(value)))
            hostcheckmd['nbtrue'] = getMetadata(self.host.name + ':' + self.hostcheck.name + '::nbtrue', '0')
            hostcheckmd['nbfalse'] = getMetadata(self.host.name + ':' + self.hostcheck.name + '::nbfalse', '0')
            hostcheckmd['lasttrue'] = getMetadata(self.host.name + ':' + self.hostcheck.name + '::lasttrue', 'No Data')
            hostcheckmd['lastfalse'] = getMetadata(self.host.name + ':' + self.hostcheck.name + '::lastfalse',
                                                   'No Data')
        elif self.hostcheck.checktype == 'snmpgetint' or self.hostcheck.checktype == 'execint':
            hostcheckmd['min'] = getMetadata(self.host.name + ':' + self.hostcheck.name + '::min', 'No Data')
            hostcheckmd['max'] = getMetadata(self.host.name + ':' + self.hostcheck.name + '::max', 'No Data')
            hostcheckmd['avg'] = getMetadata(self.host.name + ':' + self.hostcheck.name + '::avg', 'No Data')
        hostcheckmd['lasterror'] = getMetadata(self.host.name + ':' + self.hostcheck.name + '::lasterror', 'Never')
        hostcheckmd['nberror'] = getMetadata(self.host.name + ':' + self.hostcheck.name + '::nberror', '0')
        # hostcheckmd = json.loads(getMetadata(self.host.name + ':' + self.hostcheck.name + '::metadata', '{}'))
        # Prepare the context used to populate the variables in the template.  Since we have many diff type of templates, we have a lot off diff values here.
        c = {'host': self.host, 'hostcheck': self.hostcheck, 'name': self.name, 'hostcheckmd': hostcheckmd,
             'value': value, 'unit': self.unit, 'verbosename': self.verbosename, 'color': color, 'user': user,
             'notifs': notifs}
        rendered = render_to_string(t, c)
        return rendered

    class Meta:
        verbose_name = 'Widget'
        verbose_name_plural = 'Widgets'
        ordering = ['-name']


class UserView(models.Model):
    """
    This model stores the widgets to display for a particular group, related to :model:`auth.Group` and :model:`webview.Widgets`.
    """
    group = models.ManyToManyField(Group, blank=True, help_text='Groups allowed to use the view')
    name = models.SlugField('Name', max_length=128, unique=True, help_text='Name for the view.')
    widgets = models.ManyToManyField(Widgets, blank=True, help_text="List of widgets to display in the view")
    default = models.BooleanField('Default', default=False, help_text='Default view, can be only one.')
    active = models.BooleanField('Enabled', default=True, help_text='Is this view available ?')
    note = models.CharField('Note', max_length=4096, null=True, blank=True, default=None,
                            help_text='Additional information that could be usefull.')

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'User View'
        verbose_name_plural = 'User Views'
        ordering = ['name']


class UIMsg(models.Model):
    """
    This model stores the messages to be displayed in the UI.  Per user.  related to :model:`auth.Group` and :model:`auth.User`.
    """
    LEVEL_CHOICES = (
        ('20', 'info'), ('10', 'debug'), ('30', 'warning'), ('25', 'success'), ('40', 'error'), ('99', 'problem'))
    level = models.CharField('Level', max_length=16, choices=LEVEL_CHOICES, default='debug',
                             help_text='The level of the message')
    timestamp = models.DateTimeField('Timestamp', auto_now_add=True, help_text='Timestamp for the event.')
    group = models.ManyToManyField(Group, help_text='Groups who should see this message.')
    user = models.ManyToManyField(User, blank=True, default=None, help_text='Users whohave seen this message.')
    msg = models.CharField('Message', max_length=1024, help_text='The message')
    sticky = models.BooleanField('Sticky', default=False, help_text='Show everytime until removed manually.')

    def __str__(self):
        return str(self.msg)

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['-timestamp']


"""
remember to use ForeignKeyAutocompleteAdmin
from django_extensions.admin import ForeignKeyAutocompleteAdmin


class PermissionAdmin(ForeignKeyAutocompleteAdmin):
    # User is your FK attribute in your model
    # first_name and email are attributes to search for in the FK model
    related_search_fields = {
       'user': ('first_name', 'email'),
    }
https://django-extensions.readthedocs.org/en/latest/admin_extensions.html

should also use fragment caching
https://docs.djangoproject.com/en/1.9/topics/cache/#template-fragment-caching
"""
