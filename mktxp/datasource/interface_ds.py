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
from mktxp.flow.processor.output import BaseOutputProcessor

class InterfaceTrafficMetricsDataSource:
    ''' Interface Traffic Metrics data provider
    '''
    @staticmethod
    def metric_records(router_entry, *, metric_labels = None):
        if metric_labels is None:
            metric_labels = []

        try:
            traffic_records = router_entry.api_connection.router_api().get_resource('/interface').get(running='yes', disabled='no')

            return BaseDSProcessor.trimmed_records(router_entry, router_records = traffic_records, metric_labels = metric_labels)
        except Exception as exc:
            print(f'Error getting interface traffic info from router{router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None


class InterfaceMonitorMetricsDataSource:
    ''' Interface Monitor Metrics data provider
    '''
    @staticmethod
    def metric_records(router_entry, *, metric_labels = None, kind = 'ethernet', include_comments = True, running_only = True):
        if metric_labels is None:
            metric_labels = []
        try:
            interfaces = router_entry.api_connection.router_api().get_resource(f'/interface/{kind}').call('print', {'proplist':'.id,name,comment,running'})

            interface_monitor_records = []
            for interface in interfaces:
                interface_monitor_record = {}
                if not running_only or interface['running'] == 'true':
                    interface_monitor_record = router_entry.api_connection.router_api().get_resource(f'/interface/{kind}').call('monitor', {'once':'', '.id': interface['id']})[0]
                else:
                    # unless explicitly requested, no need to do a monitor call for not running interfaces
                    interface_monitor_record = {'name': interface['name'], 'status': 'no-link'}

                interface_monitor_record['comment'] = interface.get('comment', '')

                interface_monitor_records.append(interface_monitor_record)

            # With wifiwave2, Mikrotik renamed the field 'registered-clients' to 'registered-peers'
            # For backward compatibility, including both variants
            for interface_monitor_record in interface_monitor_records:
                if 'registered-peers' in interface_monitor_record:
                    interface_monitor_record['registered-clients'] = interface_monitor_record['registered-peers']

            rate_value =  {
                '10Mbps': '10',
                '100Mbps': '100',
                '1Gbps': '1000',
                '2.5Gbps': '2500',
                '5Gbps': '5000',
                '10Gbps': '10000',
                '40Gbps': '40000'
            }

            translation_table = {
                'status': lambda value: '1' if value=='link-ok' else '0',
                'rate': lambda value: rate_value.get(value, BaseOutputProcessor.parse_interface_rate(value)),
                'full_duplex': lambda value: '1' if value=='true' else (None if value is None else '0'),
                'sfp_temperature': lambda value: None if value is None else value
            }

            return BaseDSProcessor.trimmed_records(router_entry, router_records = interface_monitor_records, metric_labels = metric_labels, translation_table=translation_table)
        except Exception as exc:
            print(f'Error getting {kind} interface monitor info from router{router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None
