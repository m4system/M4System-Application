from django.http import HttpResponse, JsonResponse
from django.views.decorators.cache import never_cache, cache_page
from tools import dbg, msg, getMetadata, setMetadata
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.views.decorators.vary import vary_on_cookie
from django.views.decorators.cache import cache_control
from django.contrib import messages
import datetime
import time
from webview.models import UserProfile, Widgets, UserView, UIMsg
from webview.forms import SettingsForm
import json
from django.core.cache import cache
from scheduler.models import Hosts, HostChecks, Historical, EventLog, Sla, SlaLog, Trap
from django.shortcuts import render_to_response
from django.db.models import Q
from django.utils import timezone
from djcelery.models import TaskState
from statistics import mean
from django.views.decorators.csrf import csrf_exempt


@login_required
@never_cache
def index(request, view):
    """
    Display the main page.

    **Context**

    ``Widgets``
        List of widgets for the user's view

    **Template:**

    Loaded from the DB

    :template:`webview/index.html`
    """
    data = []
    view = view[5:]
    # Get the list of hosts so that we can loop through them and create the rows
    if view == '':
        # load hosts from the default view
        hosts = sorted(set(UserView.objects.filter(group__name__in=request.user.groups.all().values_list('name',flat=True), default=True)[0].widgets.filter(active=True, host__enabled=True).values_list('host__name', flat=True).order_by('-name')), reverse=True)
    else:
        # load hosts from the view specified in the url
        hosts = sorted(set(UserView.objects.get(name=view).widgets.filter(active=True, host__enabled=True).values_list('host__name', flat=True).order_by('-name')), reverse=True)
    for host in hosts:
        # For each host, we will get generate the widgets in it's row
        thishost = {}
        wdgts = []
        if view == '':
            # load this host's widgets from the default userview
            uv = UserView.objects.filter(group__name__in=request.user.groups.all().values_list('name',flat=True), default=True)[0].widgets.filter(host__name=host, active=True)
        else:
            # load this host's widgets from the view specified in the url
            uv = UserView.objects.get(name=view).widgets.filter(host__name=host, active=True)
        for widget in uv:
            thisdata = {}
            thisdata['name'] = widget.name
            thisdata['note'] = widget.note
            thisdata['data'] = widget.renderWidget(user=request.user)
            wdgts.append(thisdata)
        thishost['widgets'] = wdgts
        thishost['name'] = host
        thishost['note'] = Hosts.objects.get(name=host).note
        data.append(thishost)       
    # Preloads the sla widget with any SLAs relating to the user's group.
    sla = None
    if request.user.has_perm('webview.view_sla'):
        sla = Sla.objects.filter(Q(enabled=True, warngroups__name__in=request.user.groups.all().values_list('name',flat=True)) | Q(enabled=True, okgroups__name__in=request.user.groups.all().values_list('name',flat=True)) | Q(enabled=True, critgroups__name__in=request.user.groups.all().values_list('name',flat=True))).distinct()
    if request.user.has_perm('webview.view_thresholdlog') or request.user.has_perm('webview.view_slalog'):
        slalist = sla.values_list('name',flat=True)
    eventlog = None
    if request.user.has_perm('webview.view_thresholdlog'):
        # Need to figure out if this is useful or not.  Currently, we log all threshold success, making this worthless
        eventlog = EventLog.objects.filter(sla__name__in=slalist).order_by('-timestamp')[:10]
    slalog = None
    if request.user.has_perm('webview.view_slalog'):
        # Preloads the slalog widget with any SLAs relating to the user's group.
        slalog = SlaLog.objects.filter(sla__name__in=slalist).order_by('-timestamp')[:10]
    trap = None
    if request.user.has_perm('webview.view_traps'):
        now = timezone.now()
        onehour = now - datetime.timedelta(hours=24)
        trap = Trap.objects.filter(timestamp__gt=onehour)
    # Load the list of available userviews for the logged in user
    uvlist = UserView.objects.filter(group__name__in=request.user.groups.all().values_list('name',flat=True))
    context = {'data': data, 'eventlog': eventlog, 'slas': sla, 'slalog': slalog, 'uvlist': uvlist, 'taskdelay': getMetadata('taskdelay-1'), 'trap': trap}
    # Load pending message for that user from the database and push them to the UI using the message framework.
    if request.user.has_perm('webview.view_notifs'):
        msgs = UIMsg.objects.filter(group__name__in=request.user.groups.all().values_list('name',flat=True)).exclude(user__username=request.user.username)[:100]
        for mymsg in msgs:
            msg(request, mymsg.level, mymsg.msg)
            if not mymsg.sticky:
                # by adding the user to the m2m field, this msg will get skipped at next collection. see above query
                mymsg.user.add(request.user)
                mymsg.save()
    return render(request, 'index.html', context)


