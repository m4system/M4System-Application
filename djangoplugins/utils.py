from __future__ import absolute_import

from importlib import import_module

from django.conf import settings
from django.conf.urls import include, url
from django.db import connection


def get_plugin_name(cls):
    return "%s.%s" % (cls.__module__, cls.__name__)


def get_plugin_from_string(plugin_name):
    """
    Returns plugin or plugin point class from given ``plugin_name`` string.

    Example of ``plugin_name``::

        'my_app.MyPlugin'

    """
    modulename, classname = plugin_name.rsplit('.', 1)
    module = import_module(modulename)
    return getattr(module, classname)


def include_plugins(point, pattern=r'{plugin}/', urls='urls'):
    pluginurls = []
    for plugin in point.get_plugins():
        if hasattr(plugin, urls) and hasattr(plugin, 'name'):
            _urls = getattr(plugin, urls)
            for myurl in _urls:
                myurl.default_args['plugin'] = plugin.name
            pluginurls.append(url(
                pattern.format(plugin=plugin.name),
                include(_urls)
            ))
    return include(pluginurls)


def import_app(app_name):
    # print(app_name)
    try:
        mod = import_module(app_name)
    except ImportError as e:  # Maybe it's AppConfig
        parts = app_name.split('.')
        tmp_app, app_cfg_name = '.'.join(parts[:-1]), parts[-1]
        try:
            # print(parts[:-2])
            tmp_app = import_module(tmp_app)
            import_module('%s.plugins' % parts[:-2][0])  # TODO: fix this
        except ImportError as f:
            # print(f)
            raise
        mod = getattr(tmp_app, app_cfg_name).name
        mod = import_module(mod)
    return mod


def load_plugins():
    for app in settings.INSTALLED_APPS:
        try:
            import_module('%s.plugins' % app)
        except ImportError:
            import_app(app)


def db_table_exists(table_name):
    return table_name in connection.introspection.table_names()
