#!/usr/bin/env python2
# Copyright 2018 6WIND S.A.

import argparse
import json
import os
import sys
import time
import yaml

import requests

#------------------------------------------------------------------------------
def generate_dashboard(name, dashboards, datasource):
    """
    Given the dashboard name, the dashboards part of the configuration, and the
    default datasource, generate a dashboard. We use the skeleton.json file, and
    fill it with given panels and template variables.

    Rows have titles, panels, and optional repeat and collapse options.
    Panels span can be configured. 12 = one lie.

    A dashboard can inherit from another one, and be enabled or disabled, has
    rows and optional templates.
    """
    data = {}

    resource_dir = os.path.join(os.path.dirname(__file__), 'resources')
    skeleton_file = os.path.join(resource_dir, 'skeleton.json')
    with open(skeleton_file) as skel:
        data = json.load(skel)

    dashboard = dashboards[name]

    templates = dashboard.get('templating', [])
    rows = dashboard.get('rows', [])
    # If we inherit from a dashboard, initialize rows and templates with this
    # dashboard.
    if 'inherits' in dashboard:
        master = dashboards[dashboard['inherits']]
        rows = master.get('rows', []) + rows
        templates = master.get('templating', []) + templates

    data['title'] = dashboard['title']

    for template in templates:
        template_data = {}
        template_dir = os.path.join(resource_dir, 'templates')
        template_file_path = os.path.join(template_dir,
                                          template['file'] + '.json')
        with open(template_file_path) as template_file:
            template_data = json.load(template_file)

        template_data['datasource'] = datasource

        # Set template default values
        if 'values' in template:
            for value in template['values']:
                template_data['current']['value'].append(value)

        data['templating']['list'].append(template_data)

    panelid = 1
    for row in rows:
        row_data = {
            'collapse': row.get('collapse', False),
            'height': 250,
            'panels': [],
            'repeat': row.get('repeat', None),
            'showTitle': True if 'title' in row else False,
            'title': row.get('title', None),
            'titleSize': 'h5'
        }

        # Process panels
        for panel in row['panels']:
            # panel can contain the file name or a dict
            if isinstance(panel, dict):
                panel_name = panel.keys()[0]
            else:
                panel_name = panel

            panel_data = {}
            panel_dir = os.path.join(resource_dir, 'panels')
            panel_file_path = os.path.join(panel_dir, panel_name + '.json')

            with open(panel_file_path) as panel_file:
                panel_data = json.load(panel_file)

            # Renumber each panel to avoid having the same one
            panel_data['id'] = panelid
            panelid += 1

            # Set datasource with default
            panel_data['datasource'] = datasource

            # Set span if found in panel
            if isinstance(panel, dict):
                if 'span' in panel[panel_name]:
                    panel_data['span'] = panel[panel_name]['span']

            row_data['panels'].append(panel_data)

        data['rows'].append(row_data)

    return data

#------------------------------------------------------------------------------
def get_config(conf_file_path):
    """
    Parse the yaml configuration file into a dict.
    """
    with open(conf_file_path, 'r') as conf_file:
        config = yaml.load(conf_file)

    return config

#------------------------------------------------------------------------------
def get_grafana_url(config):
    """
    Given the configuration, return grafana url.
    """
    return os.path.join('http://', '%s:%u' % (config['grafana']['host'],
                                              config['grafana']['port']))

#------------------------------------------------------------------------------
def get_grafana_session(config):
    """
    Connect to grafana and get a session. We try for 60 seconds.
    """
    session = requests.Session()
    tries = 30
    url = get_grafana_url(config)
    user = config['grafana']['user']
    password = config['grafana']['password']

    # Wait for grafana to be ready for 60 seconds
    while tries:
        try:
            session.post(
                os.path.join(url, 'login'),
                data=json.dumps({
                    'user': user,
                    'email': '',
                    'password': password
                }),
                headers={
                    'content-type': 'application/json'
                })
            break
        except requests.exceptions.ConnectionError as connection_error:
            tries -= 1
            time.sleep(2)
            if tries == 0:
                print connection_error
                exit(1)

    return session

#------------------------------------------------------------------------------
def upload_datasources(session, config):
    """
    Upload datasources found in configuration to grafana.
    """
    default_datasource = 'influxdb'

    if 'datasources' in config and config['datasources']:
        for datasource in config['datasources'].itervalues():
            if not datasource['enabled']:
                continue

            del datasource['enabled']

            if datasource['isDefault']:
                default_datasource = datasource['name']

            datasources_post = session.post(
                os.path.join(get_grafana_url(config), 'api', 'datasources'),
                data=json.dumps(datasource),
                headers={'content-type': 'application/json'}
            )
            print datasources_post.text

    return default_datasource

#------------------------------------------------------------------------------
def upload_dashboards(session, config, default_datasource):
    """
    Upload dashboards found in configuration to grafana.
    """
    for name, dashboard in config['dashboards'].iteritems():
        if not dashboard['enabled']:
            continue

        data = generate_dashboard(name, config['dashboards'],
                                  default_datasource)

        dashboard_post = session.post(
            os.path.join(get_grafana_url(config), 'api', 'dashboards', 'db'),
            data=json.dumps({'dashboard': data}),
            headers={'content-type': 'application/json'},
        )
        print dashboard_post.text

#------------------------------------------------------------------------------
def main():
    """
    Main.
    """
    parser = argparse.ArgumentParser(description='Configure grafana')
    parser.add_argument('configuration',
                        metavar='FILE',
                        help='Specify the configuration to load from confs directory')

    args = parser.parse_args()

    config = get_config(args.configuration)
    session = get_grafana_session(config)

    default_datasource = upload_datasources(session, config)
    upload_dashboards(session, config, default_datasource)

if __name__ == '__main__':
    main()
