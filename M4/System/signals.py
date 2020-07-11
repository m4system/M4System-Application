import django

post_fetch = django.dispatch.Signal(providing_args=["retval", "datatype", "datapoint"])