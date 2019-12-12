# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2019-12-12 22:28
from __future__ import unicode_literals

from django.db import migrations


def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    NumberThresholdTriggerPlugin = apps.get_model("ThresholdTriggerPlugin", "NumberThresholdTriggerPlugin")
    TriggerPlugin = apps.get_model('System', 'TriggerPlugin')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    db_alias = schema_editor.connection.alias
    NumberThresholdTriggerPlugin.objects.using(db_alias).create(pk=1, name='above-10', title='Above 10',
                                                                number_high='10')
    TriggerPlugin.objects.using(db_alias).create(id=1, name='(NumberThresholdPlugin) Fail Above 10', datatype='number',
                                                 object_id=1,
                                                 content_type=ContentType.objects.get(pk=26))


def reverse_func(apps, schema_editor):
    # forwards_func() creates two Country instances,
    # so reverse_func() should delete them.
    NumberThresholdTriggerPlugin = apps.get_model("ThresholdTriggerPlugin", "NumberThresholdTriggerPlugin")
    TriggerPlugin = apps.get_model('System', 'TriggerPlugin')
    db_alias = schema_editor.connection.alias

    NumberThresholdTriggerPlugin.objects.using(db_alias).get(pk=1).delete()
    TriggerPlugin.objects.using(db_alias).get(id=1).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('ThresholdTriggerPlugin', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
