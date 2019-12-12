# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2019-12-12 22:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('DashboardDisplayPlugin', '0002_auto_20191212_1605'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dashboarddisplayplugin',
            name='logo',
            field=models.CharField(blank=True, help_text='Enter the path to your logo relative to /static/',
                                   max_length=256, verbose_name='Company Logo'),
        ),
        migrations.AlterField(
            model_name='dashboarddisplayplugin',
            name='slogan',
            field=models.CharField(blank=True, help_text='Tag Line on the dashboard.', max_length=1024,
                                   verbose_name='Company Slogan'),
        ),
        migrations.AlterField(
            model_name='dashboarddisplayplugin',
            name='template',
            field=models.CharField(blank=True,
                                   help_text='On-disk template prefix.  There must be one template per type.',
                                   max_length=128, verbose_name='Template Prefix'),
        ),
    ]
