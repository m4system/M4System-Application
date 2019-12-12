from django.http import Http404
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _

from M4.System.models.models import Setting


def index(request):
    try:
        frontend = Setting.objects.get(key='frontend_default')
    except:
        raise Http404(
            _(
                'No default frontend have been configured.  Set the frontend_default to the plugin name to redirect automatically.'))
    return redirect('/' + frontend.value + '/')
