import json

from django.utils import timezone

# from django.db.models import Avg
from tools import setMetadata, getMetadata


def computeint(check, host, value):
    # we process the value we get from the check
    from .models import Historical
    # create the db record
    history = Historical(host=host, hostcheck=check, value=value, timestamp=timezone.now())
    setMetadata(host.name + ':' + check.name + '::lastvalue',
                getMetadata(host.name + ':' + check.name + '::value', 'No Data'))
    now = int(timezone.now().timestamp())
    setMetadata(host.name + ':' + check.name + '::lastcheck', now)
    setMetadata(host.name + ':' + check.name + '::value', value)
    metadata = {'min': getMetadata(host.name + ':' + check.name + '::min', 'No Data'),
                'max': getMetadata(host.name + ':' + check.name + '::max', 'No Data'),
                'avg': getMetadata(host.name + ':' + check.name + '::avg', 'No Data'),
                'error': getMetadata(host.name + ':' + check.name + '::error', 'OK')}

    # disable avg calculation for now.  will do it out of band to avoid running late of checks
    # if (now - metadata.get('laststats', 0)) > check.statsinterval:
    #     try:
    #         castedata = []
    #         # This is the query that is loading the database, need to think about this.
    #         data = Historical.objects.filter(host=host, hostcheck=check).values_list('value')
    #         for i in data:
    #             castedata.append(float(i[0]))
    #         metadata['avg'] = mean(castedata)
    #     except:
    #         dbg('Could not compute avg of int')
    #         metadata['avg'] = 0
    #     metadata['laststats'] = now
    #     setMetadata(host.name + ':' + check.name + ':avg', str(metadata['avg']))
    #     setMetadata(host.name + ':' + check.name + ':laststats', now)

    # Update min if we are under
    # print(metadata)
    mdmin = metadata['min']
    if mdmin == 'None' or float(value) < float(mdmin):
        metadata['min'] = setMetadata(host.name + ':' + check.name + '::min', str(value))
    # Update max if we are over
    mdmax = getMetadata(host.name + ':' + check.name + '::max', None)
    if mdmax == 'None' or float(value) > float(mdmax):
        metadata['max'] = setMetadata(host.name + ':' + check.name + '::max', str(value))
    # process any alerts that could arise
    errors = alertint(check, host, value)
    thiserror = 'false'
    metadata['error'] = 'false'
    if check.colorizesla and len(errors) > 0:
        thiserror = 'ok'
        metadata['error'] = 'ok'
        # if colorizesla is true, we check if the sla is failing instead of the check
        slas = check.sla.filter(enabled=True)
        for sla in slas:
            if sla.status == 'failing':
                metadata['error'] = 'crit'
                thiserror = 'crit'
    else:
        for error in errors:
            if error.get('hasError', False):
                if error.get('lowcrit', False) or error.get('highcrit', False):
                    thiserror = 'crit'
                elif error.get('lowwarn', False) or error.get('highwarn', False):
                    thiserror = 'warn'
            elif error.get('hasError', None) is False:
                thiserror = 'ok'
    metadata['error'] = setMetadata(host.name + ':' + check.name + '::error', str(thiserror))
    # save a snapshot of the metadata when the check ran
    history.data = json.dumps(metadata)
    history.save()
    return metadata


def computestr(check, host, value):
    from .models import Historical
    # create the db record
    history = Historical(host=host, hostcheck=check, value=value, timestamp=timezone.now())
    setMetadata(host.name + ':' + check.name + '::lastvalue',
                getMetadata(host.name + ':' + check.name + '::value', 'No Data'))
    now = int(timezone.now().strftime('%s'))
    setMetadata(host.name + ':' + check.name + '::lastcheck', now)
    setMetadata(host.name + ':' + check.name + '::value', value)
    metadata = {'error': getMetadata(host.name + ':' + check.name + '::error', 'OK')}
    thiserror = 'false'
    metadata['error'] = 'false'
    errors = alertstr(check, host, value)
    if check.colorizesla and len(errors) > 0:
        thiserror = 'ok'
        metadata['error'] = 'ok'
        # dbg(check.name + ' is colorizesla')
        # if colorizesla is true, we check if the sla is failing instead of the check
        slas = check.sla.filter(enabled=True)
        for sla in slas:
            # dbg('checking sla ' + sla.name + '.  its status is ' + sla.status)
            if sla.status == 'failing':
                metadata['error'] = 'crit'
                thiserror = 'crit'
    else:
        for error in errors:
            if error.get('hasError', True):
                if error.get('strwarn', False):
                    thiserror = 'warn'
                if error.get('strgood', False) or error.get('strbad', False):
                    thiserror = 'crit'
            elif error.get('hasError', None) is False:
                thiserror = 'ok'
    metadata['error'] = setMetadata(host.name + ':' + check.name + '::error', thiserror)
    # save a snapshot of the metadata when the check ran
    history.data = json.dumps(metadata)
    history.save()
    return metadata


