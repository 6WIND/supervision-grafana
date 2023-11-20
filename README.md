# Monitoring 6WIND products using Grafana and InfluxDB

This repository contains scripts and dashboards to use with 6WIND products. It uses [docker](https://www.docker.com/) to spawn a monitoring stack, composed of an [InfluxDB](https://docs.influxdata.com/influxdb/) database and a [Grafana](http://docs.grafana.org) monitoring platform connected on a virtual network. Using those scripts, you will be able to see many runtime information on a web based graphical interface.

Thanks to the strong community around those tools, it will also be simple to add your own metrics to monitor other functions.

This document was tested with Ubuntu 22.04 distribution.

Quickstart
==========

To start the monitoring stack, install the dependencies, clone the repository
and simple use the start script by giving the configuration file to use.

```console
# apt-get update
# apt-get install docker-compose python3-requests docker.io
$ git clone https://github.com/6WIND/supervision-grafana.git
$ cd supervision-grafana
$ ./start tools/confs/vsr-3.7.yml
Creating network "supervision-grafana_monitoring" with the default driver
Pulling influxdb (influxdb:1.7.10)...
1.7.10: Pulling from library/influxdb
16cf3fa6cb11: Pull complete
3ddd031622b3: Pull complete
69c3fcab77df: Pull complete
25737831bed1: Pull complete
f7cb4946ee1e: Pull complete
1620e475f8f1: Pull complete
1cf7b9d4576e: Pull complete
f8d2c0a67069: Pull complete
Digest: sha256:d1f588db9e015e304ee5174322655e193b3706db947c9b3205b01dbba97794c8
Status: Downloaded newer image for influxdb:1.7.10
Pulling grafana (grafana/grafana:6.6.2)...
6.6.2: Pulling from grafana/grafana
4167d3e14976: Pull complete
f5de5b425a84: Pull complete
0566de8a7966: Pull complete
21558318b453: Pull complete
9c0705e53d50: Pull complete
0cb366e38dc9: Pull complete
9d6a49548b66: Pull complete
6a9f63007f4a: Pull complete
Digest: sha256:4282e80b18bb148dcc9745a337c7008d4c8397b369933cfb4e66d15f363d1818
Status: Downloaded newer image for grafana/grafana:6.6.2
Creating influxdb ... done
Creating grafana  ... done
{"datasource":{"id":1,"orgId":1,"name":"influxdb","type":"influxdb","typeLogoUrl":"","access":"proxy","url":"http://influxdb:8086","password":"","user":"","database":"telegraf","basicAuth":false,"basicAuthUser":"","basicAuthPassword":"","withCredentials":false,"isDefault":true,"jsonData":{},"secureJsonFields":{},"version":1,"readOnly":false},"id":1,"message":"Datasource added","name":"influxdb"}
{"id":1,"slug":"overview","status":"success","uid":"HdvzZh3Vz","url":"/d/HdvzZh3Vz/overview","version":1}
{"id":2,"slug":"debug","status":"success","uid":"E5vkWh3Vz","url":"/d/E5vkWh3Vz/debug","version":1}
{"id":3,"slug":"cg-nat","status":"success","uid":"RhDzZh3Vk","url":"/d/RhDzZh3Vk/cg-nat","version":1}
{"id":4,"slug":"router","status":"success","uid":"OAvkWh34z","url":"/d/OAvkWh34z/router","version":1}

Go to http://localhost:3000 for Grafana dashboard (admin/admin)
```

Log as admin/admin to http://monitoring-server-ip:3000.

Then, on your 6WIND product, enter the CLI to configure the system to send data to the InfluxDB database:

```console
vrouter> edit running
vrouter running config# system kpi
vrouter running kpi# / vrf main kpi telegraf influxdb-output url http://<monitoring-server-ip>:8086 database telegraf
vrouter running kpi# commit
```

The 6WIND product must be able to reach the monitoring server IP.

In the Grafana window, you should see monitoring data being graphed.

To stop the monitoring stack:

```console
$ ./stop
Stopping grafana ... done
Stopping influxdb ... done
Removing grafana ... done
Removing influxdb ... done
Removing network supervisiongrafana_monitoring
```

Some configuration files are stored in the [tools/confs](./tools/confs) directory
The list of this existing configuration files can be listed by simply called the start script with no argument

```console
$ ./start
Usage: ./start [conf_file]
Existing configuration file are:
./tools/confs/vrouter-3.0.yml
./tools/confs/turbo-ipsec-next.yml
./tools/confs/turbo-router-next.yml
./tools/confs/turbo-ipsec-1.6.yml
./tools/confs/6windgate-4.19.yml
./tools/confs/turbo-router-1.6.yml
./tools/confs/6windgate-next.yml
```

Configuration files can be stored anywhere but only configuration file present in the [tools/confs](./tools/confs) directory are listed

How it works
============

The start script uses ``docker-compose`` to instanciate the monitoring stack. It then calls [tools/configure_grafana.py](./tools/configure_grafana.py) to upload dashboards and the InfluxDB datasource using the Grafana web API with the provided [conf_file] as argument.

The configuration is located in the provided configuration file.

The InfluxDB container uses the ``influxdb/data`` directory to store its database.

Using an existing InfluxDB/Grafana installation
===============================================

If you already have ``Grafana`` installed, you can use [tools/configure_grafana.py](./tools/configure_grafana.py) directly. You need to configure the yml configuration file (an existing one from [tools/confs](./tools/confs) directory or your own) to remove the datasources, and make sure that the grafana parameters suit your needs.

```yaml
datasources:

grafana:
  host: your-grafana-ip
  port: your-grafana-port
  user: your-grafana-user
  password: your-grafana-user
```

The generated dashboards currently need the ``InfluxDB`` source to be called 'influxdb'.

Dashboard configuration
=======================

Here is an example of how an overview dashboard could be defined in the yml configuration file.

```yaml
dashboards:
  overview:
    enabled: yes
    title: overview
    rows:
      - title: system
        panels:
          - base-uptime
          - base-fp-status
          - base-ram-usage:
            span: 4
    templating:
      - file: host
```

This configuration will create an ``overview`` dashboard, containing one row named ``system``. This row contains the ``base-uptime``, ``base-fp-status`` and ``base-ram-usage`` panels. The ``base-ram-usage`` panel size is overriden to fit in ``4`` blocks (note that each row = 12 blocks). The panels are defined in [tools/resources/panels](./tools/resources/panels) or in a subdirectory of [tools/resources/panels](./tools/resources/panels), and are the result of the ``Grafana`` Panel JSON export feature. A template variable named ``host`` is created as well, defined in [tools/resources/templates/host.json](./tools/resources/templates/host.json).

The available keywords at dashboard level are:
- ``enabled`` (yes/no): upload the dashboard or not in Grafana
- ``title`` (string): set the dashboard name
- ``rows`` (list): describe the dashboard rows
- ``templating`` (list): describe the dashboard template variables
- ``inherits`` (dashboard name): use the rows and template variables from another dashboard

The available keywords at templating level are:
- ``file`` (string): include this template file in the dashboard
- ``values`` (list): set the default values for this template file

The available keywords at row level are:
- ``title`` (string): set the row title
- ``panels`` (list): set the list of panels in this row
- ``repeat`` (variable): repeat a row for each value of a variable

The only available keyword at panel level is:
- ``span`` (int): override the number of blocks taken by a panel when displayed (a line has 12 blocks).

Adding a new panel
==================

Adding a new panel means adding a new JSON file describing this panel in the [tools/resources/panels](./tools/resources/panels) directory. There are two ways to generate such file:
- use an existing panel file and modify it to your needs
- design the panel in Grafana, click on the panel name, on the button left of
  'View', and 'Panel JSON', and save the content

Once the file is saved, it can be added to dashboard rows.
