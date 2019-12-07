import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from scheduler.models import ErrorLog


class Command(BaseCommand):
    help = 'Report on ErrorLog'

    def handle(self, *args, **options):
        now = timezone.now()
        yesterday = now - datetime.timedelta(days=1)
        errors = ErrorLog.objects.filter(timestamp__range=[yesterday, now])
        if errors is not None:
            self.stdout.write("ErrorLog Report")
            self.stdout.write("     Errors in the last 24 hours:")
            for error in errors:
                self.stdout.write("     " + str(error))
            self.stdout.write(self.style.SUCCESS('Reporting done.'))
