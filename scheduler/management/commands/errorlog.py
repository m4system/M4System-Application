from django.core.management.base import BaseCommand, CommandError
from webview.models import UserProfile
from scheduler.models import ErrorLog
from django.contrib.auth.models import Group, User
from tools import dbg
import datetime
from django.template.loader import render_to_string
from django.core.mail import send_mass_mail
from django.utils import timezone
from django.conf import settings


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
