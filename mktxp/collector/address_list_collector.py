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
from collections import defaultdict

class AddressListCollector(BaseCollector):
    '''Address List collector'''

    @staticmethod
    def collect(router_entry):
        metric_labels = ['list', 'address', 'dynamic', 'timeout', 'disabled', 'comment']
        reduced_metric_labels = ['list', 'address', 'dynamic', 'disabled', 'comment']
        translation_table = {
            'dynamic': lambda value: '1' if value == 'true' else '0',
            'disabled': lambda value: '1' if value == 'true' else '0',
            'timeout': lambda value: BaseOutputProcessor.parse_timedelta_milliseconds(value) if value else '0',
            'comment': lambda value: value if value else ''
        }

        # IPv4
        address_list_names = AddressListCollector._get_list_names(router_entry.config_entry.address_list)
        if address_list_names:
            ipv4_records = AddressListMetricsDataSource.metric_records(
                router_entry,
                address_list_names,
                'ip',
                metric_labels = metric_labels,
                translation_table = translation_table
            )
            if ipv4_records:
                yield BaseCollector.gauge_collector('firewall_address_list', 'IPv4 Firewall Address List Entry', 
                                                                    ipv4_records, 'timeout', reduced_metric_labels)

                count_records = AddressListCollector._get_count_records(router_entry, ipv4_records)
                yield BaseCollector.gauge_collector('firewall_address_list_entries_count', 'Number of entries in a IPv4 firewall address list',
                                                                    count_records, 'count', ['list', MKTXPConfigKeys.ROUTERBOARD_NAME, MKTXPConfigKeys.ROUTERBOARD_ADDRESS])

        # IPv6
        ipv6_address_list_names = AddressListCollector._get_list_names(router_entry.config_entry.ipv6_address_list)
        if ipv6_address_list_names:
            ipv6_records = AddressListMetricsDataSource.metric_records(
                router_entry,
                ipv6_address_list_names,
                'ipv6',
                metric_labels=metric_labels,
                translation_table = translation_table
            )
            if ipv6_records:
                yield BaseCollector.gauge_collector('firewall_address_list_ipv6', 'Firewall IPv6 Address List Entry',
                                                                    ipv6_records, 'timeout', reduced_metric_labels)

                count_records = AddressListCollector._get_count_records(router_entry, ipv6_records)
                yield BaseCollector.gauge_collector('firewall_address_list_entries_count_ipv6', 'Number of entries in a IPv6 firewall address list',
                                                                    count_records, 'count', ['list', MKTXPConfigKeys.ROUTERBOARD_NAME, MKTXPConfigKeys.ROUTERBOARD_ADDRESS])

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

    @staticmethod
    def _get_count_records(router_entry, records):
        counts = defaultdict(int)
        for record in records:
            counts[record['list']] += 1
        
        count_records = []
        for list_name, count in counts.items():
            count_records.append({
                MKTXPConfigKeys.ROUTERBOARD_NAME: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_NAME],
                MKTXPConfigKeys.ROUTERBOARD_ADDRESS: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_ADDRESS],
                'list': list_name, 'count': count})
        return count_records
