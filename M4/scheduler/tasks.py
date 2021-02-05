from __future__ import absolute_import

import traceback
from time import time

from celery import shared_task
from django.utils import timezone

# import sh
from M4.scheduler.tools import setMetadata, getMetadata
from .models import Hosts, HostChecks, ErrorLog
from .utils import computeint, computebool, computestr

from easysnmp import snmp_get

# Defines the celery task available.  Links to the checktypes

# this needs a better approach
checkname = None
hostname = None
res = None


@shared_task(bind=True, name='snmpgetint')
def snmpgetint(self, host, check):
    global checkname
    global hostname
    global res
    try:
        print('doing ' + check + ' on ' + host)
        hostname = Hosts.objects.get(name=host)
        if hostname.enabled is True:
            checkname = HostChecks.objects.get(name=check)
            address = hostname.address
            community = hostname.community
            oid = checkname.arg
            res = str(float(snmp_get(oid, hostname=address, community=community, version=1).value) * float(checkname.quotient))
            computeint(checkname, hostname, res)
            print(oid + ' on ' + address + ' equals ' + res)
    except Exception as e:
        print('doing ' + checkname.name + ' on ' + hostname.name + ' failed')
        print(traceback.format_exc())
        # update the error count
        setMetadata(hostname.name + ':' + checkname.name + '::lasterror', str(timezone.now()))
        setMetadata(hostname.name + ':' + checkname.name + '::nberror',
                    int(getMetadata(hostname.name + ':' + checkname.name + '::nberror', 0)) + 1)
        # Log the error to the database.
        ErrorLog(hostcheck=checkname, host=hostname, event=e.__class__.__name__, error=str(e), value=res).save()
    return res


@shared_task(bind=True, name='snmpgetstr')
def snmpgetstr(self, host, check):
    res = None
    try:
        print('doing ' + check + ' on ' + host)
        host = Hosts.objects.get(name=host)
        if host.enabled is True:
            check = HostChecks.objects.get(name=check)
            address = host.address
            community = host.community
            oid = check.arg
            res = str(snmp_get(oid, hostname=address, community=community, version=1).value)
            computestr(check, host, res)
            print(oid + ' on ' + address + ' equals ' + res)
    except Exception as e:
        print('doing ' + check.name + ' on ' + host.name + ' failed')
        # update the error count
        setMetadata(host.name + ':' + check.name + '::lasterror', str(timezone.now()))
        setMetadata(host.name + ':' + check.name + '::nberror',
                    int(getMetadata(host.name + ':' + check.name + '::nberror', 0)) + 1)
        # Log the error to the database.
        ErrorLog(hostcheck=check, host=host, event=e.__class__.__name__, error=str(e), value=res).save()
    return res


@shared_task(bind=True, name='snmpgetbool')
def snmpgetbool(self, host, check):
    res = None
    try:
        print('doing ' + check + ' on ' + host)
        host = Hosts.objects.get(name=host)
        if host.enabled is True:
            check = HostChecks.objects.get(name=check)
            address = host.address
            community = host.community
            oid = check.arg
            res = str(snmp_get(oid, hostname=address, community=community, version=1).value)
            computebool(check, host, res)
            print(oid + ' on ' + address + ' equals ' + res)
    except Exception as e:
        print('doing ' + check.name + ' on ' + host.name + ' failed')
        # update the error count
        setMetadata(host.name + ':' + check.name + '::lasterror', str(timezone.now()))
        setMetadata(host.name + ':' + check.name + '::nberror',
                    int(getMetadata(host.name + ':' + check.name + '::nberror', 0)) + 1)
        # Log the error to the database.
        ErrorLog(hostcheck=check, host=host, event=e.__class__.__name__, error=str(e), value=res).save()
    return res


@shared_task(bind=True, name='dump')
def dump_context(self):
    return 'Executing task id {0.id}, args: {0.args!r} kwargs: {0.kwargs!r}'.format(self.request)


@shared_task(bind=True, name='execint')
def execint(self, host, check):
    res = None
    try:
        print('doing ' + check + ' on ' + host)
        host = Hosts.objects.get(name=host)
        check = HostChecks.objects.get(name=check)
        if host.enabled is True and check.enabled is True:
            run = sh.Command("./bin/runthis.sh")
            res = str(float(run(check.arg)) * float(check.quotient))
            computeint(check, host, res)
            print(oid + ' on ' + address + ' equals ' + res)
    except Exception as e:
        print('doing ' + check.name + ' on ' + host.name + ' failed')
        # update the error count
        setMetadata(host.name + ':' + check.name + '::lasterror', str(timezone.now()))
        setMetadata(host.name + ':' + check.name + '::nberror',
                    int(getMetadata(host.name + ':' + check.name + '::nberror', 0)) + 1)
        # Log the error to the database.
        ErrorLog(hostcheck=check, host=host, event=e.__class__.__name__, error=str(e), value=res).save()
    return res


