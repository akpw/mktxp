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


from mktxp.collector.base_collector import BaseCollector
from mktxp.flow.processor.output import BaseOutputProcessor
from mktxp.cli.config.config import MKTXPConfigKeys
from mktxp.datasource.address_list_ds import AddressListMetricsDataSource


class AddressListCollector(BaseCollector):
    '''Address List collector'''

    @staticmethod
    def collect(router_entry):
        metric_labels = ['list', 'address', 'dynamic', 'timeout', 'disabled', 'comment']
        reduced_metric_labels = [label for label in metric_labels if label != 'timeout']
        translation_table = {
            'dynamic': lambda value: '1' if value == 'true' else '0',
            'disabled': lambda value: '1' if value == 'true' else '0',
            'timeout': lambda value: BaseOutputProcessor.parse_timedelta_milliseconds(value) if value else '0',
            'comment': lambda value: value if value else ''
        }

        # IPv4
        address_list_names = AddressListCollector._get_list_names(router_entry.config_entry.address_list)
        if address_list_names:
            yield from AddressListCollector._collect_and_yield_metrics(router_entry, address_list_names, 'ip', metric_labels, reduced_metric_labels, translation_table)

        # IPv6
        ipv6_address_list_names = AddressListCollector._get_list_names(router_entry.config_entry.ipv6_address_list)
        if ipv6_address_list_names:
            yield from AddressListCollector._collect_and_yield_metrics(router_entry, ipv6_address_list_names, 'ipv6', metric_labels, reduced_metric_labels, translation_table)

    @staticmethod
    def _collect_and_yield_metrics(router_entry, address_list_names, ip_version, metric_labels, reduced_metric_labels, translation_table):
        ipv6_suffix = '_ipv6' if ip_version == 'ipv6' else ''
        
        # Collect and yield address list entries
        records = AddressListMetricsDataSource.metric_records(
            router_entry,
            address_list_names,
            ip_version,
            metric_labels=metric_labels,
            translation_table=translation_table
        )
        if records:
            yield BaseCollector.gauge_collector(f'firewall_address_list{ipv6_suffix}', f'Firewall {ip_version.upper()} Address List Entry',
                                                                records, 'timeout', reduced_metric_labels)

        # Collect and yield address list counts
        counts = AddressListMetricsDataSource.count_metric_records(router_entry, address_list_names, ip_version)
        if not counts:
            return

        # Counts for all lists
        all_lists_records = []
        for count_type, count in counts['all_lists'].items():
            all_lists_records.append({
                'count_type': count_type,
                'count': count,
                **router_entry.router_id
            })
        if all_lists_records:
            yield BaseCollector.gauge_collector(f'firewall_address_list_all_count{ipv6_suffix}',
                                                f'Total number of addresses in all {ip_version.upper()} address lists',
                                                all_lists_records, 'count', ['count_type'])

        # Counts for selected lists
        selected_lists_records = []
        for list_name, list_counts in counts['selected_lists'].items():
            selected_lists_records.append({
                'list': list_name,
                'count': list_counts['total'],
                **router_entry.router_id
            })
        if selected_lists_records:
            yield BaseCollector.gauge_collector(f'firewall_address_list_selected_count{ipv6_suffix}',
                                                f'Number of addresses in the selected {ip_version.upper()} address list',
                                                selected_lists_records, 'count', ['list'])

    @staticmethod
    def _get_list_names(config_value):
        if not config_value:
            return []
        if isinstance(config_value, str):
            if config_value.lower() == 'none':
                return []
            return [name.strip() for name in config_value.split(',') if name.strip()]
        if isinstance(config_value, list):
            return [name for name in config_value if name]
        return []
