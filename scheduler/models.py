import datetime

from django.contrib.auth.models import Group, User
from django.core.mail import send_mass_mail
from django.db import models
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.template import engines
from django.utils import timezone
from djcelery.models import IntervalSchedule, PeriodicTask

# from delorean import Delorean
from scheduler.utils import strtobool, booltostr
from tools import dbg, setmd, add_msg, getMetadata, setMetadata


# noinspection PyProtectedMember
def get_choicename(obj, fieldname):
    """
    given an object and a field which has a choices argument,
    find the name of choice for that field instead of its stored
    database number svalue

    returns the tuple ( '$field$_choicename', field_choicename
    """
    field_key = getattr(obj, fieldname)
    field = obj._meta.get_field(fieldname)
    field_choicename = [val for key, val in field.choices if key == field_key][0]
    return '%s_choicename' % fieldname, field_choicename


class Hosts(models.Model):
    """
    This model stores the hosts that we will be checking.
    """
    name = models.SlugField('Name', max_length=128, unique=True, help_text='Name of the host.')
    address = models.GenericIPAddressField('IP', protocol='IPv4', unique=False, help_text='IP address of the host.')
    community = models.CharField('Community', max_length=128, default='public', help_text='Community for snmp checks.')
    enabled = models.BooleanField('Active', default=True, help_text='Are checks for this host active ?')
    note = models.CharField('Note', max_length=4096, null=True, blank=True, default=None,
                            help_text='Additional information that could be usefull.')

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'Host Definition'
        verbose_name_plural = 'Hosts and Devices'
        ordering = ['-name']


class HostChecks(models.Model):
    """
    This model stores the checks performed on hosts, related to :model:`scheduler.Hosts`.
    """
    CHECK_CHOICES = (
        ('snmpgetint', 'SNMP Check Int'), ('snmpgetbool', 'SNMP Check Bool'), ('execint', 'Shell Exec Int'),
        ('execbool', 'Shell Exec Bool'), ('snmpgetstr', 'SNMP Check String'), ('execstr', 'Shell Exec String'))
    INTERVAL_CHOICES = (
        ('10', 'every 10 seconds'), ('30', 'every 30 seconds'), ('60', 'every 60 seconds'),
        ('600', 'every 600 seconds'))
    name = models.SlugField('Name', max_length=128, unique=True, help_text='Name of the check.')
    hosts = models.ManyToManyField('Hosts', help_text='Hosts the check applies to.')
    checktype = models.CharField('Type', max_length=16, choices=CHECK_CHOICES, default='snmpgetint',
                                 help_text='The type of check to be performed.')
    interval = models.CharField('Interval', max_length=32, choices=INTERVAL_CHOICES, default='30',
                                help_text='Interval for the periodic task.')
    arg = models.CharField('Argument', max_length=1024,
                           help_text='The argument for the check.  oid for snmp and cmd for exec.')
    unit = models.CharField('Unit', max_length=4, default=None, blank=True,
                            help_text='Unit used for the check in the widget, i.e. A')
    quotient = models.CharField('Quotient', max_length=4, default='1',
                                help_text='Divide or multiply the result. .01 = divided by 100')
    verbosename = models.CharField('Full Name', max_length=128, help_text='Name of the widget as rendered on the page.')
    threshold = models.ManyToManyField('Thresholds', blank=True, help_text='Threshold the check adheres to.')
    sla = models.ManyToManyField('Sla', blank=True, help_text='SLAs this check affects.')
    allhosts = models.BooleanField('Check all hosts to fail a threshold', default=False,
                                   help_text='When more than one host is assigned to a check, require them all to fail before failing the check.')
    colorizesla = models.BooleanField('Colorize on SLA status instead of threshold', default=False,
                                      help_text='So that pumps do not always show a red widget')
    # status = models.CharField('Check global status', max_length=4096, default='{}', help_text='Ok, partial, failed, none')
    # statsinterval = models.IntegerField('Stats Interval', default='300', help_text='How often, in seconds, we recalculate the stats.')
    enabled = models.BooleanField('Active', default=True, help_text='Are checks for this host active ?')
    note = models.CharField('Note', max_length=4096, null=True, blank=True, default=None,
                            help_text='Additional information that could be usefull.')

    def save(self, *args, **kwargs):
        super(HostChecks, self).save(*args, **kwargs)
        # Set the master status of the check, depending on wether or not we account for all hosts
        if self.allhosts is True:
            nbhosts = 0  # number of hosts we have total
            nbfailed = 0  # number of faled hosts
            for host in self.hosts.filter(enabled=True):
                nbhosts = nbhosts + 1
                if getMetadata(host.name + ':' + self.name + '::checkstatus', 'OK') == "failed":
                    nbfailed = nbfailed + 1
            if nbhosts - nbfailed <= 0:
                # self.status = 'failed'
                setMetadata(self.name + '::globalstatus', 'failed')
            elif nbfailed == 0:
                setMetadata(self.name + '::globalstatus', 'OK')
                # self.status = 'OK'
            elif nbhosts - nbfailed > 0 and nbfailed < nbhosts:
                # self.status = 'partial'
                setMetadata(self.name + '::globalstatus', 'partial')
            else:
                dbg('Should not be hitting else')
        else:
            nbhosts = 0
            nbfailed = 0
            for host in self.hosts.filter(enabled=True):
                nbhosts = nbhosts + 1
                if getMetadata(host.name + ':' + self.name + '::checkstatus', 'OK') == "failed":
                    nbfailed = nbfailed + 1
            if nbhosts - nbfailed < nbhosts:
                setMetadata(self.name + '::globalstatus', 'failed')
                # self.status = 'failed'
            elif nbhosts - nbfailed == nbhosts:
                setMetadata(self.name + '::globalstatus', 'OK')
                # self.status = 'OK'
            else:
                dbg('Should not be hitting else')
        super(HostChecks, self).save(*args, **kwargs)  # Call the "real" save() method.
        return True

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'Host Check'
        verbose_name_plural = 'Checks'
        ordering = ['-name']


