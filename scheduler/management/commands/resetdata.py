from django.core.cache import cache
from django.core.management.base import BaseCommand

from scheduler.models import HostChecks, Historical, Sla, EventLog, SlaLog, ErrorLog, Metadata
from webview.models import UIMsg


# totally reset all data

class Command(BaseCommand):
    help = 'Reset all datapoints'

    def handle(self, *args, **options):
        cache.clear()
        self.stdout.write(self.style.SUCCESS('Successfully cleared cache'))
        Historical.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully wiped Historicals'))
        EventLog.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully wiped EventLog'))
        SlaLog.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully wiped SlaLog'))
        ErrorLog.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully wiped ErrorLog'))
        Metadata.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully wiped Metadata'))
        for hostcheck in HostChecks.objects.all():
            hostcheck.data = '{}'
            hostcheck.hoststatus = '{}'
            hostcheck.status = '{}'
            hostcheck.save()
        self.stdout.write(self.style.SUCCESS('Successfully reset HostChecks metadata'))
        for sla in Sla.objects.all():
            sla.status = 'OK'
            sla.currentvalue = 100
            sla.data = '{}'
            sla.save()
        self.stdout.write(self.style.SUCCESS('Successfully reset Sla metadata'))
        UIMsg.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully wiped UIMsg'))
        self.stdout.write(self.style.SUCCESS('All data points reset.'))
