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
from mktxp.datasource.system_resource_ds import SystemResourceMetricsDataSource
from mktxp.utils.utils import routerOS7_version


class BaseInterfaceDataSource:
    @staticmethod
    def rewrite_interface_names(router_entry, metric_records):
        for metric_record in metric_records:
            if metric_record.get('comment'):
                if router_entry.config_entry.use_comments_over_names:
                    metric_record['name'] = metric_record['comment']
                else:
                    metric_record['name'] = f"{metric_record['name']} ({metric_record['comment']})"

        return metric_records


class InterfaceMetricsDataSource(BaseInterfaceDataSource):
    """ Interface Monitor Metrics data provider
    """
    @staticmethod
    def metric_records(router_entry, *, metric_labels=None, kind='ethernet', additional_proplist=None,
                       translation_table=None):
        if metric_labels is None:
            metric_labels = []

        if additional_proplist is None:
            additional_proplist = []

        call_params = {
            'proplist': ','.join(['name', 'running', 'disabled'] + additional_proplist)
        }

        try:
            interface_records = router_entry.api_connection.router_api().get_resource(
                f'/interface/{kind}'
            ).call(
                'print',
                call_params
            )
            interface_records = BaseInterfaceDataSource.rewrite_interface_names(router_entry, interface_records)
            return BaseDSProcessor.trimmed_records(
                router_entry,
                router_records=interface_records,
                metric_labels=metric_labels,
                translation_table=translation_table
            )
        except Exception as exc:
            print(f'Error getting {kind} interface info from router {router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None


class InterfaceTrafficMetricsDataSource(BaseInterfaceDataSource):
    """ Interface Traffic Metrics data provider
    """
    @staticmethod
    def metric_records(router_entry, *, metric_labels, translation_table=None):
        metric_labels = metric_labels or []
        try:
            # get stats for all existing interfaces
            metric_stats_records = router_entry.api_connection.router_api().get_resource(
                '/interface'
            ).call(
                'print',
                {'stats': 'detail'}
            )
            metric_stats_records = BaseInterfaceDataSource.rewrite_interface_names(router_entry, metric_stats_records)
            return BaseDSProcessor.trimmed_records(
                router_entry=router_entry,
                router_records=metric_stats_records,
                metric_labels=metric_labels,
                translation_table=translation_table,
            )
        except Exception as exc:
            print(f'Error getting interface traffic stats info from router {router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None


class InterfaceMonitorMetricsDataSource:
    """ Interface Monitor Metrics data provider
    """
    @staticmethod
    def metric_records(router_entry, *, metric_labels = None, translation_table = None, kind = 'ethernet', include_comments = False, running_only = True):
        if metric_labels is None:
            metric_labels = []

        ver = SystemResourceMetricsDataSource.os_version(router_entry)
        # On RouterOS 7, the 'monitor' action was replaced with 'info' for LTE interfaces, and the 'number' key was replaced with 'numbers'
        monitor_action = 'info' if kind == 'lte' and not routerOS7_version(ver) else 'monitor'
        monitor_numbers_key = 'number' if kind == 'lte' and not routerOS7_version(ver) else 'numbers'

        try:
            interfaces = router_entry.api_connection.router_api().get_resource(f'/interface/{kind}').call('print', {'proplist':'name,comment,running'})

            interface_monitor_records = []
            for int_num, interface in enumerate(interfaces):
                interface_monitor_record = {}
                if not running_only or interface['running'] == 'true':
                    interface_monitor_record = router_entry.api_connection.router_api().get_resource(f'/interface/{kind}').call(monitor_action, {'once':'', monitor_numbers_key:f'{int_num}'})[0]
                else:
                    # unless explicitly requested, no need to do a monitor call for not running interfaces
                    interface_monitor_record = {'name': interface['name'], 'status': 'no-link'}

                if include_comments and interface.get('comment'):
                    # combines names with comments
                    interface_monitor_record['name'] = interface['comment'] if router_entry.config_entry.use_comments_over_names else \
                                                                                                        f"{interface['name']} ({interface['comment']})"
                interface_monitor_records.append(interface_monitor_record)

            # With wifiwave2, Mikrotik renamed the field 'registered-clients' to 'registered-peers'
            # For backward compatibility, including both variants
            for interface_monitor_record in interface_monitor_records:
                if 'registered-peers' in interface_monitor_record:
                    interface_monitor_record['registered-clients'] = interface_monitor_record['registered-peers']
            return BaseDSProcessor.trimmed_records(router_entry, router_records = interface_monitor_records, metric_labels = metric_labels, translation_table=translation_table)
        except Exception as exc:
            print(f'Error getting {kind} interface monitor info from router {router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None