# noinspection PyUnusedLocal
class Thresholds(models.Model):
    """
    This model stores the Thresholds applied to checks, related to :model:`scheduler.HostChecks`.

    There are probably better ways of doing this, but this is the fast one.  We can refactor this later.
    INT: If high is filled, trigger sla over it.  if low is filled, trigger sla under it.  both can be applied.
    BOOL: one or the other must be filled.  If Good is filled, any other values triggers an SLA.  If bad is filled, trigger an SLA when when value is detected.
    STR: one or the other must be filled.  If Good is filled, any other values triggers an SLA.  If bad is filled, trigger an SLA when when value is detected.  Also, can specify a warning string.
    """
    THOLD_CHOICES = (('int', 'Integer'), ('bool', 'Boolean'), ('str', 'String'))
    name = models.SlugField('Name', max_length=128, unique=True, help_text='Name of the thresholds.')
    verbosename = models.CharField('Full Name', max_length=256, blank=True, help_text='Verbose name as displayed.')
    type = models.CharField('Type', max_length=4, choices=THOLD_CHOICES, default='int',
                            help_text='The type of value we check against.')
    warngroups = models.ManyToManyField(Group, verbose_name='Warning Groups', related_name='warngroup', default=None,
                                        blank=True, help_text='Groups to notify on warning, if applicable.')
    critgroups = models.ManyToManyField(Group, verbose_name='Critical Groups', related_name='critgroup', default=None,
                                        blank=True, help_text='Groups to notify on critical, if applicable.')
    okgroups = models.ManyToManyField(Group, verbose_name='Recovery Groups', related_name='okgroup', default=None,
                                      blank=True, help_text='Groups to notify on recovery, if applicable.')
    errgroups = models.ManyToManyField(Group, verbose_name='Error Groups', related_name='errgroup', default=None,
                                       blank=True, help_text='Groups to notify on errors, if applicable.')
    warntpl = models.ForeignKey('Template', verbose_name='Warning template', related_name='warntpl', default=None,
                                null=True, blank=True, on_delete=models.PROTECT,
                                limit_choices_to={'event': 'warn', 'obj': 'thold'},
                                help_text='Template to use when sending out warning emails.')
    crittpl = models.ForeignKey('Template', verbose_name='Critical template', related_name='crittpl', default=None,
                                null=True, blank=True, on_delete=models.PROTECT,
                                limit_choices_to={'event': 'crit', 'obj': 'thold'},
                                help_text='Template to use when sending out critical emails.')
    oktpl = models.ForeignKey('Template', verbose_name='Recovery template', related_name='oktpl', default=None,
                              null=True, blank=True, on_delete=models.PROTECT,
                              limit_choices_to={'event': 'ok', 'obj': 'thold'},
                              help_text='Template to use when sending out recovery emails.')
    errtpl = models.ForeignKey('Template', verbose_name='Error template', related_name='errtpl', default=None,
                               null=True, blank=True, on_delete=models.PROTECT,
                               limit_choices_to={'event': 'err', 'obj': 'thold'},
                               help_text='Template to use when sending out error emails.')
    warnrepeat = models.IntegerField('Warning Interval', default=120, blank=True, null=True,
                                     help_text='How often, in seconds, we send the warnings. Set to 0 to not rate limit, blank to send only once.')
    critrepeat = models.IntegerField('Critical Interval', default=120, blank=True, null=True,
                                     help_text='How often, in seconds, we send the criticals. Set to 0 to not rate limit, blank to send only once.')
    lowwarn = models.FloatField('INT Low Warning', blank=True, null=True, default=None,
                                help_text='For Integer checks, the low warning value.  for Internal Use.')
    lowcrit = models.FloatField('INT Low Critical', blank=True, null=True, default=None,
                                help_text='For Integer checks, the low critical value.  Affects the SLA.')
    highwarn = models.FloatField('INT High Warning', blank=True, null=True, default=None,
                                 help_text='For Integer checks, the high warning value.  for Internal Use.')
    highcrit = models.FloatField('INT High Critical', blank=True, null=True, default=None,
                                 help_text='For Integer checks, the high critical value.  Affects the SLA.')
    boolgood = models.NullBooleanField('BOOL Good', default=None,
                                       help_text='For Boolean checks, This is the expected value.  Anything else affects the SLA.  Leave UNKOWN to disable')
    boolbad = models.NullBooleanField('BOOL Bad', default=None,
                                      help_text='For Boolean checks, If seen, this affects the SLA.  All other values OK.  Leave UNKOWN to disable.')
    boolwarn = models.NullBooleanField('BOOL Warn', default=None,
                                       help_text='For Boolean checks, If seen, this triggers a warning email.  Leave UNKOWN to disable.')
    strgood = models.CharField('STR Good', max_length=1024, blank=True, null=True, default=None,
                               help_text='For string checks. expected value.  Anything else affects the SLA.')
    strwarn = models.CharField('STR Bad', max_length=1024, blank=True, null=True, default=None,
                               help_text='For string checks. If seen, this affects the SLA.')
    strbad = models.CharField('STR Warning', max_length=1024, blank=True, null=True, default=None,
                              help_text='For string checks. If seen, Emit a warning.  For internal use.')
    enabled = models.BooleanField('Active', default=True, help_text='Is this threshold active ?')
    note = models.CharField('Note', max_length=4096, null=True, blank=True, default=None,
                            help_text='Additional information that could be usefull.')

    def __str__(self):
        return str(self.name)

    def checkForIntWith(self, value, check, host):
        # Compile the list of possible error and trigger actions
        error = {'hasError': False, 'lowwarn': False, 'lowcrit': False, 'highwarn': False, 'highcrit': False, }

        if self.enabled:
            tocheck = float(value)
            if self.lowcrit is not None and tocheck <= self.lowcrit:
                error['hasError'] = True
                error['lowcrit'] = True
                self.doCrit(tocheck, error, check, host)
            if self.lowwarn is not None and tocheck <= self.lowwarn:
                error['hasError'] = True
                error['lowwarn'] = True
                self.doWarn(tocheck, error, check, host)
            if self.highcrit is not None and tocheck >= self.highcrit:
                error['hasError'] = True
                error['highcrit'] = True
                self.doCrit(tocheck, error, check, host)
            if self.highwarn is not None and tocheck >= self.highwarn:
                error['hasError'] = True
                error['highwarn'] = True
                self.doWarn(tocheck, error, check, host)
            if error['hasError'] is False:
                self.doOK(tocheck, error, check, host)
        return error

    def checkForBoolWith(self, value, check, host):
        # Compile the list of possible error and trigger actions
        error = {'hasError': False, 'boolgood': False, 'boolbad': False, 'boolwarn': False}
        if self.enabled:
            tocheck = strtobool(value)
            if self.boolwarn is not None and tocheck is self.boolwarn:
                error['hasError'] = True
                error['boolwarn'] = True
                self.doWarn(tocheck, error, check, host)
            if self.boolgood is not None and tocheck is not self.boolgood:
                error['hasError'] = True
                error['boolgood'] = True
                self.doCrit(tocheck, error, check, host)
            if self.boolbad is not None and tocheck is self.boolbad:
                error['hasError'] = True
                error['boolbad'] = True
                self.doCrit(tocheck, error, check, host)
            if error['hasError'] is False:
                self.doOK(tocheck, error, check, host)
        return error

    def checkForStrWith(self, value, check, host):
        # Compile the list of possible error and trigger actions
        error = {'hasError': False, 'strgood': False, 'strbad': False, 'strwarn': False}
        if self.enabled:
            tocheck = str(value)
            if self.strgood is not None and tocheck != self.strgood:
                error['hasError'] = True
                error['strgood'] = True
                self.doCrit(tocheck, error, check, host)
            if self.strbad is not None and tocheck == self.strbad:
                error['hasError'] = True
                error['strbad'] = True
                self.doCrit(tocheck, error, check, host)
            if self.strwarn is not None and tocheck == self.strwarn:
                error['hasError'] = True
                error['strwarn'] = True
                self.doWarn(tocheck, error, check, host)
            if error['hasError'] is False:
                self.doOK(tocheck, error, check, host)
        return error

    def doWarn(self, value, error, check, host):
        # a warn means notify warn group, but dont fail the service.
        global subj
        now = timezone.now().timestamp()
        doit = False
        setMetadata(host.name + ':' + check.name + ':thold-' + self.name + '::laststatus', 'warn')

        if self.warnrepeat is None and int(
                getMetadata(host.name + ':' + check.name + ':thold-' + self.name + '::lastwarn', 0) == 0):
            doit = True
        elif self.critrepeat is not None and int(
                getMetadata(host.name + ':' + check.name + ':thold-' + self.name + '::lastwarn', 0)) < int(now) - int(
            self.warnrepeat):
            doit = True
        if getMetadata(host.name + ':' + check.name + '::notifs', 'True') == 'False':
            doit = False

        if doit is True:
            setMetadata(host.name + ':' + check.name + ':thold-' + self.name + '::lastwarn', int(now))
            # dbg('do warn 2')
            if self.type == 'bool':
                subj = '[M4 - WARNING] ' + check.name + ' on ' + host.name + ' = ' + booltostr(strtobool(str(value)))
            elif self.type == 'int':
                subj = '[M4 - WARNING] ' + check.name + ' on ' + host.name + ' is at ' + str(value) + check.unit
            elif self.type == 'str':
                subj = '[M4 - WARNING] ' + check.name + ' on ' + host.name + ' is ' + str(value)
            from webview.models import UserProfile
            emails = []
            
            # It is also an issue for users who dont log on often and have lots of threshold events.
            add_msg('30', check.name + ' on ' + host.name + ' failed threshold named ' + self.name + ' with value ' + str(value), self.warngroups.all())
            for group in self.warngroups.all():
                users = User.objects.filter(groups=group)
                for user in users:
                    # This is where the user decides where to receive his notifications.
                    mail = UserProfile.objects.get(user=user).notifemail
                    if mail is not None and mail != '':
                        emails.append(
                            (subj, self.renderMail(value, error, check, host, 'warn'), 'm4@m4system.com', [mail]))
            send_mass_mail(tuple(emails), fail_silently=False)
        return True

    def doCrit(self, value, error, check, host):
        # A crit means fail this host-check combo and, depending on settings, fail any SLA that are linked to that check
        # Happens only once.  Use warngroups if you want repearing alerts.
        # It is also an issue for users who dont log on often and have lots of threshold events.
        # add_msg('30', check.name + ' on ' + host.name + ' critically failed threshold named ' + self.name + ' with value ' + str(value), self.warngroups.all())
        now = timezone.now().timestamp()
        doit = False

        if self.critrepeat is None and int(
                getMetadata(host.name + ':' + check.name + ':thold-' + self.name + '::lastcrit', 0)) == 0:
            doit = True
        elif self.critrepeat is not None and int(
                getMetadata(host.name + ':' + check.name + ':thold-' + self.name + '::lastcrit', 0)) < int(now) - int(
            self.critrepeat):
            doit = True
        if getMetadata(host.name + ':' + check.name + '::notifs', 'True') == 'False':
            doit = False

        if doit is True:
            setMetadata(host.name + ':' + check.name + ':thold-' + self.name + '::laststatus', 'crit')
            setMetadata(host.name + ':' + check.name + ':thold-' + self.name + '::lastcrit', int(now))
            setMetadata(host.name + ':' + check.name + '::checkstatus', 'failed')
            check.save()  # This is required to trigger the SLA failure check
            if getMetadata(host.name + ':' + check.name + '::notifs', True):
                if self.type == 'bool':
                    subj = '[M4 - CRITICAL] ' + check.name + ' on ' + host.name + ' = ' + booltostr(
                        strtobool(str(value)))
                    from webview.models import UserProfile
                    emails = []
                    
                    # It is also an issue for users who dont log on often and have lots of threshold events.
                    # add_msg('30', check.name + ' on ' + host.name + ' failed threshold named ' + self.name + ' with value ' + str(value), self.warngroups.all())
                    for group in self.critgroups.all():
                        users = User.objects.filter(groups=group)
                        for user in users:
                            # This is where the user decides where to receive his notifications.
                            mail = UserProfile.objects.get(user=user).notifemail
                            # dbg( user.username + ' is ' + mail)
                            if mail is not None and mail != '':
                                emails.append((subj, self.renderMail(value, error, check, host, 'crit'),
                                               'm4@m4system.com', [mail]))
                    send_mass_mail(tuple(emails), fail_silently=False)
                elif self.type == 'str':
                    subj = '[M4 - CRITICAL] ' + check.name + ' on ' + host.name + ' is ' + str(value)
                    from webview.models import UserProfile
                    emails = []
                    
                    # It is also an issue for users who dont log on often and have lots of threshold events.
                    # add_msg('30', check.name + ' on ' + host.name + ' failed threshold named ' + self.name + ' with value ' + str(value), self.warngroups.all())
                    for group in self.critgroups.all():
                        users = User.objects.filter(groups=group)
                        for user in users:
                            # This is where the user decides where to receive his notifications.
                            mail = UserProfile.objects.get(user=user).notifemail
                            # dbg( user.username + ' is ' + mail)
                            if mail is not None and mail != '':
                                emails.append((subj, self.renderMail(value, error, check, host, 'crit'),
                                               'm4@m4system.com', [mail]))
                    send_mass_mail(tuple(emails), fail_silently=False)
                elif self.type == 'int':
                    subj = '[M4 - CRITICAL] ' + check.name + ' on ' + host.name + ' is at ' + str(
                        value) + " " + check.unit
                    from webview.models import UserProfile
                    emails = []
                    
                    # It is also an issue for users who dont log on often and have lots of threshold events.
                    # add_msg('30', check.name + ' on ' + host.name + ' failed threshold named ' + self.name + ' with value ' + str(value), self.warngroups.all())
                    for group in self.critgroups.all():
                        users = User.objects.filter(groups=group)
                        for user in users:
                            # This is where the user decides where to receive his notifications.
                            mail = UserProfile.objects.get(user=user).notifemail
                            # dbg( user.username + ' is ' + mail)
                            if mail is not None and mail != '':
                                emails.append((subj, self.renderMail(value, error, check, host, 'crit'),
                                               'm4@m4system.com', [mail]))
                    send_mass_mail(tuple(emails), fail_silently=False)
            # Log a fail event for all SLA that have this check assigned
            for sla in Sla.objects.filter(hostchecks=check):
                EventLog(sla=sla, hostcheck=check, host=host, threshold=self, event='bad', value=value,
                         data=error).save()
        return True

    def doOK(self, value, error, check, host):
        # Go back to ok state for SLA calculation.
        global subj
        if getMetadata(host.name + ':' + check.name + ':thold-' + self.name + '::laststatus', False) != 'OK':
            setMetadata(host.name + ':' + check.name + '::notifs', True)
            setMetadata(host.name + ':' + check.name + ':thold-' + self.name + '::lastwarn', 0)
            setMetadata(host.name + ':' + check.name + ':thold-' + self.name + '::lastcrit', 0)
            setMetadata(host.name + ':' + check.name + ':thold-' + self.name + '::laststatus', 'OK')
            setMetadata(host.name + ':' + check.name + '::checkstatus', 'OK')
            check.save()  # This is required to trigger the SLA failure check
            if self.type == 'bool':
                subj = '[M4 - OK] ' + check.name + ' on ' + host.name + ' = ' + booltostr(strtobool(str(value)))
            elif self.type == 'int':
                subj = '[M4 - OK] ' + check.name + ' on ' + host.name + ' is at ' + str(value) + check.unit
            elif self.type == 'str':
                subj = '[M4 - OK] ' + check.name + ' on ' + host.name + ' is ' + str(value)
            from webview.models import UserProfile
            emails = []
            
            # It is also an issue for users who dont log on often and have lots of threshold events.
            # add_msg('30', check.name + ' on ' + host.name + ' failed threshold named ' + self.name + ' with value ' + str(value), self.warngroups.all())
            for group in self.okgroups.all():
                users = User.objects.filter(groups=group)
                for user in users:
                    # This is where the user decides where to receive his notifications.
                    mail = UserProfile.objects.get(user=user).notifemail
                    if mail is not None and mail != '':
                        emails.append(
                            (subj, self.renderMail(value, error, check, host, 'ok'), 'm4@m4system.com', [mail]))
            send_mass_mail(tuple(emails), fail_silently=False)
            # Log a fail event for all SLA that have this check assigned
            for sla in Sla.objects.filter(hostchecks=check):
                EventLog(sla=sla, hostcheck=check, host=host, threshold=self, event='good', value=value,
                         data=error).save()
        return True

    def renderMail(self, value, error, check, host, type):
        django_engine = engines['django']
        t = None
        if type == 'warn':
            try:
                t = django_engine.from_string(self.warntpl.content)
            except Exception as e:
                dbg(e)
                t = None
        elif type == 'crit':
            try:
                t = django_engine.from_string(self.crittpl.content)
            except Exception as e:
                dbg(e)
                t = None
        elif type == 'ok':
            try:
                t = django_engine.from_string(self.oktpl.content)
            except Exception as e:
                dbg(e)
                t = None
        else:
            t = django_engine.from_string("THIS TEMPLATE TYPE DOES NOT EXIST")
        if t is not None:
            c = {'value': str(value), 'error': error, 'check': check, 'host': host, 'thold': self}
            rendered = t.render(c)
            return rendered
        else:
            return 'THERE WAS AN ERROR RENDERING YOUR TEMPLATE'

    class Meta:
        verbose_name = 'Threshold for check'
        verbose_name_plural = 'Thresholds'
        ordering = ['name']


