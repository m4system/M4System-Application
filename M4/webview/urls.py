from django.conf.urls import include, url
# We load them here to override their template.
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView, LoginView, LogoutView
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
    url(r'^login/', LoginView.as_view(template_name='login.html'), name='login'),  # override the template with ours
    url(r'^logout/', LogoutView.as_view(template_name='loggedout.html'), name='logout'),  # override the template with ours
    url(r'^password_reset/', PasswordResetView.as_view(template_name='lostpass.html'), name='password_reset'),
    url(r'^password_reset_done/',
        PasswordResetDoneView.as_view(template_name='resetdone.html'), name='password_reset_done'),
    url(r'^password_reset_confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        PasswordResetConfirmView.as_view(template_name='resetconfirm.html', success_url='/'),
        name='password_reset_confirm'),  # override the template with ours
    url(r'^password_reset_complete/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    url(r'^settings/', settings, name='settings')
    # override the template with ours
]
