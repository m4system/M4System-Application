# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2019-12-07 11:58
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('scheduler', '0001_initial'),
        ('auth', '0007_alter_validators_add_error_messages'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UIMsg',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.CharField(choices=[('20', 'info'), ('10', 'debug'), ('30', 'warning'), ('25', 'success'), ('40', 'error'), ('99', 'problem')], default='debug', help_text='The level of the message', max_length=16, verbose_name='Level')),
                ('timestamp', models.DateTimeField(auto_now_add=True, help_text='Timestamp for the event.', verbose_name='Timestamp')),
                ('msg', models.CharField(help_text='The message', max_length=1024, verbose_name='Message')),
                ('sticky', models.BooleanField(default=False, help_text='Show everytime until removed manually.', verbose_name='Sticky')),
                ('group', models.ManyToManyField(help_text='Groups who should see this message.', to='auth.Group')),
                ('user', models.ManyToManyField(blank=True, default=None, help_text='Users whohave seen this message.', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Messages',
                'ordering': ['-timestamp'],
                'verbose_name': 'Message',
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('loggedin', models.BooleanField(default=False, help_text='Is this user currentely logged-in ?', verbose_name='Currently logged-in.')),
                ('notifemail', models.EmailField(blank=True, default=None, help_text='Fill this field to receive email alerts', max_length=254, null=True, verbose_name='Notification Email')),
                ('notifcallback', models.URLField(blank=True, help_text='Fill this field to receive POST callbacks to the specified URL', max_length=1024, null=True, verbose_name='Notification URL')),
                ('prefs', models.CharField(blank=True, help_text="JSON Object containing all of the UI's settings.", max_length=4096, verbose_name='Settings')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User profile',
                'verbose_name_plural': 'Users profiles Editor',
                'permissions': (('view_traps', 'Can see received  traps'), ('silence_check', 'Can silence a check'), ('view_sla', 'Can view the SLA window'), ('view_slalog', 'Can view the SLA log window'), ('view_thresholdlog', 'Can view the threshold log window'), ('view_notifs', 'Can receive notifications')),
            },
        ),
        migrations.CreateModel(
            name='UserView',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.SlugField(help_text='Name for the view.', max_length=128, unique=True, verbose_name='Name')),
                ('default', models.BooleanField(default=False, help_text='Default view, can be only one.', verbose_name='Default')),
                ('active', models.BooleanField(default=True, help_text='Is this view available ?', verbose_name='Enabled')),
                ('note', models.CharField(blank=True, default=None, help_text='Additional information that could be usefull.', max_length=4096, null=True, verbose_name='Note')),
                ('group', models.ManyToManyField(blank=True, help_text='Groups allowed to use the view', to='auth.Group')),
            ],
            options={
                'verbose_name_plural': 'User Views',
                'ordering': ['name'],
                'verbose_name': 'User View',
            },
        ),
        migrations.CreateModel(
            name='Widgets',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.SlugField(help_text='Name of the widget.', max_length=128, unique=True, verbose_name='Name')),
                ('verbosename', models.CharField(help_text='Name of the widget as rendered on the page.', max_length=128, verbose_name='Full Name')),
                ('active', models.BooleanField(default=True, help_text='Is this widget available ?', verbose_name='Enabled')),
                ('unit', models.CharField(blank=True, default='A', help_text='Unit used for the check in the widget, i.e. A', max_length=4, verbose_name='Unit')),
                ('template', models.CharField(choices=[('snmpgetint', 'SNMP Integer Check'), ('snmpgetintgraph', 'SNMP Integer Graph'), ('snmpgetintinfo', 'SNMP Integer Info'), ('snmpgetbool', 'SNMP Boolean Check'), ('snmpgetboolgraph', 'SNMP Boolean Graph'), ('snmpgetboolinfo', 'SNMP Boolean Info'), ('snmpgetstr', 'SNMP String Check'), ('snmpgetstrgraph', 'SNMP String Graph'), ('snmpgetstrinfo', 'SNMP String Info'), ('execint', 'Exec Int Check'), ('execintgraph', 'Exec Int Graph'), ('execintinfo', 'Exec Int Info'), ('execstr', 'Exec String Check'), ('execstrgraph', 'Exec String Graph'), ('execstrinfo', 'Exec String Info'), ('execbool', 'Exec Bool Check'), ('execboolgraph', 'Exec Bool Graph'), ('execboolinfo', 'Exec Bool Info')], default='snmpgetint', help_text='The template to use to display the widget.', max_length=32, verbose_name='Template')),
                ('note', models.CharField(blank=True, default=None, help_text='Additional information that could be usefull.', max_length=4096, null=True, verbose_name='Note')),
                ('host', models.ForeignKey(blank=True, help_text='Which host does this widget refers to ?', null=True, on_delete=django.db.models.deletion.SET_NULL, to='scheduler.Hosts')),
                ('hostcheck', models.ForeignKey(blank=True, help_text='Which check does this widget refers to ?', null=True, on_delete=django.db.models.deletion.SET_NULL, to='scheduler.HostChecks')),
            ],
            options={
                'verbose_name_plural': 'Widgets',
                'ordering': ['-name'],
                'verbose_name': 'Widget',
            },
        ),
        migrations.AddField(
            model_name='userview',
            name='widgets',
            field=models.ManyToManyField(blank=True, help_text='List of widgets to display in the view', to='webview.Widgets'),
        ),
    ]