class Historical(models.Model):
    """
    This model stores historical data related to the checks, related to :model:`scheduler.HostChecks` and :model:`scheduler.Hosts`.
    """
    host = models.ForeignKey('Hosts', on_delete=models.CASCADE, help_text='Host this data relates to.')
    hostcheck = models.ForeignKey('HostChecks', on_delete=models.CASCADE, help_text='Check this data relates to.')
    value = models.CharField('Value', max_length=4096, help_text='Value returned by check.')
    data = models.CharField('Metadata', max_length=4096, default='{}', help_text='JSON encoded metadata')
    timestamp = models.DateTimeField('Timestamp', auto_now_add=True, help_text='Timestamp for the event.')
    exported = models.BooleanField('To Delete', default=False,
                                   help_text='Set to True if it was exported to InfluxDB and can be deleted')

    # exportedk = models.BooleanField('To Delete K', default=False, help_text='Set to True if it was exported to Kafka and can be deleted')

    def __str__(self):
        return str(self.host.name) + '[' + str(self.hostcheck.name) + '] = ' + str(self.value) + ' on ' + str(
            self.timestamp)

    class Meta:
        verbose_name = 'Historical data'
        verbose_name_plural = 'Historical Data Log'
        ordering = ['-pk']


# noinspection PyUnusedLocal,PyUnusedLocal,PyUnusedLocal,PyUnusedLocal,PyUnusedLocal,PyUnusedLocal,PyUnusedLocal,PyUnusedLocal,PyUnusedLocal,PyUnusedLocal,PyUnusedLocal,PyUnusedLocal,PyUnusedLocal,PyUnusedLocal,PyUnusedLocal,PyUnusedLocal,PyUnusedLocal,PyUnusedLocal,PyUnusedLocal,PyUnusedLocal,PyUnusedLocal,PyUnusedLocal,PyUnusedLocal,PyUnusedLocal,PyBroadException,PyBroadException,PyBroadException,PyBroadException,PyBroadException
class Sla(models.Model):
    """
    This model stores SLA data from thresholds fail, related to :model:`scheduler.HostChecks`.
    """
    name = models.SlugField('Name', max_length=128, unique=True, help_text='Name of the SLA.')
    verbosename = models.CharField('Full Name', max_length=256, blank=True, help_text='Verbose name as displayed.')
    currentvalue = models.FloatField('Rolling window value', blank=True, null=True, default='100',
                                     help_text='30 Day Rolling window value')
    status = models.CharField('Current Status', max_length=16, default='OK',
                              help_text='Current condition of the SLA.  Failing or OK')
    critical = models.FloatField('Value in percentile for criticality', blank=True, null=True, default='99',
                                 help_text='Consider the SLA critical at this value.  Email alertgroups.')
    warngroups = models.ManyToManyField(Group, verbose_name='Warning Groups', related_name='slawarngroup', default=None,
                                        blank=True, help_text='Groups to notify on warning, if applicable.')
    critgroups = models.ManyToManyField(Group, verbose_name='Critical Groups', related_name='slacritgroup',
                                        default=None, blank=True,
                                        help_text='Groups to notify on critical, if applicable.')
    okgroups = models.ManyToManyField(Group, verbose_name='Recovery Groups', related_name='slaokgroup', default=None,
                                      blank=True, help_text='Groups to notify on recovery, if applicable.')
    warntpl = models.ForeignKey('Template', verbose_name='Warning template', related_name='slawarntpl', default=None,
                                null=True, blank=True, on_delete=models.PROTECT,
                                limit_choices_to={'event': 'warn', 'obj': 'sla'},
                                help_text='Template to use when sending out warning emails when the SLA is being affected.')
    crittpl = models.ForeignKey('Template', verbose_name='Critical template', related_name='slacrittpl', default=None,
                                null=True, blank=True, on_delete=models.PROTECT,
                                limit_choices_to={'event': 'crit', 'obj': 'sla'},
                                help_text='Template to use when sending out critical emails when the SLA goes under the critical threshold.')
    oktpl = models.ForeignKey('Template', verbose_name='Recovery template', related_name='slaoktpl', default=None,
                              null=True, blank=True, on_delete=models.PROTECT,
                              limit_choices_to={'event': 'ok', 'obj': 'sla'},
                              help_text='Template to use when sending out recovery emails.')
    # data = models.CharField('Metadata', max_length=4096, default='{}', help_text='JSON encoded metadata')
    allchecks = models.BooleanField('Require all checks to fail', default=False,
                                    help_text='When more than one check is assigned to an SLA, require all of them to fail before we consider the SLA event.')
    enabled = models.BooleanField('Active', default=True, help_text='Is this SLA active ?')
    note = models.CharField('Note', max_length=4096, null=True, blank=True, default=None,
                            help_text='Additional information that could be usefull.')

    def __str__(self):
        return str(self.name) + '@' + str(self.currentvalue)

    def save(self, *args, **kwargs):
        super(Sla, self).save(*args, **kwargs)  # Call the "real" save() method.
        # trigger a critical if value is under our setting
        if self.enabled:
            if self.status == 'failing' and getMetadata('sla-' + self.name + '::laststatus', False) != 'failing':
                setMetadata('sla-' + self.name + '::laststatus', self.status)
                self.doWarn()
            if float(self.currentvalue) <= float(self.critical) and self.status == 'failing' and getMetadata(
                    'sla-' + self.name + '::laststatus', False) != 'failing':
                setMetadata('sla-' + self.name + '::laststatus', self.status)
                self.doCrit()
            elif self.status == 'OK' and getMetadata('sla-' + self.name + '::laststatus', False) != 'OK':
                setMetadata('sla-' + self.name + '::laststatus', self.status)
                self.doOk()
        super(Sla, self).save(*args, **kwargs)  # Call the "real" save() method.
        return True

    def doWarn(self):
        # send notifications if the SLA is affected
        from webview.models import UserProfile
        emails = []
        for group in self.warngroups.all():
            users = User.objects.filter(groups=group)
            for user in users:
                mail = UserProfile.objects.get(user=user).notifemail
                if mail is not None and mail != '':
                    emails.append(
                        ('[M4] SLA Warning for ' + self.name, self.renderMail('warn'), 'm4@m4system.com', [mail]))
        send_mass_mail(tuple(emails), fail_silently=False)
        return True

    def doCrit(self):
        # Declare the SLA critical and send notification
        from webview.models import UserProfile
        emails = []
        for group in self.critgroups.all():
            users = User.objects.filter(groups=group)
            for user in users:
                mail = UserProfile.objects.get(user=user).notifemail
                if mail is not None and mail != '':
                    emails.append(('[M4] ***CRITICAL SLA*** for ' + self.name, self.renderMail('crit'),
                                   'm4@m4system.com', [mail]))
        send_mass_mail(tuple(emails), fail_silently=False)
        return True

    def doOk(self):
        # Declare the SLA OK again and send notification
        from webview.models import UserProfile
        emails = []
        for group in self.okgroups.all():
            users = User.objects.filter(groups=group)
            for user in users:
                mail = UserProfile.objects.get(user=user).notifemail
                if mail is not None and mail != '':
                    emails.append(
                        ('[M4] SLA Restored for ' + self.name, self.renderMail('ok'), 'm4@m4system.com', [mail]))
        send_mass_mail(tuple(emails), fail_silently=False)
        return True

    def renderMail(self, type):
        django_engine = engines['django']
        t = None
        if type == 'warn':
            try:
                t = django_engine.from_string(self.warntpl.content)
            except Exception as e:
                dbg(e)
                t = None
        elif type == 'crit':
            try:
                t = django_engine.from_string(self.crittpl.content)
            except Exception as e:
                dbg(e)
                t = None
        elif type == 'ok':
            try:
                t = django_engine.from_string(self.oktpl.content)
            except Exception as e:
                dbg(e)
                t = None
        else:
            t = django_engine.from_string("THIS TEMPLATE TYPE DOES NOT EXIST")
        if t is not None:
            c = {'value': str(self.currentvalue), 'sla': self}
            rendered = t.render(c)
            return rendered
        else:
            return 'THERE WAS AN ERROR RENDERING YOUR TEMPLATE'

    def computeSLA(self):
        # Compute the SLA.  Can be called from the management shell:  m4@m4dev:~$ manage computesla
        # A100 wants this in amount of failures per periods instead of %.
        global lastevent, lastbad
        now = timezone.now()
        monthbefore = now - datetime.timedelta(days=30)
        # Compute last 30 days
        try:
            events = SlaLog.objects.filter(timestamp__range=[monthbefore, now], sla=self).order_by('pk')
            lastevent = events[0].event
            if lastevent == 'bad':
                lastbad = events[0].timestamp
                lastgood = None
            elif lastevent == 'good':
                lastgood = events[0].timestamp
                lastbad = None
            badintervals = []
            countbad = 0
            for event in events:
                if event.event == 'bad' and lastevent == 'good':
                    countbad = countbad + 1
                    lastbad = event.timestamp
                    lastevent = 'bad'
                elif lastevent == 'bad' and event.event == 'good':
                    lastgood = event.timestamp
                    lastevent = 'good'
                    badintervals.append([lastbad, lastgood])
                elif event.event == 'bad' and lastevent == 'bad':
                    countbad = countbad + 1
                    lastbad = events[0].timestamp
                    lastevent = 'bad'
            if lastevent == 'bad':
                badintervals.append([lastbad, now])
            monthinseconds = 30 * 24 * 60 * 60
            goodinseconds = monthinseconds
            delta = None
            for interval in badintervals:
                delta = interval[1] - interval[0]
                goodinseconds = goodinseconds - delta.total_seconds()
            self.currentvalue = goodinseconds / monthinseconds * 100
            setMetadata('sla-' + self.name + '::30daybad', countbad)
            # self.data = setmd(self.data, '30daybad', countbad)
            setMetadata('sla-' + self.name + '::30lastcompute', int(now.timestamp()))
            # self.data = setmd(self.data, '30lastcompute', int(now.timestamp()))
            self.save()
        except:
            dbg("could not compute SLA for " + self.name)
        # compute last 60 days
        twomonthbefore = now - datetime.timedelta(days=60)
        try:
            events = SlaLog.objects.filter(timestamp__range=[twomonthbefore, now], sla=self).order_by('pk')
            countbad = 0
            if events[0].event == 'bad':
                lastevent = 'good'
                lastbad = events[0].timestamp
                lastgood = twomonthbefore
            elif events[0].event == 'good':
                lastevent = 'bad'
                lastgood = events[0].timestamp
                lastbad = twomonthbefore
                countbad = countbad + 1
            badintervals = []
            for event in events:
                if event.event == 'bad' and lastevent == 'good':
                    countbad = countbad + 1
                    lastevent = 'bad'
                # elif event.event == 'good' and lastevent == 'bad':
                #     countbad = countbad + 1
                #     lastevent = 'good'
            # self.data = setmd(self.data, '60daybad', countbad)
            setMetadata('sla-' + self.name + '::60daybad', countbad)
            # self.data = setmd(self.data, '60lastcompute', int(now.timestamp()))
            setMetadata('sla-' + self.name + '::60lastcompute', int(now.timestamp()))
            # self.save()
        except:
            dbg("could not compute 60 day SLA for " + self.name)
        # compute last 90 days
        threemonthbefore = now - datetime.timedelta(days=90)
        try:
            events = SlaLog.objects.filter(timestamp__range=[threemonthbefore, now], sla=self).order_by('pk')
            lastevent = events[0].event
            if lastevent == 'bad':
                lastbad = events[0].timestamp
                lastgood = None
            elif lastevent == 'good':
                lastgood = events[0].timestamp
                lastbad = None
            badintervals = []
            countbad = 0
            for event in events:
                if event.event == 'bad' and lastevent == 'good':
                    countbad = countbad + 1
                    lastevent = 'bad'
            # self.data = setmd(self.data, '90daybad', countbad)
            setMetadata('sla-' + self.name + '::90daybad', countbad)
            # self.data = setmd(self.data, '90lastcompute', int(now.timestamp()))
            setMetadata('sla-' + self.name + '::90lastcompute', int(now.timestamp()))
            # self.save()
        except:
            dbg("could not compute 90 day SLA for " + self.name)
        # Compute last 180 days
        sixmonthbefore = now - datetime.timedelta(days=180)
        try:
            events = SlaLog.objects.filter(timestamp__range=[sixmonthbefore, now], sla=self).order_by('pk')
            lastevent = events[0].event
            if lastevent == 'bad':
                lastbad = events[0].timestamp
                lastgood = None
            elif lastevent == 'good':
                lastgood = events[0].timestamp
                lastbad = None
            badintervals = []
            countbad = 0
            for event in events:
                if event.event == 'bad' and lastevent == 'good':
                    countbad = countbad + 1
                    lastevent = 'bad'
            # self.data = setmd(self.data, '180daybad', countbad)
            setMetadata('sla-' + self.name + '::180daybad', countbad)
            # self.data = setmd(self.data, '180lastcompute', int(now.timestamp()))
            setMetadata('sla-' + self.name + '::180lastcompute', int(now.timestamp()))
            # self.save()
        except:
            dbg("could not compute 180 day SLA for " + self.name)
        # Compute last year
        twelvemonthbefore = now - datetime.timedelta(days=365)
        try:
            events = SlaLog.objects.filter(timestamp__range=[twelvemonthbefore, now], sla=self).order_by('pk')
            lastevent = events[0].event
            if lastevent == 'bad':
                lastbad = events[0].timestamp
                lastgood = None
            elif lastevent == 'good':
                lastgood = events[0].timestamp
                lastbad = None
            badintervals = []
            countbad = 0
            for event in events:
                if event.event == 'bad' and lastevent == 'good':
                    countbad = countbad + 1
                    lastevent = 'bad'
            setMetadata('sla-' + self.name + '::365daybad', countbad)
            setMetadata('sla-' + self.name + '::365lastcompute', int(now.timestamp()))
            # self.save()
        except:
            dbg("could not compute 365 day SLA for " + self.name)
        return True

    class Meta:
        verbose_name = 'Service Level Agreement'
        verbose_name_plural = 'SLAs'
        ordering = ['name']


