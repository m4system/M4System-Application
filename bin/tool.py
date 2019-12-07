#!/usr/bin/python3
# Quickly add breakers
# To use:
# manage shell_plus
# from bin.tool import branch
# branch()  

def branch():
    # Shell Plus Model Imports
    from django.contrib.admin.models import LogEntry
    from django.contrib.auth.models import Group, Permission, User
    from django.contrib.contenttypes.models import ContentType
    from django.contrib.sessions.models import Session
    from djcelery.models import CrontabSchedule, IntervalSchedule, PeriodicTask, PeriodicTasks, TaskMeta, TaskSetMeta, TaskState, WorkerState
    from jet.dashboard.models import UserDashboardModule
    from jet.models import Bookmark, PinnedApplication
    from reversion.models import Revision, Version
    from scheduler.models import ErrorLog, EventLog, Historical, HostChecks, Hosts, Metadata, Sla, SlaLog, Template, Thresholds, Trap
    from webview.models import UIMsg, UserProfile, UserView, Widgets
    # Shell Plus Django Imports
    from django.db import transaction
    from django.core.cache import cache
    from django.core.urlresolvers import reverse
    from django.conf import settings
    from django.db.models import Avg, Count, F, Max, Min, Sum, Q, Prefetch, Case, When
    from django.utils import timezone

    fpcName = "fpc"
    hostname = "fpc"
    fpc = Hosts.objects.get(name=hostname)
    view = UserView.objects.get(name='Breakers')
    breaker30a = Thresholds.objects.get(name='24Amp')
    breaker20a = Thresholds.objects.get(name='16Amp')
    breaker15a = Thresholds.objects.get(name='12Amp')
    branchName = input('Branch Name ? ')
    startPos = input('Start Position ? ')
    numPole = input('Amount of pole ? ')
    branchRating = input('Breaker Rating ? ')
    

    if branchRating == "30":
        thold = breaker30a
    if branchRating == "20":
        thold = breaker20a
    if branchRating == "15":
        thold = breaker15a

    if numPole == "1" or numPole == "2" or numPole == "3":
        c=HostChecks(name=fpcName+"Branch"+startPos+"CurrentPhaseA", verbosename=branchName+" Current Phase A", unit='A AC', arg="iso.3.6.1.4.1.476.1.42.3.9.20.1.20.1.2.1.5219.1."+startPos, note='Breaker #'+startPos)
        c.save()
        c.hosts=[fpc]
        c.threshold=[thold]
        c.save()
        view.widgets.add(Widgets.objects.get(name=hostname+'-'+fpcName+"Branch"+startPos+"CurrentPhaseA"))
        view.save()
    if numPole == "2" or numPole == "3":
        c=HostChecks(name=fpcName+"Branch"+startPos+"CurrentPhaseB", verbosename=branchName+" Current Phase B", unit='A AC', arg="iso.3.6.1.4.1.476.1.42.3.9.20.1.20.1.2.1.5220.1."+startPos, note='Breaker #'+startPos)
        c.save()
        c.hosts=[fpc]
        c.threshold=[thold]
        c.save()
        view.widgets.add(Widgets.objects.get(name=hostname+'-'+fpcName+"Branch"+startPos+"CurrentPhaseB"))
        view.save()
    if numPole == "3":
        c=HostChecks(name=fpcName+"Branch"+startPos+"CurrentPhaseC", verbosename=branchName+" Current Phase C", unit='A AC', arg="iso.3.6.1.4.1.476.1.42.3.9.20.1.20.1.2.1.5221.1."+startPos, note='Breaker #'+startPos)
        c.save()
        c.hosts=[fpc]
        c.threshold=[thold]
        c.save()
        view.widgets.add(Widgets.objects.get(name=hostname+'-'+fpcName+"Branch"+startPos+"CurrentPhaseC"))
        view.save()

    c=HostChecks(name=fpcName+"Branch"+startPos+"OutputPower", verbosename=branchName+" Output Power", unit='kW', arg="iso.3.6.1.4.1.476.1.42.3.9.20.1.20.1.2.1.5222.1."+startPos, note='Breaker #'+startPos)
    c.save()
    c.hosts=[fpc]
    c.save()
    view.widgets.add(Widgets.objects.get(name=hostname+'-'+fpcName+"Branch"+startPos+"OutputPower"))
    view.save()

    c=HostChecks(name=fpcName+"Branch"+startPos+"PowerFactor", verbosename=branchName+" Power Factor", unit='pf', arg="iso.3.6.1.4.1.476.1.42.3.9.20.1.20.1.2.1.5224.1."+startPos, note='Breaker #'+startPos)
    c.save()
    c.hosts=[fpc]
    c.save()
    view.widgets.add(Widgets.objects.get(name=hostname+'-'+fpcName+"Branch"+startPos+"PowerFactor"))
    view.save()

    c=HostChecks(name=fpcName+"Branch"+startPos+"OutputLoad", verbosename=branchName+" Output Load", unit='%', arg="iso.3.6.1.4.1.476.1.42.3.9.20.1.20.1.2.1.5225.1."+startPos, note='Breaker #'+startPos)
    c.save()
    c.hosts=[fpc]
    c.save()
    view.widgets.add(Widgets.objects.get(name=hostname+'-'+fpcName+"Branch"+startPos+"OutputLoad"))
    view.save()

    return True
