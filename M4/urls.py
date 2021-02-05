"""M4 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin

from django.views.generic import RedirectView


urlpatterns = [
    url(r'^favicon\.ico$', RedirectView.as_view(url='/public/img/favicon.ico')),  # serve the favicon and avoid 404s
    url(r'^jet/', include('jet.urls', 'jet')),  # Django JET URLS
    url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),  # Django JET dashboard URLS
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),  # add admin
    url(r'', include('M4.webview.urls'))
]

from django.conf import settings
import sys

TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'
if settings.DEBUG or TESTING:
    import debug_toolbar
    from django.contrib.staticfiles import views

    urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls)),
                    url(r'^public/(?P<path>.*)$', views.serve)]  # for the debug toolbar