class EventLog(models.Model):
    """
    This model stores event data related to the thresholds, related to :model:`scheduler.Sla`.
    """
    EVENT_CHOICES = (('bad', 'Failure'), ('good', 'Restored'))
    sla = models.ForeignKey('Sla', on_delete=models.PROTECT, null=True, blank=True,
                            help_text='SLA this data relates to.')
    hostcheck = models.ForeignKey('HostChecks', on_delete=models.PROTECT, null=True, blank=True,
                                  help_text='Check this data relates to.')
    host = models.ForeignKey('Hosts', on_delete=models.PROTECT, null=True, blank=True,
                             help_text='Host this data relates to.')
    threshold = models.ForeignKey('Thresholds', blank=True, null=True, help_text='Threshold the data relates to.')
    event = models.CharField('Event', max_length=4, choices=EVENT_CHOICES, default='bad',
                             help_text='What type of event are we logging.')
    value = models.CharField('Value', max_length=4096, help_text='Value of the event.')
    data = models.CharField('Metadata', max_length=4096, default='{}', help_text='JSON encoded metadata')
    timestamp = models.DateTimeField('Timestamp', auto_now_add=True, help_text='Timestamp for the event.')

    def __str__(self):
        return str(self.threshold.name) + ' on ' + str(self.hostcheck.name) + ' ' + str(
            get_choicename(self, 'event')[1]) + ' -> ' + str(self.value) + ' @ ' + str(self.timestamp)

    class Meta:
        verbose_name = 'Threshold Event Log'
        verbose_name_plural = 'Threshold Events'
        ordering = ['-pk']