@cache_control(private=True)
@vary_on_cookie
@login_required
def settings(request):
    """
    ajax view for the :model:`webview.UserProfile`.

    **Context**

    ``UserProfile``
        An instance of :model:`webview.UserProfile`.

    **Template:**

    :template:`webview/settings.html`
    """
    if request.method == 'POST':
        # load the settings form using django's form framework
        form = SettingsForm(request.POST)
        if form.is_valid():
            profile = UserProfile.objects.get(user=request.user)
            # load the validated data from the form and let the UI know we succeeded
            profile.notifemail = form.cleaned_data['notifemail']
            profile.notifcallback = form.cleaned_data['notifcallback']
            profile.save()
            # We push a success notification to the notification drop down on the top-left
            messages.success(request, 'settings saved - ' + json.dumps(form.cleaned_data), extra_tags=timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M:%S %Z'))
            return render(request, 'settings.html', {'form': form})
        else:
            # or we push a failure
            messages.error(request, 'Some field did not validate', extra_tags=timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M:%S %Z'))
            return render(request, 'settings.html', {'form': form}, status=400)
    else:
        # load the settings when showing the modal
        profile = get_object_or_404(UserProfile, user=request.user)
        prefs = {'notifemail': profile.notifemail, 'notifcallback': profile.notifcallback}
        # initialize the form with the current values
        form = SettingsForm(prefs)
    return render(request, 'settings.html', {'form': form})


@never_cache
def test(request):
    """
    Display an individual :model:`webview.UserProfile`.

    **Context**

    ``mymodel``
        An instance of :model:`webview.UserProfile`.

    **Template:**

    :template:`webview/index.html`
    """
    # Write to the debug log
    dbg("testing debug with name and true")
    # from scheduler.tasks import snmpgetint
    # snmpgetint.delay("10.168.118.99", "public", "1.3.6.1.4.1.7777.1.2.1.3.0")
    return HttpResponse("<htm><head></head><body>Hello, world. ip: " + request.META['REMOTE_ADDR'] + "</body></html>")


@login_required
@cache_page(5)
@cache_control(private=True)
@vary_on_cookie
def getCheck(request, host, check, checktype):
    # updates the data in the widgets.
    # Bail out if we cant find the objects
    get_object_or_404(Hosts, name=host)
    get_object_or_404(HostChecks, name=check)
    # uv = UserView.objects.get(group__name__in=request.user.groups.all().values_list('name',flat=True), default=True).widgets.filter(host__name=host, hostcheck__name=check, active=True)
    uv = Widgets.objects.get(name=host+'-'+check).userview_set.filter(group__name__in=request.user.groups.all().values_list('name',flat=True))
    if len(uv) == 0:
        raise PermissionDenied
    # Grab all the data for that object from the cache
    data = {}
    data['data'] = getMetadata(host + ':' + check + '::value', 'No Data')
    data['alert'] = getMetadata(host + ':' + check + '::error', 'No Data')
    data['lastcheck'] = getMetadata(host + ':' + check + '::lastcheck', 'No Data')
    notifs = getMetadata(host + ':' + check + '::notifs', 'No Data')
    if notifs == 'False':
        data['notifs'] = 'false'
    else:
        data['notifs'] = 'true'
    if checktype == 'int':
        data['avg'] = getMetadata(host + ':' + check + '::avg', 'No Data')
        data['min'] = getMetadata(host + ':' + check + '::min', 'No Data')
        data['max'] = getMetadata(host + ':' + check + '::max', 'No Data')
    elif checktype == 'bool':
        data['nbtrue'] = getMetadata(host + ':' + check + '::nbtrue', '0')
        data['nbfalse'] = getMetadata(host + ':' + check + '::nbfalse', '0')
        data['lastfalse'] = getMetadata(host + ':' + check + '::lastfalse', 'No Data')
        data['lasttrue'] = getMetadata(host + ':' + check + '::lasttrue', 'No Data')
    return JsonResponse(data, safe=False)


@never_cache
@login_required
def getGraphData(request, host, check, qty):
    uv = UserView.objects.filter(group__name__in=request.user.groups.all().values_list('name',flat=True), default=True)[0].widgets.filter(host__name=host, hostcheck__name=check, active=True)
    if len(uv) == 0:
        raise PermissionDenied
    if qty is None:
        # set to 30 minutes of 30s checks by default
        qty = "60"
    host = get_object_or_404(Hosts, name=host)
    check = get_object_or_404(HostChecks, name=check)
    # grab the data used in the graph
    bootstrapgraph = Historical.objects.values_list('value', 'timestamp', 'data').filter(host=host, hostcheck=check).order_by('-timestamp')[:int(qty)]
    # dbg(bootstrapgraph)
    data = []
    # Format it to be used by the front end
    for value, timestamp, mddata in bootstrapgraph:
        if mddata != '{}':
            metadata = json.loads(mddata)
            if check.checktype == 'snmpgetint' or check.checktype == 'execint':
                data.append({'datetime': timestamp.strftime("%m/%d/%Y %H:%M:%S %z"), 'value': value, 'avg': metadata['avg'], 'max': metadata['max'], 'min': metadata['min']})
            elif check.checktype == 'snmpgetbool':
                data.append({'datetime': timestamp.strftime("%m/%d/%Y %H:%M:%S %z"), 'value': value, 'nbtrue': metadata['nbtrue'], 'nbfalse': metadata['nbfalse'], 'lasttrue': metadata['lasttrue'], 'lastfalse': metadata['lastfalse']})
    return JsonResponse(data, safe=False)


@cache_control(private=True)
@vary_on_cookie
@login_required
def getWidget(request, host, check, name):
    get_object_or_404(Hosts, name=host)
    get_object_or_404(HostChecks, name=check)
    uv = UserView.objects.filter(group__name__in=request.user.groups.all().values_list('name',flat=True), default=True)[0].widgets.filter(host__name=host, hostcheck__name=check, active=True)
    if len(uv) == 0:
        raise PermissionDenied
    # Get a widget to display in the UI and render it with the internal function.  Used for graphs and info modals.
    widget = get_object_or_404(Widgets, name=host + '-' + check + '-' + name)
    return HttpResponse(widget.renderWidget(user=request.user))


@cache_control(private=True)
@vary_on_cookie
@login_required
def getEvents(request, qty):
    # not used anymore.  was used for the eventlog 
    if not request.user.has_perm('webview.view_thresholdlog'):
        raise PermissionDenied
    if qty is None:
        qty = "10"
    sla = Sla.objects.filter(Q(enabled=True, warngroups__name__in=request.user.groups.all().values_list('name',flat=True)) | Q(enabled=True, critgroups__name__in=request.user.groups.all().values_list('name',flat=True)) | Q(enabled=True, okgroups__name__in=request.user.groups.all().values_list('name',flat=True))).distinct()
    slalist = sla.values_list('name',flat=True)
    eventlog = EventLog.objects.filter(sla__name__in=slalist).order_by('-timestamp')[:int(qty)]
    return render_to_response('widgets/eventlog.html', {'eventlog': eventlog})


@cache_control(private=True)
@vary_on_cookie
@login_required
def getSla(request):
    if not request.user.has_perm('webview.view_sla'):
        raise PermissionDenied
    # display SLAs in the UI based on which group you belong to.
    sla = Sla.objects.filter(Q(enabled=True, warngroups__name__in=request.user.groups.all().values_list('name',flat=True)) | Q(enabled=True, critgroups__name__in=request.user.groups.all().values_list('name',flat=True)) | Q(enabled=True, okgroups__name__in=request.user.groups.all().values_list('name',flat=True))).distinct()
    return render_to_response('widgets/sla.html', {'slas': sla})


@cache_control(private=True)
@vary_on_cookie
@login_required
def getSlaLog(request, qty):
    if not request.user.has_perm('webview.view_slalog'):
        raise PermissionDenied
    # display SLA Logs in the UI based on which group you belong to.
    if qty is None:
        qty = "10"
    sla = Sla.objects.filter(Q(enabled=True, warngroups__name__in=request.user.groups.all().values_list('name',flat=True)) | Q(enabled=True, critgroups__name__in=request.user.groups.all().values_list('name',flat=True)) | Q(enabled=True, okgroups__name__in=request.user.groups.all().values_list('name',flat=True))).distinct()
    slalist = sla.values_list('name',flat=True)
    slalog = SlaLog.objects.filter(sla__name__in=slalist).order_by('-timestamp')[:int(qty)]
    return render_to_response('widgets/slalog.html', {'slalog': slalog})


@cache_control(private=True)
@vary_on_cookie
@login_required
def getTraps(request):
    if not request.user.has_perm('webview.view_traps'):
        raise PermissionDenied
    # display SLA Logs in the UI based on which group you belong to.
    now = timezone.now()
    onehour = now - datetime.timedelta(hours=24)
    trap = Trap.objects.filter(timestamp__gt=onehour)
    return render_to_response('widgets/trap.html', {'trap': trap})



@cache_control(private=True)
@vary_on_cookie
@login_required
def getMsg(request):
    if not request.user.has_perm('webview.view_notifs'):
        raise PermissionDenied
    # Used by the notification refresh button.  gets a list of pending notifications and writes them of as read if not sticky.
    msgs = UIMsg.objects.filter(group__name__in=request.user.groups.all().values_list('name',flat=True)).exclude(user__username=request.user.username)
    for mymsg in msgs:
        msg(request, mymsg.level, mymsg.msg)
        if not mymsg.sticky:
            mymsg.user.add(request.user)
            mymsg.save()
    return render(request, 'widgets/msg.html')


@cache_control(private=True)
@vary_on_cookie
@login_required
def reports(request, host, check):
    # Download CSV button on widgets.
    host = get_object_or_404(Hosts, name=host)
    check = get_object_or_404(HostChecks, name=check)
    logs = Historical.objects.filter(host=host, hostcheck=check)
    import csv
    from django.utils.encoding import smart_str
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=report-' + host.name + '-' + check.name + '.csv'
    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8')) # BOM (optional...Excel needs it to open UTF-8 file properly)
    writer.writerow([
        smart_str(u"id"),
        smart_str(u"timestamp"),
        smart_str(u"value"),
    ])
    for obj in logs:
        writer.writerow([
            smart_str(obj.pk),
            smart_str(obj.timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')),
            smart_str(obj.value),
        ])
    return response


@cache_page(600)
@login_required
def getDelay(request, days):
    # Pulls the info for the avg task delay info bubble at the top )
    if days is None:
        days = 1
    # meandelay = getMetadata('taskdelay-' + str(days), None)
    # if meandelay is None:
    tasks = TaskState.objects.filter(tstamp__range=[timezone.now()-datetime.timedelta(days=int(days)), timezone.now()]).exclude(runtime=None).values_list('runtime', flat=True)
    meandelay = mean(tasks)
    setMetadata('taskdelay-' + str(days), meandelay)
    return HttpResponse(meandelay)


@never_cache
@login_required
def setNotifs(request, host, check, status):
    if not request.user.has_perm('webview.silence_check'):
        raise PermissionDenied
    # toggle notification status per host-check combo.  uses switchery in the UI.
    host = get_object_or_404(Hosts, name=host)
    check = get_object_or_404(HostChecks, name=check)
    if status == "false":
        status = False
    else:
        status = True
    setMetadata(host.name + ":" + check.name + "::notifs", status)
    return HttpResponse("done")
