from scheduler.models import Trap, Hosts
from tools import dbg
from django.core.management.base import BaseCommand, CommandError
import sys

class Command(BaseCommand):
    help = 'Import a Trap'

    def handle(self, *args, **options):
        # for sla in Sla.objects.filter(enabled=True):
        #     sla.computeSLA()
        #     self.stdout.write(self.style.SUCCESS('Successfully recomputed "%s"' % sla.name))
        stdin = sys.stdin.readlines()
        dbg(stdin)
        for data in stdin:
            msg = data.split(' | ')
            try:
                host = Hosts.objects.get(name=msg[0])
            except:
                host = None
            if msg[3][0:9] == '"Message:':
                Trap(host=host, oid=msg[2], value=msg[3][9:-3]).save()
            elif msg[3][0:8] == '"Active:':
                Trap(host=host, oid=msg[2], value=msg[3][8:-3]).save()
            else:
                dbg('Trap message not worth seeing: ' + msg[3])