class SlaLog(models.Model):
    """
    This model stores event data related to the SLA, related to :model:`scheduler.Sla`.
    """
    EVENT_CHOICES = (('bad', 'Failure'), ('good', 'Restored'))
    sla = models.ForeignKey('Sla', on_delete=models.PROTECT, null=True, blank=True,
                            help_text='SLA this data relates to.')
    event = models.CharField('Event', max_length=4, choices=EVENT_CHOICES, default='bad',
                             help_text='What type of event are we logging.')
    data = models.CharField('Metadata', max_length=4096, default='{}', help_text='JSON encoded metadata')
    timestamp = models.DateTimeField('Timestamp', auto_now_add=True, help_text='Timestamp for the event.')

    def __str__(self):
        return str(self.sla.name) + ' ' + str(get_choicename(self, 'event')[1]) + ' -> ' + str(
            self.event) + ' @ ' + str(self.timestamp)

    class Meta:
        verbose_name = 'Sla Log'
        verbose_name_plural = 'SLA Event Log'
        ordering = ['-pk']


class ErrorLog(models.Model):
    """
    This model stores error data related to the hostchecks, related to :model:`scheduler.Hostchecks`.
    """
    hostcheck = models.ForeignKey('HostChecks', on_delete=models.PROTECT, null=True, blank=True,
                                  help_text='Check this data relates to.')
    host = models.ForeignKey('Hosts', on_delete=models.PROTECT, null=True, blank=True,
                             help_text='Host this data relates to.')
    event = models.CharField('Event', max_length=64, help_text='What was the exception.')
    error = models.CharField('Error', max_length=4096, null=True, blank=True, help_text='Verbose text of the error.')
    value = models.CharField('Value', max_length=4096, null=True, blank=True, help_text='Value of the check.')
    data = models.CharField('Metadata', max_length=4096, default='{}', help_text='JSON encoded metadata')
    timestamp = models.DateTimeField('Timestamp', auto_now_add=True, help_text='Timestamp for the event.')

    def __str__(self):
        return str(self.hostcheck.name) + ' on ' + str(self.host.name) + ' got ' + ' [' + self.event + '] with ' + str(
            self.value) + ' -> ' + self.error + ' @ ' + str(self.timestamp)

    class Meta:
        verbose_name = 'Check Error Log'
        verbose_name_plural = 'Error Log'


