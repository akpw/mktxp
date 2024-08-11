# coding=utf8
## Copyright (c) 2020 Arseniy Kuznetsov
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License
## as published by the Free Software Foundation; either version 2
## of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.


from mktxp.datasource.base_ds import BaseDSProcessor


class HealthMetricsDataSource:
    ''' Health Metrics data provider
    '''             
    @staticmethod
    def metric_records(router_entry, *, metric_labels = None, translation_table = None, translate_if_no_value = False):
        if metric_labels is None:
            metric_labels = []                
        try:
            health_records = router_entry.api_connection.router_api().get_resource('/system/health').get()
            for record in health_records:
                if 'name' in record:
                    # Note: The API in RouterOS v7.X+ returns a response like this:
                    # [{'name': 'temperature', 'value': '33', 'type': 'C'}, ...]
                    # To make this work for both v6 and v7 add a <name>:<value> pair in v7
                    # Otherwise it is not possible to get the value by name (e.g. records['voltage'])
                    name = record['name']
                    val = record.get('value', None)
                    record[name] = val

            return BaseDSProcessor.trimmed_records(router_entry, router_records = health_records, metric_labels = metric_labels, 
                                                    translation_table = translation_table, translate_if_no_value = translate_if_no_value)
        except Exception as exc:
            print(f'Error getting system health info from router {router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None
