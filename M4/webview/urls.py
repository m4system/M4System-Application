from django.conf.urls import include, url

# import the views from the current folder
from M4.webview.views import *

urlpatterns = [
    url(r'^(?P<view>|view/[A-Za-z0-9\-\_]+)$', index, name='index'),
    url(r'^test$', test, name='test'),
    url(r'^data/(?P<host>[A-Za-z0-9\-\_]+)/(?P<check>[A-Za-z0-9\_\-]+)/(?P<checktype>[a-z]+)/$', getCheck,
        name='getCheck'),
    url(r'^graph/(?P<host>[A-Za-z0-9\-\_]+)/(?P<check>[A-Za-z0-9\_\-]+)(/|/(?P<qty>[0-9]+)/)$', getGraphData,
        name='getGraphData'),
    url(r'^eventlog(/|/(?P<qty>[0-9]+)/)$', getEvents, name='getEvents'),
    url(r'^sla/$', getSla, name='getSla'),
    url(r'^trap/$', getTraps, name='getTraps'),
    url(r'^slalog(/|/(?P<qty>[0-9]+)/)$', getSlaLog, name='getSlaLog'),
    url(r'^graph/(?P<host>[A-Za-z0-9\-\_]+)/(?P<check>[A-Za-z0-9\_\-]+)/$', getGraphData, name='getGraphData'),
    url(r'^widget/(?P<host>[A-Za-z0-9\-\_]+)/(?P<check>[A-Za-z0-9\_\-]+)/(?P<name>[A-Za-z0-9\-\_]+)/$', getWidget,
        name='getWidget'),
    url(r'^msg/$', getMsg, name='getMsg'),
    url(r'^report/(?P<host>[A-Za-z0-9\-\_]+)/(?P<check>[A-Za-z0-9\_\-]+)/', reports, name='reports'),
    url(r'^delay(/|/(?P<days>[0-9]+)/)$', getDelay, name='getDelay'),
    url(r'^notifications/m4-(?P<host>[A-Za-z0-9\-\_]+)--(?P<check>[A-Za-z0-9\_\-]+)-notifs/(?P<status>[a-z]+)/$',
        setNotifs, name='setNotifs'),
]