class Metadata(models.Model):
    """
    This model stores meta data for all models.
    """
    key = models.CharField('Key', max_length=128, unique=True, help_text='Key to the data.')
    data = models.CharField('Data', max_length=4096, default='{}', null=True, blank=True,
                            help_text='JSON encoded metadata')
    timestamp = models.DateTimeField('Timestamp', auto_now=True, help_text='Timestamp for the last write to this key.')

    def __str__(self):
        return str(self.key)

    class Meta:
        verbose_name = 'Metadata'
        verbose_name_plural = 'Metadata'


class Trap(models.Model):
    """
    This model stores traps received by the sink
    """
    host = models.ForeignKey('Hosts', on_delete=models.PROTECT, null=True, blank=True,
                             help_text='Host this data relates to.')
    oid = models.CharField('OID', max_length=128, help_text='OID received.')
    value = models.CharField('Value', max_length=4096, help_text='Message received')
    timestamp = models.DateTimeField('Timestamp', auto_now=True, db_index=True, help_text='Timestamp for the event.')

    def __str__(self):
        return str(self.oid + ' = ' + self.value)

    class Meta:
        verbose_name = 'Trap'
        verbose_name_plural = 'Traps'
        ordering = ['-pk']


class Template(models.Model):
    """
    This model stores the templates used to send email alerts
    """
    OBJ_CHOICES = (('sla', 'SLA'), ('thold', 'Threshold'), ('error', 'Error'), ('trap', 'Trap'))
    EVENT_CHOICES = (('warn', 'Warning'), ('crit', 'Critical'), ('ok', 'Recovery'), ('err', 'Error'))
    name = models.SlugField('Name', max_length=128, help_text='Slug for the Template.')
    verbosename = models.CharField('Full Name', max_length=256, help_text='Verbose name as displayed.')
    obj = models.CharField('Object type', max_length=32, choices=OBJ_CHOICES, blank=False, null=False,
                           help_text='The object type this template relates to.')
    event = models.CharField('Event type', max_length=32, choices=EVENT_CHOICES, blank=False, null=False,
                             help_text='The event type this template relates to.')
    subject = models.TextField('Template Subject', help_text='The template subject, django template syntax supported.')
    content = models.TextField('Template Content', help_text='The template content, django template syntax supported.')
    timestamp = models.DateTimeField('Timestamp', auto_now=True, help_text='Last modification date.')

    def __str__(self):
        return str(self.verbosename)

    class Meta:
        verbose_name = 'Template'
        verbose_name_plural = 'Templates'
        ordering = ['-pk']


