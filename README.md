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
$ ./start tools/confs/vsr-3.8.yaml
Creating network "supervision-grafana_monitoring" with the default driver
Pulling influxdb (influxdb:1.8.10)...
1.8.10: Pulling from library/influxdb
646e886fa3cf: Pull complete
c5a360c5f105: Pull complete
535642cb98ee: Pull complete
1aca97f2aa3d: Pull complete
3df356749afd: Pull complete
7f1dbc2c143c: Pull complete
3487689ee2ff: Pull complete
Digest: sha256:98b05bb813c143a430f8b2eca8d59b5f58bffd812a9359310093901ce559366b
Status: Downloaded newer image for influxdb:1.8.10
Pulling grafana (grafana/grafana:9.5.3)...
9.5.3: Pulling from grafana/grafana
f56be85fc22e: Pull complete
2fe2fda407f1: Pull complete
6789b114b6ea: Pull complete
81dab1f0499f: Pull complete
1af72664dc17: Pull complete
94fae322688b: Pull complete
692464e6f3e6: Pull complete
da5365e3a243: Pull complete
fe21d8ff0cf2: Pull complete
Digest: sha256:35e8e1b76912e4c3bbaa8de01e730aad310acdb51ea0903f84bd098b12b8d861
Status: Downloaded newer image for grafana/grafana:9.5.3
Creating influxdb ... done
Creating grafana  ... done
{"datasource":{"id":1,"uid":"d7e39504-41c3-4f71-b615-70d3895a4bab","orgId":1,"name":"influxdb","type":"influxdb","typeLogoUrl":"","access":"proxy","url":"http://influxdb:8086","user":"","database":"telegraf","basicAuth":false,"basicAuthUser":"","withCredentials":false,"isDefault":true,"jsonData":{},"secureJsonFields":{},"version":1,"readOnly":false},"id":1,"message":"Datasource added","name":"influxdb"}
{"id":1,"slug":"overview","status":"success","uid":"dac5535c-f468-41f1-80c0-183ea60107cb","url":"/d/dac5535c-f468-41f1-80c0-183ea60107cb/overview","version":1}
{"id":2,"slug":"debug","status":"success","uid":"f68a9276-f66b-43bb-9387-fea91b3093df","url":"/d/f68a9276-f66b-43bb-9387-fea91b3093df/debug","version":1}
{"id":3,"slug":"cg-nat","status":"success","uid":"a8184370-5d23-470b-90c6-55516d9ddc03","url":"/d/a8184370-5d23-470b-90c6-55516d9ddc03/cg-nat","version":1}
{"id":4,"slug":"firewall","status":"success","uid":"b307d3e1-c470-4949-9ab9-47948359b4c5","url":"/d/b307d3e1-c470-4949-9ab9-47948359b4c5/firewall","version":1}
{"id":5,"slug":"router","status":"success","uid":"b9e35b7c-1904-49dc-a4a4-9fce4b3fb457","url":"/d/b9e35b7c-1904-49dc-a4a4-9fce4b3fb457/router","version":1}


Go to http://localhost:3000 for Grafana dashboard (admin/admin)
```

Log as admin/admin to http://monitoring-server-ip:3000.

Then, on your 6WIND product, enter the CLI to configure the system to send data to the InfluxDB database:

```console
vrouter> edit running
vrouter running config# / vrf main kpi telegraf metrics template all
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
./tools/confs/6windgate-4.33.yaml
./tools/confs/6windgate-5.6.yaml
./tools/confs/vsr-3.5.yaml
./tools/confs/vsr-3.7-cg-nat.yaml
./tools/confs/vsr-3.7.yaml
./tools/confs/vsr-3.8-cg-nat.yaml
./tools/confs/vsr-3.8.yaml
```

Configuration files can be stored anywhere but only configuration file present in the [tools/confs](./tools/confs) directory are listed

How it works
============

The start script uses ``docker-compose`` to instanciate the monitoring stack. It then calls [tools/configure_grafana.py](./tools/configure_grafana.py) to upload dashboards and the InfluxDB datasource using the Grafana web API with the provided [conf_file] as argument.

The configuration is located in the provided configuration file.

The InfluxDB container uses the ``influxdb/data`` directory to store its database.

Using an existing InfluxDB/Grafana installation
===============================================

If you already have ``Grafana`` installed, you can use [tools/configure_grafana.py](./tools/configure_grafana.py) directly. You need to configure the yaml configuration file (an existing one from [tools/confs](./tools/confs) directory or your own) to remove the datasources, and make sure that the grafana parameters suit your needs.

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

Here is an example of how an overview dashboard could be defined in the yaml configuration file.

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
