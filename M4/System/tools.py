import inspect
import logging

logger = logging.getLogger('M4')
del logging  # To prevent accidentally using it
import json
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import Group
from django.core.cache import cache


def error(msg):
    logger.error(str(inspect.stack()[1][3]) + ' in ' + str(inspect.stack()[1][1]) + ': ' + msg)


def dbg(msg):
    logger.debug(str(inspect.stack()[1][3]) + ' in ' + str(inspect.stack()[1][1]) + ': ' + str(msg))


def info(msg):
    logger.info(str(inspect.stack()[1][3]) + ' in ' + str(inspect.stack()[1][1]) + ': ' + msg)


def die(msg):
    logger.exception(str(inspect.stack()[1][3]) + ' in ' + str(inspect.stack()[1][1]) + ': ' + msg)


# Phasing out
def savemd(md):
    # dbg('savemd called')
    return json.dumps(md)


# Phasing out
def loadmd(md):
    # dbg('loadmd called')
    return json.loads(md)


# get a value with an optional default value from the cached key-value store
def getMetadata(key, default=None):
    # local import to avoid import loop
    from M4.scheduler.models import Metadata
    fromcache = cache.get(key, None)
    if fromcache is not None:
        return fromcache
    else:
        try:
            md = Metadata.objects.get(key=key).data
        except Exception as e:
            dbg(e)
            dbg("get - Did not find object for key " + key + ' , will initialize with ' + str(default))
            md = default
            Metadata(key=key, data=md).save()
        # Prime the cache with the value
        cache.set(key, md)
        # dbg('got key ' + key + ' as ' + str(md))
        return md


# set a value on the cached key-value store
def setMetadata(key, data):
    # local import to avoid import loop
    from M4.scheduler.models import Metadata
    # Prime the cache with the new value right away to avoid stale data
    cache.set(key, data)
    # Try to get the current key, create it instead on any error.
    try:
        md = Metadata.objects.get(key=key)
    except Exception as e:
        dbg(e)
        dbg('set - Did not find object for key ' + key + ' , initialize new key ')
        md = Metadata(key=key)
    md.data = data
    md.save()
    # dbg('set key ' + key + ' as ' + str(md.data))
    return md.data


# Phasing out
def setmd(md, key, value):
    # dbg('setmd called')
    data = loadmd(md)
    data[key] = value
    return savemd(data)


# Phasing out
def getmd(md, key, default=0):
    # dbg('getmd called')
    data = loadmd(md)
    return data.get(key, default)


# Add messages in the UI
def debug_msg(request, msg):
    messages.debug(request, str(msg), extra_tags=timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M:%S %Z'))
    return True


def error_msg(request, msg):
    messages.error(request, str(msg), extra_tags=timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M:%S %Z'))
    return True


def info_msg(request, msg):
    messages.info(request, str(msg), extra_tags=timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M:%S %Z'))
    return True


def warning_msg(request, msg):
    messages.warning(request, str(msg), extra_tags=timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M:%S %Z'))
    return True


# Add a msg with a custom level
def msg(request, level, msg):
    messages.add_message(request, level, str(msg),
                         extra_tags=timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M:%S %Z'))
    return True


# Add a notification to be displayed in the UI.
# It will be displayed to the groups provided.
# To add a sticky message, do it from the admin UI
def add_msg(level, msg, groups):
    from M4.DashboardDisplayPlugin.webview_models import UIMsg
    mymsg = UIMsg(level=level, msg=str(msg))
    mymsg.save()
    for group in groups:
        if isinstance(group, Group):
            mymsg.group.add(group)
        elif isinstance(group, int):
            mymsg.group.add(Group.objects.get(pk=group))
    mymsg.save()
    return True


def dump(obj):
    """return a printable representation of an object for debugging"""
    newobj = obj
    if '__dict__' in dir(obj):
        newobj = obj.__dict__
        if ' object at ' in str(obj) and not newobj.has_key('__type__'):
            newobj['__type__'] = str(obj)
        for attr in newobj:
            newobj[attr] = dump(newobj[attr])
    return newobj
