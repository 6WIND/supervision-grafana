# Monitoring 6WIND products using Grafana and InfluxDB

This repository contains scripts and dashboards to use with 6WIND products. It uses [docker](https://www.docker.com/) to spawn a monitoring stack, composed of an [InfluxDB](https://docs.influxdata.com/influxdb/) database and a [Grafana](http://docs.grafana.org) monitoring platform connected on a virtual network. Using those scripts, you will be able to see many runtime information on a web based graphical interface.

Thanks to the strong community around those tools, it will also be simple to add your own metrics to monitor other functions.

This document was tested with Ubuntu 16.04 distribution.

Quickstart
==========

To start the monitoring stack, install the dependencies, clone the repository and simple use the start script by giving the configuration file to use:

```console
# apt-get update
# apt-get install docker-compose python-requests docker.io
$ git clone https://github.com/6WIND/supervision-grafana.git
$ cd supervision-grafana.git
$ ./start tools/confs/turbo-router-1.6.yml
Creating network "supervisiongrafana_monitoring" with the default driver
Pulling influxdb (influxdb:1.4.2)...
1.4.2: Pulling from library/influxdb
723254a2c089: Pull complete
abe15a44e12f: Pull complete
409a28e3cc3d: Pull complete
920d0ed5293b: Pull complete
4e6d61de962a: Pull complete
5f29e8ea78c9: Pull complete
b15384258074: Pull complete
20bbf0e6af28: Pull complete
Digest: sha256:4b08e5315b198dbd1f1f070fbccb12f258b3219f4f1d85370156fb0bb2b95677
Status: Downloaded newer image for influxdb:1.4.2
Pulling grafana (grafana/grafana:4.6.3)...
4.6.3: Pulling from grafana/grafana
c6b13209f43b: Pull complete
a3ed95caeb02: Pull complete
051738ac6f7e: Pull complete
66e042ba6513: Pull complete
Digest: sha256:6397aafb899ef7a9ca61c2ef80863dbebce504620b044954d80203e0b8c1ada4
Status: Downloaded newer image for grafana/grafana:4.6.3
Creating influxdb
Creating grafana
{"id":1,"message":"Datasource added","name":"influxdb"}
{"slug":"debug","status":"success","version":1}
{"slug":"overview","status":"success","version":1}
{"slug":"router","status":"success","version":1}

Go to http://localhost:3000 for Grafana dashboard (admin/admin)
```

Log as admin/admin to http://monitoring-server-ip:3000.

Then, on your 6WIND product, enter the CLI to configure the system to send data to the InfluxDB database:

```console
router{conf:myconf}kpi
router{conf:myconf-kpi}kpi enable
router{conf:myconf-kpi}telegraf
router{conf:myconf-kpi-telegraf}telegraf enable
router{conf:myconf-kpi-telegraf}influxdb
router{conf:myconf-kpi-telegraf-influxdb}url http://<monitoring-server-ip>:8086
router{conf:myconf-kpi-telegraf-influxdb}database telegraf
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
