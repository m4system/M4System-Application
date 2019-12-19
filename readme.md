---
title: "Install on Window (Dev)"
date: 2017-01-05
description:
  A full guide to install and setup M4 on a Windows machine.
  This setup is not designed for production use.
---

[![Actions Status](https://github.com/dgagnon/m4system/workflows/M4%20Unit%20Test/badge.svg)](https://github.com/dgagnon/m4system/actions)


## Install Python

Install vcc++ 2015 and build tools
- https://www.python.org/ftp/python/3.5.1/python-3.5.1-amd64.exe
- https://www.visualstudio.com/downloads/#build-tools-for-visual-studio-2019

More information on building python modules on windows here: https://wiki.python.org/moin/WindowsCompilers
Install getttext: https://mlocati.github.io/articles/gettext-iconv-windows.html

reboot

## Install RabbitMQ

Follow the instruction here: https://www.rabbitmq.com/install-windows.html

```
rabbitmqctl add_user m4 changeme
rabbitmqctl add_vhost m4
rabbitmqctl set_user_tags m4 m4
rabbitmqctl set_permissions -p m4 m4 ".*" ".*" ".*"
```

## Install lessc

npm install lessc -g

## Setup SNMP

See: https://blog.paessler.com/how-to-enable-snmp-on-your-operating-system

Allow localhost with community "public"

This will allow M4 to poll your local SNMP deamon to get some fresh data.

## Setup M4

```
pip3.5 install virtualenvwrapper-win
git clone https://github.com/dgagnon/m4system.git mym4dev
mkvirtualenv mym4dev
pip3.5 install -e .
manage migrate djangoplugins
manage migrate
manage collectstatic
```

migrations , revisions, cache table, fixtures, collectstatic

## Load the fixtures

```
python3.5 manage.py loaddata fixtures/auth.json
python3.5 manage.py loaddata fixtures/user.json
python3.5 manage.py loaddata fixtures/djcelery.json
python3.5 manage.py loaddata fixtures/scheduler.json
python3.5 manage.py loaddata fixtures/webview.json
```

## Run M4

```
start.bat
```

## Login to M4

http://127.0.0.1:8000

m4 / Changeme1!

