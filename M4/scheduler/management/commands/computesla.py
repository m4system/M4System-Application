from django.core.management.base import BaseCommand

from scheduler.models import Sla


class Command(BaseCommand):
    help = 'Recompute all SLAs'

    def handle(self, *args, **options):
        for sla in Sla.objects.filter(enabled=True):
            sla.computeSLA()
            self.stdout.write(self.style.SUCCESS('Successfully recomputed "%s"' % sla.name))
        self.stdout.write(self.style.SUCCESS('All SLA done.'))
