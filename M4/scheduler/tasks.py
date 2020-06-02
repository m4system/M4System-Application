from __future__ import absolute_import

import traceback
from time import time

from celery import shared_task
from django.utils import timezone
from pyasn1.codec.ber import encoder, decoder
from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.carrier.asyncore.dispatch import AsyncoreDispatcher
from pysnmp.proto import api

# import sh
from M4.System.tools import setMetadata, getMetadata
from .models import Hosts, HostChecks, ErrorLog
from .utils import computeint, computebool, computestr

# Easysnmp is not supported on windows unfortunally
# from easysnmp import snmp_get
# from pysnmp.hlapi import getCmd as snmp_get

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
            # res = str(float(snmp_get(oid, hostname=address, community=community, version=1).value) * float(check.quotient))
            # from pysnmp import debug
            # debug.setLogger(debug.Debug('msgproc'))

            # Protocol version to use
            pMod = api.protoModules[api.protoVersion1]
            # pMod = api.protoModules[api.protoVersion2c]

            # Build PDU
            reqPDU = pMod.GetRequestPDU()
            pMod.apiPDU.setDefaults(reqPDU)
            pMod.apiPDU.setVarBinds(reqPDU, (((oid), pMod.Null()),))

            # Build message
            reqMsg = pMod.Message()
            pMod.apiMessage.setDefaults(reqMsg)
            pMod.apiMessage.setCommunity(reqMsg, community)
            pMod.apiMessage.setPDU(reqMsg, reqPDU)

            startedAt = time()

            def cbTimerFun(timeNow):
                if timeNow - startedAt > 3:
                    raise Exception("Request timed out")

            # noinspection PyUnusedLocal,PyUnusedLocal
            def cbRecvFun(transportDispatcher, transportDomain, transportAddress,
                          wholeMsg, reqPDU=reqPDU):
                while wholeMsg:
                    rspMsg, wholeMsg = decoder.decode(wholeMsg, asn1Spec=pMod.Message())
                    rspPDU = pMod.apiMessage.getPDU(rspMsg)
                    # Match response to request
                    if pMod.apiPDU.getRequestID(reqPDU) == pMod.apiPDU.getRequestID(rspPDU):
                        # Check for SNMP errors reported
                        errorStatus = pMod.apiPDU.getErrorStatus(rspPDU)
                        if errorStatus:
                            print(errorStatus.prettyPrint())
                        else:
                            for oid, val in pMod.apiPDU.getVarBinds(rspPDU):
                                # print('%s = %s' % (oid.prettyPrint(), val.prettyPrint()))
                                # res = str(float(val.prettyPrint() * float(check.quotient)))
                                global checkname
                                global hostname
                                global res
                                res = str(float(val * float(checkname.quotient)))
                                computeint(checkname, hostname, res)
                        transportDispatcher.jobFinished(1)
                return wholeMsg

            transportDispatcher = AsyncoreDispatcher()

            transportDispatcher.registerRecvCbFun(cbRecvFun)
            # transportDispatcher.registerTimerCbFun(cbTimerFun)

            # UDP/IPv4
            transportDispatcher.registerTransport(
                udp.domainName, udp.UdpSocketTransport().openClientMode()
            )

            # Pass message to dispatcher
            transportDispatcher.sendMessage(
                encoder.encode(reqMsg), udp.domainName, (address, 161)
            )
            transportDispatcher.jobStarted(1)

            ## UDP/IPv6 (second copy of the same PDU will be sent)
            # transportDispatcher.registerTransport(
            #    udp6.domainName, udp6.Udp6SocketTransport().openClientMode()
            # )

            # Pass message to dispatcher
            # transportDispatcher.sendMessage(
            #    encoder.encode(reqMsg), udp6.domainName, ('::1', 161)
            # )
            # transportDispatcher.jobStarted(1)

            ## Local domain socket
            # transportDispatcher.registerTransport(
            #    unix.domainName, unix.UnixSocketTransport().openClientMode()
            # )
            #
            # Pass message to dispatcher
            # transportDispatcher.sendMessage(
            #    encoder.encode(reqMsg), unix.domainName, '/tmp/snmp-agent'
            # )
            # transportDispatcher.jobStarted(1)

            # Dispatcher will finish as job#1 counter reaches zero
            transportDispatcher.runDispatcher()

            transportDispatcher.closeDispatcher()
            # print(transportDispatcher)
            del transportDispatcher
            del pMod
            del reqPDU
            del reqMsg
            del startedAt
            del cbTimerFun
            del cbRecvFun

            # computeint(check, host, res)
            # print(oid + ' on ' + address + ' equals ' + res)
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
            # res = str(snmp_get(oid, hostname=address, community=community, version=1).value)
            computestr(check, host, res)
        # print(oid + ' on ' + address + ' equals ' + res)
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
            # res = str(snmp_get(oid, hostname=address, community=community, version=1).value)
            computebool(check, host, res)
        # print(oid + ' on ' + address + ' equals ' + res)
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
            # run = sh.Command("./bin/runthis.sh")
            # res = str(float(run(check.arg)) * float(check.quotient))
            computeint(check, host, res)
            # print(oid + ' on ' + address + ' equals ' + res)
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
            # run = sh.Command("./bin/runthis.sh")
            # res = str(run(check.arg))
            computebool(check, host, res)
            # print(oid + ' on ' + address + ' equals ' + res)
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
            # run = sh.Command("./bin/runthis.sh")
            # res = str(run(check.arg))
            computestr(check, host, res)
            # print(oid + ' on ' + address + ' equals ' + res)
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
def exportInfluxDB(count=100):
    print("Starting with exportInfluxDB")
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
    try:
        with transaction.atomic():
            logs = Historical.objects.select_for_update().filter(exported=False).order_by('pk')[:count]
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
    print("Done with exportInfluxDB")
    # producer.close()
    return True


@shared_task(bind=True, name='exportInfluxDBnew')
def exportInfluxDBnew(count=1000):
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
def pruneFromDB():
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
def Heartbeat():
    from django.core.mail import send_mass_mail
    print("Starting with Heartbeat")
    emails = [('[YUL62-BMS] Heartbeat', 'This email confirms YUL62 BMS is online and operational.',
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