@shared_task(bind=True, name='execbool')
def execbool(self, host, check):
    res = None
    try:
        print('doing ' + check + ' on ' + host)
        host = Hosts.objects.get(name=host)
        check = HostChecks.objects.get(name=check)
        if host.enabled is True and check.enabled is True:
            run = sh.Command("./bin/runthis.sh")
            res = str(run(check.arg))
            computebool(check, host, res)
            print(oid + ' on ' + address + ' equals ' + res)
    except Exception as e:
        print('doing ' + check.name + ' on ' + host.name + ' failed')
        # update the error count
        setMetadata(host.name + ':' + check.name + '::lasterror', str(timezone.now()))
        setMetadata(host.name + ':' + check.name + '::nberror',
                    int(getMetadata(host.name + ':' + check.name + '::nberror', 0)) + 1)
        # Log the error to the database.
        ErrorLog(hostcheck=check, host=host, event=e.__class__.__name__, error=str(e), value=res).save()
    return res


@shared_task(bind=True, name='execstr')
def execstr(self, host, check):
    res = None
    try:
        print('doing ' + check + ' on ' + host)
        host = Hosts.objects.get(name=host)
        check = HostChecks.objects.get(name=check)
        if host.enabled is True and check.enabled is True:
            run = sh.Command("./bin/runthis.sh")
            res = str(run(check.arg))
            computestr(check, host, res)
            print(oid + ' on ' + address + ' equals ' + res)
    except Exception as e:
        print('doing ' + check.name + ' on ' + host.name + ' failed')
        # update the error count
        setMetadata(host.name + ':' + check.name + '::lasterror', str(timezone.now()))
        setMetadata(host.name + ':' + check.name + '::nberror',
                    int(getMetadata(host.name + ':' + check.name + '::nberror', 0)) + 1)
        # Log the error to the database.
        ErrorLog(hostcheck=check, host=host, event=e.__class__.__name__, error=str(e), value=res).save()
    return res


# noinspection PyBroadException
@shared_task(bind=True, name='exportInfluxDB')
def exportInfluxDB(self, count):
    print("Starting with exportInfluxDB")
    from django.db import transaction
    from influxdb import InfluxDBClient
    from django.conf import settings
    from .models import Historical

    user = 'username'
    password = '48Sh4bSh!94b'
    dbname = 'm4'
    port = '8086'
    host = settings.INFLUXDB_HOST
    client = InfluxDBClient(host, port, user, password, dbname)

    # do batches of 1000 rows to start
    try:
        with transaction.atomic():
            logs = Historical.objects.select_for_update().filter(exported=False).order_by('pk')[:int(count)]
            for log in logs:
                # keep entries than are less than 1h old
                if log.hostcheck.checktype == 'snmpgetint' or log.hostcheck.checktype == 'execint':
                    value = float(log.value)
                else:
                    value = log.value
                json_body = [{}]
                json_body[0]['measurement'] = log.hostcheck.name
                json_body[0]['tags'] = {}
                json_body[0]['tags']['host'] = log.host.name
                json_body[0]['tags']['address'] = log.host.address
                json_body[0]['tags']['community'] = log.host.community
                json_body[0]['tags']['hostnote'] = log.host.note
                json_body[0]['tags']['type'] = log.hostcheck.checktype
                json_body[0]['tags']['interval'] = log.hostcheck.interval
                json_body[0]['tags']['unit'] = log.hostcheck.unit
                json_body[0]['tags']['quotient'] = log.hostcheck.quotient
                json_body[0]['tags']['checknote'] = log.hostcheck.note
                json_body[0]['tags']['verbosename'] = log.hostcheck.verbosename
                json_body[0]['time'] = log.timestamp
                json_body[0]['fields'] = {}
                json_body[0]['fields']['value'] = value

                try:
                    # we should be writing to 2 servers to ensure high availibility
                    client.write_points(json_body, batch_size=5000)

                    # json_body = {'measurement': log.hostcheck.name, 'host': log.host.name, 'address': log.host.address,
                    #              'type': log.hostcheck.checktype, 'unit': log.hostcheck.unit,
                    #              'checknote': log.hostcheck.note, 'verbosename': log.hostcheck.verbosename,
                    #              'time': log.timestamp.strftime("%m/%d/%Y, %H:%M:%S"), 'value': value}
                    # producer.send('m4-measurements', json.dumps(json_body).encode())
                    # producer.flush()

                except Exception as e:
                    print('doing exportInfluxDB failed' + str(e.message))
                    # Log the error to the database.
                else:
                    # I think we should write to a file before deletion
                    log.exported = True
                    log.save()

    except Exception as e:
        print(traceback.format_exc())
        print('Was an error in the transaction in doing influxdb')
    print("Done with exportInfluxDB")
    # producer.close()
    return True


