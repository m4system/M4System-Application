# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-12-12 20:16
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EmailAlertHookPlugin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name',
                 models.SlugField(blank=True, help_text='Internal name, leave empty to autopopulate.', max_length=64,
                                  unique=True, verbose_name='Name')),
                ('title',
                 models.CharField(help_text='Verbose name for display purposes', max_length=256, verbose_name='Title')),
                ('recipients',
                 models.CharField(help_text='Email addresses that will receive the alerts.  Separate with a comma.',
                                  max_length=256, verbose_name='Recipients List')),
            ],
            options={
                'verbose_name_plural': 'Email Alerts',
                'verbose_name': 'Email Alert',
            },
        ),
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name',
                 models.SlugField(blank=True, help_text='Internal name, leave empty to autopopulate.', max_length=64,
                                  unique=True, verbose_name='Email Template Name')),
                ('title', models.CharField(help_text='Verbose name for display purposes', max_length=256,
                                           verbose_name='Email Template Title')),
            ],
            options={
                'ordering': ['-name'],
                'verbose_name_plural': 'Email Templates',
                'verbose_name': 'Template',
            },
        ),
        migrations.AddField(
            model_name='emailalerthookplugin',
            name='template_error',
            field=models.ForeignKey(help_text='Choose or create an email template.  You can use django templating.',
                                    on_delete=django.db.models.deletion.CASCADE, related_name='template_error',
                                    to='EmailAlertHookPlugin.EmailTemplate',
                                    verbose_name='Email Template when an error is raised.'),
        ),
        migrations.AddField(
            model_name='emailalerthookplugin',
            name='template_failing',
            field=models.ForeignKey(help_text='Choose or create an email template.  You can use django templating.',
                                    on_delete=django.db.models.deletion.CASCADE, related_name='template_failing',
                                    to='EmailAlertHookPlugin.EmailTemplate',
                                    verbose_name='Email Template when a fail is trigger.'),
        ),
        migrations.AddField(
            model_name='emailalerthookplugin',
            name='template_recovered',
            field=models.ForeignKey(help_text='Choose or create an email template.  You can use django templating.',
                                    on_delete=django.db.models.deletion.CASCADE, related_name='template_recovered',
                                    to='EmailAlertHookPlugin.EmailTemplate',
                                    verbose_name='Email Template when recovering.'),
        ),
    ]
