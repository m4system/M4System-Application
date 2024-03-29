from celery import shared_task
from easysnmp import snmp_get
from pprint import pprint
from M4.System.signals import post_fetch
from M4.System.tools import error, dbg, die

from M4.System.signals import post_fetch
from django.dispatch import receiver
from M4.System.tools import error, dbg, die


@shared_task(bind=True, name='snmp_source')
def snmp_source(self, oid, version, datatype, datasource, datapoint):
    # do snmp get here
    # pprint(vars(self))
    res = str(snmp_get(oid, hostname=datasource, community='public', version=int(version)).value)

    post_fetch.send(sender='M4.SNMPSourcePlugin', retval=res, datatype=datatype, datapoint=datapoint)

    return res