# noinspection PyUnusedLocal,PyUnusedLocal,PyUnusedLocal
@receiver(post_save, sender=SlaLog, dispatch_uid="compute_the_sla")
# Each time a record in save in the SLA log, we compute the SLA for the related SLA
# We need to call this from a cronjob before doing the reporting in case there is an open incident
def do_sla(sender, instance, **kwargs):
    instance.sla.computeSLA()
    return True


@receiver(post_save, sender=EventLog, dispatch_uid="do_the_sla")
# Since a thold event does not necessarily equal a sla event, we log all events to the eventlog and
# this signal handler handles writing to the SlaLog table to trigger and SLA event if required
def do_events(sender, instance, **kwargs):
    if instance.event == 'bad' and instance.sla.status != 'failing':
        # Failing from a good state
        # dbg("instance is bad")
        if instance.sla.allchecks is True:
            # Require to fail all checks assigned to this sla to trigger an event
            # Keep in mind that each check can then have allhost set and then needs to check all hosts.
            # dbg('this one has allchecks on')
            totalchecks = 0
            failedchecks = 0
            checks = HostChecks.objects.filter(sla=instance.sla, sla__enabled=True, enabled=True)
            for check in checks:
                totalchecks = totalchecks + 1
                # dbg('checking check named ' + check.name)
                if getMetadata(check.name + '::globalstatus', 'OK') == 'failed':
                    failedchecks = failedchecks + 1
            if totalchecks - failedchecks == 0:
                # dbg("totalchecks VS failedchecks: " + str(totalchecks) + " / " + str(failedchecks))
                setMetadata('sla-' + instance.sla.name + '::laststatus', instance.sla.status)
                instance.sla.status = 'failing'
                timefailed = int(getMetadata('sla-' + instance.sla.name + '::timefailed', 0))
                instance.sla.data = setmd(instance.sla.data, 'timefailed', timefailed + 1)
                setMetadata('sla-' + instance.sla.name + '::timefailed', str(timefailed + 1))
                instance.sla.save()
                SlaLog(sla=instance.sla, event='bad', data=instance.sla.data).save()
        else:
            # We fail the sla since the check failed and allchecks is false.  AllHost is supposed to have been checked already at this point
            setMetadata('sla-' + instance.sla.name + '::laststatus', instance.sla.status)
            instance.sla.status = 'failing'
            timefailed = int(getMetadata('sla-' + instance.sla.name + '::timefailed', 0))
            instance.sla.data = setmd(instance.sla.data, 'timefailed', timefailed + 1)
            setMetadata('sla-' + instance.sla.name + '::timefailed', str(timefailed + 1))
            instance.sla.save()
            SlaLog(sla=instance.sla, event='bad', data=instance.sla.data).save()
    elif instance.event == 'good' and instance.sla.status != 'OK':
        # We become good from a bad state
        # dbg('her I guess I become good')
        totalchecks = 0
        failedchecks = 0
        
        # It is also an issue for users who dont log on often and have lots of threshold events.
        add_msg('25',
                instance.hostcheck.name + ' on ' + instance.host.name + ' suceeded threshold named ' + instance.threshold.name + ' with value ' + str(
                    instance.value), instance.threshold.warngroups.all())
        checks = HostChecks.objects.filter(sla=instance.sla, sla__enabled=True, enabled=True)
        # dbg(checks)
        for check in checks:
            totalchecks = totalchecks + 1
            # dbg('checking check named ' + check.name)
            if getMetadata(check.name + '::globalstatus', 'OK') == 'failed':
                failedchecks = failedchecks + 1
        # dbg("totalchecks VS failedchecks: " + str(totalchecks) + " / " + str(failedchecks))
        if instance.sla.allchecks is True and totalchecks - failedchecks != 0:
            # Allcheck is true and we have at least one good check
            # dbg("totalchecks VS failedchecks: " + str(totalchecks) + " / " + str(failedchecks))
            setMetadata('sla-' + instance.sla.name + '::laststatus', instance.sla.status)
            instance.sla.status = 'OK'
            timerecovered = int(getMetadata('sla-' + instance.sla.name + '::timerecovered', 0))
            instance.sla.data = setmd(instance.sla.data, 'timerecovered', timerecovered + 1)
            setMetadata('sla-' + instance.sla.name + '::timerecovered', timerecovered + 1)
            instance.sla.save()
            SlaLog(sla=instance.sla, event='good', data=instance.sla.data).save()
        elif totalchecks - failedchecks == totalchecks:
            # allchecks is false and we have no failed checks
            setMetadata('sla-' + instance.sla.name + '::laststatus', instance.sla.status)
            instance.sla.status = 'OK'
            timerecovered = int(getMetadata('sla-' + instance.sla.name + '::timerecovered', 0))
            instance.sla.data = setmd(instance.sla.data, 'timerecovered', timerecovered + 1)
            setMetadata('sla-' + instance.sla.name + '::timerecovered', timerecovered + 1)
            instance.sla.save()
            SlaLog(sla=instance.sla, event='good', data=instance.sla.data).save()
    return True