def computebool(check, host, value):
    value = booltoint(strtobool(value))
    # we process the value we get from the check
    from .models import Historical
    # create the db record
    history = Historical(host=host, hostcheck=check, value=value, timestamp=timezone.now())
    setMetadata(host.name + ':' + check.name + '::lastvalue',
                getMetadata(host.name + ':' + check.name + '::value', 'No Data'))
    now = int(timezone.now().strftime('%s'))
    setMetadata(host.name + ':' + check.name + '::lastcheck', now)
    setMetadata(host.name + ':' + check.name + '::value', value)
    metadata = {'nbtrue': getMetadata(host.name + ':' + check.name + '::nbtrue', '0'),
                'nbfalse': getMetadata(host.name + ':' + check.name + '::nbfalse', '0'),
                'lasttrue': getMetadata(host.name + ':' + check.name + '::lasttrue', 'No Data'),
                'lastfalse': getMetadata(host.name + ':' + check.name + '::lastfalse', 'No Data'),
                'error': getMetadata(host.name + ':' + check.name + '::error', 'OK')}
    # Update the metadata
    if value == 0:
        metadata['nbfalse'] = setMetadata(host.name + ':' + check.name + '::nbfalse', int(metadata['nbfalse']) + 1)
        metadata['lastfalse'] = setMetadata(host.name + ':' + check.name + '::lastfalse',
                                            timezone.now().strftime("%m/%d/%Y %H:%M:%S"))
    elif value == 1:
        metadata['nbtrue'] = setMetadata(host.name + ':' + check.name + '::nbtrue', int(metadata['nbtrue']) + 1)
        metadata['lasttrue'] = setMetadata(host.name + ':' + check.name + '::lasttrue',
                                           timezone.now().strftime("%m/%d/%Y %H:%M:%S"))
    thiserror = 'false'
    metadata['error'] = 'false'
    errors = alertbool(check, host, value)
    if check.colorizesla and len(errors) > 0:
        thiserror = 'ok'
        metadata['error'] = 'ok'
        # dbg(check.name + ' is colorizesla')
        # if colorizesla is true, we check if the sla is failing instead of the check
        slas = check.sla.filter(enabled=True)
        for sla in slas:
            # dbg('checking sla ' + sla.name + '.  its status is ' + sla.status)
            if sla.status == 'failing':
                metadata['error'] = 'crit'
                thiserror = 'crit'
    else:
        for error in errors:
            if error.get('hasError', True):
                if error.get('boolgood', False) or error.get('boolbad', False):
                    thiserror = 'crit'
            elif error.get('hasError', None) is False:
                thiserror = 'ok'
    metadata['error'] = setMetadata(host.name + ':' + check.name + '::error', thiserror)
    # save a snapshot of the metadata when the check ran
    history.data = json.dumps(metadata)
    history.save()
    return metadata


def alertint(check, host, value):
    # process thresholds for a int
    tholds = check.threshold.filter(enabled=True)
    errors = []
    for thold in tholds:
        errors.append(thold.checkForIntWith(value, check, host))
    return errors


def alertstr(check, host, value):
    # process thresholds for a str
    tholds = check.threshold.filter(enabled=True)
    errors = []
    for thold in tholds:
        errors.append(thold.checkForStrWith(str(value), check, host))
    return errors


def alertbool(check, host, value):
    # process thresholds for a bool
    tholds = check.threshold.filter(enabled=True)
    errors = []
    for thold in tholds:
        errors.append(thold.checkForBoolWith(str(value), check, host))
    return errors


def strtobool(str):
    # work around json lack of datatypes
    if type(str) is bool or str is None:
        return str
    elif str == '0':
        return False
    elif str == '1':
        return True
    elif str.lower() == 'false':
        return False
    elif str.lower() == 'true':
        return True
    elif str.lower() == 'off':
        return False
    elif str.lower() == 'on':
        return True
    elif str.lower() == 'no':
        return False
    elif str.lower() == 'yes':
        return True
    else:
        return None


def booltoint(bool):
    # work around json lack of datatypes
    if bool is None:
        return None
    elif not bool:
        return 0
    elif bool:
        return 1
    else:
        return None


def booltostr(bool):
    # work around json lack of datatypes
    if bool is None:
        return None
    elif bool is False:
        return 'No'
    elif bool is True:
        return 'Yes'
    else:
        return None
