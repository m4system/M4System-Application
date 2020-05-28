from django.conf.urls import include, url
from django.contrib import admin
# We load them here to override their template.
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView, LoginView, LogoutView
from django.views.generic import RedirectView

from webview.views import settings

urlpatterns = [
    url(r'^favicon\.ico$', RedirectView.as_view(url='/public/img/favicon.ico')),  # serve the favicon and avoid 404s
    url(r'^', include('webview.urls')),
    url(r'^jet/', include('jet.urls', 'jet')),  # Django JET URLS
    url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),  # Django JET dashboard URLS
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),  # add admin
    url(r'^login/', LoginView.as_view(template_name='login.html'), name='login'),  # override the template with ours
    url(r'^logout/', LogoutView.as_view(template_name='loggedout.html'), name='logout'),  # override the template with ours
    url(r'^password_reset/', PasswordResetView.as_view(template_name='lostpass.html'), name='password_reset'),
    url(r'^password_reset_done/',
        PasswordResetDoneView.as_view(template_name='resetdone.html'), name='password_reset_done'),
    url(r'^password_reset_confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        PasswordResetConfirmView.as_view(template_name='resetconfirm.html', success_url='/'),
        name='password_reset_confirm'),  # override the template with ours
    url(r'^password_reset_complete/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    # override the template with ours
    url(r'^settings/', settings, name='settings')
    # url(r'^500/$', 'django.views.defaults.server_error'),
]