# the two next signal handlers are very ghetto, but they mostly work.  need to put some work here
@receiver(m2m_changed, sender=HostChecks.hosts.through, dispatch_uid="Create_them_models")
def create_them_models(sender, instance, action, reverse, *args, **kwargs):
    # Create the celery task to update the check
    global Widgets
    if action == 'post_add' and not reverse:
        for host in instance.hosts.all():
            try:
                gettask = PeriodicTask.objects.get(name=host.name + '-' + instance.name)
            except Exception as e:
                dbg(e)
                gettask = None
            if gettask is None:
                task = PeriodicTask(name=host.name + '-' + instance.name,
                                    interval=IntervalSchedule.objects.get(every=instance.interval),
                                    task=instance.checktype, args='["' + host.name + '", "' + instance.name + '"]',
                                    last_run_at=timezone.now(), exchange=None, routing_key=None, queue=None)
                task.save()
            else:
                gettask.name = host.name + '-' + instance.name
                gettask.enabled = instance.enabled
                gettask.interval = IntervalSchedule.objects.get(every=instance.interval)
                gettask.args = '["' + host.name + '", "' + instance.name + '"]'
                gettask.save()
            print(host.name + '-' + instance.name)
            try:
                from webview.models import Widgets
                getwidget = Widgets.objects.get(name=host.name + '-' + instance.name)
            except Exception as e:
                dbg(e)
                getwidget = None
            # Autocreating widets
            if getwidget is None:
                widget = Widgets(name=host.name + '-' + instance.name, verbosename=instance.verbosename,
                                 hostcheck=instance, host=host, unit=instance.unit, template=instance.checktype)
                widget.save()
            else:
                getwidget.name = host.name + '-' + instance.name
                getwidget.verbosename = instance.verbosename
                getwidget.active = instance.enabled
                getwidget.unit = instance.unit
                getwidget.template = instance.checktype
                getwidget.save()

            try:
                getwidgetgraph = Widgets.objects.get(name=host.name + '-' + instance.name + '-graph')
            except Exception as e:
                dbg(e)
                getwidgetgraph = None
            if getwidgetgraph is None:
                widgetgraph = Widgets(name=host.name + '-' + instance.name + '-graph',
                                      verbosename=instance.verbosename + ' Graph', hostcheck=instance, host=host,
                                      unit=instance.unit, template=instance.checktype + 'graph')
                widgetgraph.save()
            else:
                getwidgetgraph.name = host.name + '-' + instance.name + '-graph'
                getwidgetgraph.verbosename = instance.verbosename + ' Graph'
                getwidgetgraph.active = instance.enabled
                getwidgetgraph.unit = instance.unit
                getwidgetgraph.template = instance.checktype + 'graph'
                getwidgetgraph.save()

            try:
                getwidgetinfo = Widgets.objects.get(name=host.name + '-' + instance.name + '-info')
            except Exception as e:
                dbg(e)
                getwidgetinfo = None
            if getwidgetinfo is None:
                widgetinfo = Widgets(name=host.name + '-' + instance.name + '-info',
                                     verbosename=instance.verbosename + ' Info', hostcheck=instance, host=host,
                                     unit=instance.unit, template=instance.checktype + 'info')
                widgetinfo.save()
            else:
                getwidgetinfo.name = host.name + '-' + instance.name + '-info'
                getwidgetinfo.verbosename = instance.verbosename + ' Info'
                getwidgetinfo.active = instance.enabled
                getwidgetinfo.unit = instance.unit
                getwidgetinfo.template = instance.checktype + 'info'
                getwidgetinfo.save()
    return True


@receiver(post_save, sender=HostChecks, dispatch_uid="edit_hostchecks")
def edit_hostchecks(sender, instance, **kwargs):
    # Create the celery task to update the check
    global Widgets
    for host in instance.hosts.all():
        try:
            gettask = PeriodicTask.objects.get(name=host.name + '-' + instance.name)
        except Exception as e:
            dbg(e)
            gettask = None
        if gettask is None:
            task = PeriodicTask(name=host.name + '-' + instance.name,
                                interval=IntervalSchedule.objects.get(every=instance.interval), task=instance.checktype,
                                args='["' + host.name + '", "' + instance.name + '"]', last_run_at=timezone.now(),
                                exchange=None, routing_key=None, queue=None)
            task.save()
        else:
            gettask.name = host.name + '-' + instance.name
            gettask.enabled = instance.enabled
            gettask.interval = IntervalSchedule.objects.get(every=instance.interval)
            gettask.args = '["' + host.name + '", "' + instance.name + '"]'
            gettask.save()

        try:
            from webview.models import Widgets
            getwidget = Widgets.objects.get(name=host.name + '-' + instance.name)
        except Exception as e:
            dbg(e)
            getwidget = None
        # Autocreating widets
        if getwidget is None:
            widget = Widgets(name=host.name + '-' + instance.name, verbosename=instance.verbosename, hostcheck=instance,
                             host=host, unit=instance.unit, template=instance.checktype)
            widget.save()
        else:
            getwidget.name = host.name + '-' + instance.name
            getwidget.verbosename = instance.verbosename
            getwidget.active = instance.enabled
            getwidget.unit = instance.unit
            getwidget.template = instance.checktype
            getwidget.save()

        try:
            getwidgetgraph = Widgets.objects.get(name=host.name + '-' + instance.name + '-graph')
        except Exception as e:
            dbg(e)
            getwidgetgraph = None
        if getwidgetgraph is None:
            widgetgraph = Widgets(name=host.name + '-' + instance.name + '-graph',
                                  verbosename=instance.verbosename + ' Graph', hostcheck=instance, host=host,
                                  unit=instance.unit, template=instance.checktype + 'graph')
            widgetgraph.save()
        else:
            getwidgetgraph.name = host.name + '-' + instance.name + '-graph'
            getwidgetgraph.verbosename = instance.verbosename + ' Graph'
            getwidgetgraph.active = instance.enabled
            getwidgetgraph.unit = instance.unit
            getwidgetgraph.template = instance.checktype + 'graph'
            getwidgetgraph.save()

        try:
            getwidgetinfo = Widgets.objects.get(name=host.name + '-' + instance.name + '-info')
        except Exception as e:
            dbg(e)
            getwidgetinfo = None
        if getwidgetinfo is None:
            widgetinfo = Widgets(name=host.name + '-' + instance.name + '-info',
                                 verbosename=instance.verbosename + ' Info', hostcheck=instance, host=host,
                                 unit=instance.unit, template=instance.checktype + 'info')
            widgetinfo.save()
        else:
            getwidgetinfo.name = host.name + '-' + instance.name + '-info'
            getwidgetinfo.verbosename = instance.verbosename + ' Info'
            getwidgetinfo.active = instance.enabled
            getwidgetinfo.unit = instance.unit
            getwidgetinfo.template = instance.checktype + 'info'
            getwidgetinfo.save()
    return True


# Better to use the ErrorLog management comment on a cronjob or to use ossec.

@receiver(post_save, sender=ErrorLog, dispatch_uid="report_error")
def error_to_ui(sender, instance, **kwargs):
    # When an error gets logged, we want to display a notification for it in the UI
    from webview.models import UserView
    host = None
    hostcheck = None
    if isinstance(instance.host, Hosts):
        host = instance.host.name
    elif isinstance(instance.host, str):
        host = instance.host
    if isinstance(instance.hostcheck, HostChecks):
        hostcheck = instance.hostcheck.name
    elif isinstance(instance.hostcheck, str):
        hostcheck = instance.hostcheck
    if getMetadata(host + ':' + hostcheck + '::notifs', 'True') == 'True':
        groups = UserView.objects.filter(widgets__name=host + '-' + hostcheck).values_list('group',
                                                                                           flat=True).distinct()
        add_msg(level='99', msg=instance, groups=groups)
    return True