@shared_task(bind=True, name='exportInfluxDBnew')
def exportInfluxDBnew(self, count=1000):
    print("Starting with exportInfluxDBnew")
    from django.db import transaction
    from influxdb import InfluxDBClient
    from django.conf import settings
    from .models import Historical

    user = ''
    password = ''
    dbname = 'm4'
    port = '8086'
    host = settings.INFLUXDB_HOST
    client = InfluxDBClient(host, port, user, password, dbname)
    # producer = KafkaProducer(bootstrap_servers='172.31.238.221:9092',acks=0)

    # do batches of 1000 rows to start
    # noinspection PyBroadException
    try:
        with transaction.atomic():
            logs = Historical.objects.select_for_update().filter(exported=False).order_by('-pk')[:count]
            for log in logs:
                # keep entries than are less than 1h old
                if log.hostcheck.checktype == 'snmpgetint' or log.hostcheck.checktype == 'execint':
                    value = float(log.value)
                else:
                    value = log.value
                json_body = [{}]
                json_body[0]['measurement'] = log.hostcheck.name
                json_body[0]['tags'] = {}
                json_body[0]['tags']['host'] = log.host.name
                json_body[0]['tags']['address'] = log.host.address
                json_body[0]['tags']['community'] = log.host.community
                json_body[0]['tags']['hostnote'] = log.host.note
                json_body[0]['tags']['type'] = log.hostcheck.checktype
                json_body[0]['tags']['interval'] = log.hostcheck.interval
                json_body[0]['tags']['unit'] = log.hostcheck.unit
                json_body[0]['tags']['quotient'] = log.hostcheck.quotient
                json_body[0]['tags']['checknote'] = log.hostcheck.note
                json_body[0]['tags']['verbosename'] = log.hostcheck.verbosename
                json_body[0]['time'] = log.timestamp
                json_body[0]['fields'] = {}
                json_body[0]['fields']['value'] = value

                try:
                    # we should be writing to 2 servers to ensure high availibility
                    client.write_points(json_body, batch_size=5000)

                    # json_body = {'measurement': log.hostcheck.name, 'host': log.host.name, 'address': log.host.address,
                    #              'type': log.hostcheck.checktype, 'unit': log.hostcheck.unit,
                    #              'checknote': log.hostcheck.note, 'verbosename': log.hostcheck.verbosename,
                    #              'time': log.timestamp.strftime("%m/%d/%Y, %H:%M:%S"), 'value': value}
                    # producer.send('m4-measurements', json.dumps(json_body).encode())
                    # producer.flush()

                except Exception as e:
                    print('doing exportInfluxDB failed' + str(e.message))
                    # Log the error to the database.
                else:
                    # I think we should write to a file before deletion
                    log.exported = True
                    log.save()

    except:
        print('Was an error in the transaction in doing influxdb')
    print("Done with exportInfluxDBnew")
    # producer.close()
    return True


@shared_task(bind=True, name='pruneFromDB')
def pruneFromDB(self):
    print("Starting with pruneFromDB")
    from django.db import transaction
    from .models import Historical
    import datetime
    try:
        with transaction.atomic():
            now = timezone.now()
            onehourago = now - datetime.timedelta(hours=1)
            logs = Historical.objects.select_for_update().filter(exported=True, timestamp__lt=onehourago).order_by('pk')
            logs.delete()
    except:
        print('Was an error in the transaction in doing pruneFromDB')
    print("Done with pruneFromDB")
    return True


# This should get the email from  from settings.py
@shared_task(bind=True, name='Heartbeat')
def Heartbeat(self):
    from django.core.mail import send_mass_mail
    print("Starting with Heartbeat")
    emails = [('[M4] Heartbeat', 'This email confirms YUL62 BMS is online and operational.',
               'm4@m4system.com', ['m4@m4system.com'])]
    send_mass_mail(tuple(emails), fail_silently=False)
    print("Done sending Heartbeat email")

# @shared_task(bind=True, name='ExportKafka')
# def exportKafka(count = 100):
#     print("Starting with exportKafka")
#     from .models import Historical
#     from kafka import KafkaProducer
#     import json
#
#     producer = KafkaProducer(bootstrap_servers='127.0.0.1:9092')
#     # do batches of 1000 rows to start
#     # try:
#     # with transaction.atomic():
#     logs = Historical.objects.filter(exportedk=False).order_by('pk')[:count]
#     for log in logs:
#         # keep entries than are less than 1h old
#         if log.hostcheck.checktype == 'snmpgetint' or log.hostcheck.checktype == 'execint':
#             value = float(log.value)
#         else:
#             value = log.value
#         json_body = {}
#         json_body['measurement'] = log.hostcheck.name
#         json_body['host'] = log.host.name
#         json_body['address'] = log.host.address
#         json_body['type'] = log.hostcheck.checktype
#         json_body['unit'] = log.hostcheck.unit
#         json_body['checknote'] = log.hostcheck.note
#         json_body['verbosename'] = log.hostcheck.verbosename
#         json_body['time'] = log.timestamp.strftime("%m/%d/%Y, %H:%M:%S")
#         json_body['value'] = value
#
#
#         try:
#             # we should be writing to 2 servers to ensure high availibility
#             producer.send('measurements', json.dumps(json_body).encode())
#         except Exception as e:
#             print('doing exportKafka failed' + str(e.message))
#             # Log the error to the database.
#         else:
#             # I think we should write to a file before deletion
#             log.exportedk = True
#             log.save()
#             producer.flush()
#     producer.close()
#     # except:
#     #     print('Was an error in the transaction in doing kafka')
#     print("Done with exportKafka")
#
#     return True
