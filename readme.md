---
title: "Install on Window (Dev)"
date: 2017-01-05
description:
  A full guide to install and setup M4 on a Windows machine.
  This setup is not designed for production use.
---




## Install Python

Install vcc++ 2015 and build tools
- https://www.python.org/ftp/python/3.5.1/python-3.5.1-amd64.exe
- https://www.visualstudio.com/downloads/#build-tools-for-visual-studio-2019

More information on building python modules on windows here: https://wiki.python.org/moin/WindowsCompilers

reboot

cd to your folder

```
pip install -r requirements.txt
```

## Install RabbitMQ

Follow the instruction here: https://www.rabbitmq.com/install-windows.html


## Setup SNMP

See: https://blog.paessler.com/how-to-enable-snmp-on-your-operating-system

Allow localhost with community "public"

This will allow M4 to poll your local SNMP deamon to get some fresh data.


## Setup Django

migrations , revisions, cache table, fixtures, collectstatic

## Run M4

```
start.bat
```

## Login to M4

http://127.0.0.1:8000

m4 / Changeme1!
