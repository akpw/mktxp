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


class InterfaceTrafficMetricsDataSource:
    ''' Interface Traffic Metrics data provider
    '''             
    @staticmethod
    def metric_records(router_entry, *, metric_labels = []):
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
    def metric_records(router_entry, *, metric_labels = [], kind = 'ethernet', include_comments = False, running_only = True):
        try:
            interfaces = router_entry.api_connection.router_api().get_resource(f'/interface/{kind}').get()
            interface_names = [(interface['name'], interface.get('comment'), interface.get('running')) for interface in interfaces]

            interface_monitor_records = []
            for int_num, interface_name in enumerate(interface_names):
                interface_monitor_record = {}
                if not running_only or interface_name[2] == 'true':
                    interface_monitor_record = router_entry.api_connection.router_api().get_resource(f'/interface/{kind}').call('monitor', {'once':'', 'numbers':f'{int_num}'})[0]
                else:
                    # unless explicitly requested, no need to do a monitor call for not running interfaces                    
                    interface_monitor_record = {'name': interface_name[0], 'status': 'no-link'}

                if include_comments and interface_name[1]:
                    # combines names with comments
                    interface_monitor_record['name'] = interface_name[1] if router_entry.config_entry.use_comments_over_names else \
                                                                                                        f"{interface_name[0]} ({interface_name[1]})"                                
                interface_monitor_records.append(interface_monitor_record)
                
            return BaseDSProcessor.trimmed_records(router_entry, router_records = interface_monitor_records, metric_labels = metric_labels)
        except Exception as exc:
            print(f'Error getting {kind} interface monitor info from router{router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None

