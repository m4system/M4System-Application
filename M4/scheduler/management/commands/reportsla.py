import datetime

from django.contrib.auth.models import User
from django.core.mail import send_mass_mail
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils import timezone

from M4.scheduler.models import Sla, SlaLog
from M4.System.tools import getMetadata
from M4.DashboardDisplayPlugin.webview_models import UserProfile


def convertEvent(event):
    if event == "good":
        return "Threshold succeeded"
    elif event == "bad":
        return "Threshold exceeded"
    else:
        return event


class Command(BaseCommand):
    help = 'Report on SLAs'

    def handle(self, *args, **options):
        now = timezone.now()
        onemonthbefore = now - datetime.timedelta(days=30)
        twomonthbefore = now - datetime.timedelta(days=60)
        threemonthbefore = now - datetime.timedelta(days=90)
        sixmonthbefore = now - datetime.timedelta(days=180)
        twelvemonthbefore = now - datetime.timedelta(days=365)
        t = 'emailtpl/report.html'
        emails = []

        for user in User.objects.all():
            data = {'username': user.username, 'slas': {}}
            self.stdout.write("Report for user " + user.username)
            self.stdout.write(' ')
            slas = {}
            for sla in Sla.objects.filter(enabled=True,
                                          critgroups__name__in=user.groups.all().values_list('name', flat=True)):
                slas[sla.name] = {
                    '30daybad': {'count': str(getMetadata('sla-' + sla.name + '::30daybad')), 'slalog': []},
                    'note': sla.note}
                if sla.note != '':
                    title = " Statistics for " + sla.name + " (" + sla.note + "):"
                else:
                    title = " Statistics for " + sla.name + ":"
                self.stdout.write(title)
                self.stdout.write(
                    "     SLA events in the past 30 days: " + str(getMetadata('sla-' + sla.name + '::30daybad')))
                for log in SlaLog.objects.filter(timestamp__range=[onemonthbefore, now], sla=sla).order_by('pk'):
                    slas[sla.name]['30daybad']['slalog'].append(
                        "         " + log.timestamp.strftime('%Y-%m-%d %H:%M:%S %Z') + " -> " + convertEvent(log.event))
                    self.stdout.write(
                        "         " + log.timestamp.strftime('%Y-%m-%d %H:%M:%S %Z') + " -> " + convertEvent(log.event))
                self.stdout.write(
                    "     SLA events in the past 60 days: " + str(getMetadata('sla-' + sla.name + '::60daybad')))
                slas[sla.name]['60daybad'] = {'count': str(getMetadata('sla-' + sla.name + '::60daybad')), 'slalog': []}
                for log in SlaLog.objects.filter(timestamp__range=[twomonthbefore, onemonthbefore], sla=sla).order_by(
                        'pk'):
                    slas[sla.name]['60daybad']['slalog'].append(
                        "         " + log.timestamp.strftime('%Y-%m-%d %H:%M:%S %Z') + " -> " + convertEvent(log.event))
                    self.stdout.write(
                        "         " + log.timestamp.strftime('%Y-%m-%d %H:%M:%S %Z') + " -> " + convertEvent(log.event))
                self.stdout.write(
                    "     SLA events in the past 90 days: " + str(getMetadata('sla-' + sla.name + '::90daybad')))
                slas[sla.name]['90daybad'] = {'count': str(getMetadata('sla-' + sla.name + '::90daybad')), 'slalog': []}
                for log in SlaLog.objects.filter(timestamp__range=[threemonthbefore, twomonthbefore], sla=sla).order_by(
                        'pk'):
                    slas[sla.name]['90daybad']['slalog'].append(
                        "         " + log.timestamp.strftime('%Y-%m-%d %H:%M:%S %Z') + " -> " + convertEvent(log.event))
                    self.stdout.write(
                        "         " + log.timestamp.strftime('%Y-%m-%d %H:%M:%S %Z') + " -> " + convertEvent(log.event))
                self.stdout.write(
                    "     SLA events in the past 180 days: " + str(getMetadata('sla-' + sla.name + '::180daybad')))
                slas[sla.name]['180daybad'] = {'count': str(getMetadata('sla-' + sla.name + '::180daybad')),
                                               'slalog': []}
                for log in SlaLog.objects.filter(timestamp__range=[sixmonthbefore, threemonthbefore], sla=sla).order_by(
                        'pk'):
                    slas[sla.name]['180daybad']['slalog'].append(
                        "         " + log.timestamp.strftime('%Y-%m-%d %H:%M:%S %Z') + " -> " + convertEvent(log.event))
                    self.stdout.write(
                        "         " + log.timestamp.strftime('%Y-%m-%d %H:%M:%S %Z') + " -> " + convertEvent(log.event))
                self.stdout.write(
                    "     SLA events in the past 365 days: " + str(getMetadata('sla-' + sla.name + '::365daybad')))
                slas[sla.name]['365daybad'] = {'count': str(getMetadata('sla-' + sla.name + '::365daybad')),
                                               'slalog': []}
                for log in SlaLog.objects.filter(timestamp__range=[twelvemonthbefore, sixmonthbefore],
                                                 sla=sla).order_by('pk'):
                    slas[sla.name]['365daybad']['slalog'].append(
                        "         " + log.timestamp.strftime('%Y-%m-%d %H:%M:%S %Z') + " -> " + convertEvent(log.event))
                    self.stdout.write(
                        "         " + log.timestamp.strftime('%Y-%m-%d %H:%M:%S %Z') + " -> " + convertEvent(log.event))
            self.stdout.write(' ')
            self.stdout.write(' ')
            data['slas'] = slas
            c = {'data': data}
            # dbg(data)
            rendered = render_to_string(t, c)
            mail = UserProfile.objects.get(user=user).notifemail
            if mail is not None and mail != '':
                emails.append(('[M4] Monthly Report', rendered, 'm4@m4system.com', [mail]))
        send_mass_mail(tuple(emails), fail_silently=False)
        self.stdout.write(self.style.SUCCESS('Reporting done.'))
