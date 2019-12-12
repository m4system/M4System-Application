from django.conf.urls import url

from .views import field_changed

urlpatterns = [url(r'field_changed', field_changed, name='field_changed'), ]
