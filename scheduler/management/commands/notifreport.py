from django.core.management.base import BaseCommand, CommandError
from webview.models import UserProfile, Widgets, UserView
from scheduler.models import Hosts, HostChecks, Historical, EventLog, Sla, SlaLog
from django.contrib.auth.models import Group, User
# from tools import dbg, setmd, getmd, loadmd, savemd, getMetadata, setMetadata
# import datetime
# from django.template.loader import render_to_string
# from django.core.mail import send_mass_mail
from django.utils import timezone


class Command(BaseCommand):
    help = 'Notification Report'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Who gets notified ?'))
        check=HostChecks.objects.filter(enabled=True)

        for c in check:
            if c.sla.count() > 0 or c.threshold.count() > 0:
                self.stdout.write(self.style.SUCCESS(c.name))
                for t in c.threshold.filter(enabled=True):
                    self.stdout.write("   Threshold name: " + t.name)
                    str='       Warn groups: '
                    for w in t.warngroups.all():
                        str=str + w.name + " "
                    self.stdout.write(str)
                    str='       Crit groups: '
                    for crit in t.critgroups.all():
                        str=str + crit.name + " "
                    self.stdout.write(str)
                for s in c.sla.filter(enabled=True):
                    self.stdout.write("   SLA name: " + s.name)
                    str='       Warn groups: '
                    for w in s.warngroups.all():
                        str=str + w.name + " "
                    self.stdout.write(str)
                    str='       Crit groups: '
                    for crit in s.critgroups.all():
                        str=str + crit.name + " "
                    self.stdout.write(str)



