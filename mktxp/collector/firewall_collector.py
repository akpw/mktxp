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


from mktxp.cli.config.config import MKTXPConfigKeys
from mktxp.collector.base_collector import BaseCollector
from mktxp.datasource.firewall_ds import FirewallMetricsDataSource


class FirewallCollector(BaseCollector):
    ''' Firewall rules traffic metrics collector
    '''    
    @staticmethod
    def collect(router_entry):
        # Initialize all pool counts, including those currently not used
        # These are the same for both IPv4 and IPv6
        firewall_labels = ['chain', 'action', 'bytes', 'comment', 'log', 'out_interface', 'protocol']

        if router_entry.config_entry.firewall:
            # ~*~*~*~*~*~ IPv4 ~*~*~*~*~*~
            firewall_filter_records = FirewallMetricsDataSource.metric_records(router_entry, metric_labels = firewall_labels, filter_path='filter')
            if firewall_filter_records:           
                metrics_records = [FirewallCollector.metric_record(router_entry, record) for record in firewall_filter_records]
                firewall_filter_metrics = BaseCollector.counter_collector('firewall_filter', 'Total amount of bytes matched by firewall rules', metrics_records, 'bytes', ['name', 'log'])
                yield firewall_filter_metrics

            firewall_raw_records = FirewallMetricsDataSource.metric_records(router_entry, metric_labels = firewall_labels, filter_path='raw')
            if firewall_raw_records:      
                metrics_records = [FirewallCollector.metric_record(router_entry, record) for record in firewall_raw_records]     
                firewall_raw_metrics = BaseCollector.counter_collector('firewall_raw', 'Total amount of bytes matched by raw firewall rules', metrics_records, 'bytes', ['name', 'log'])
                yield firewall_raw_metrics

            filter_nat_records = FirewallMetricsDataSource.metric_records(router_entry, metric_labels = firewall_labels, filter_path='nat')
            if filter_nat_records:
                metrics_records = [FirewallCollector.metric_record(router_entry, record) for record in filter_nat_records]
                filter_nat_metrics = BaseCollector.counter_collector('firewall_nat', 'Total amount of bytes matched by NAT rules', metrics_records, 'bytes', ['name', 'log'])
                yield filter_nat_metrics

            filter_mangle_records = FirewallMetricsDataSource.metric_records(router_entry, metric_labels = firewall_labels, filter_path='mangle')
            if filter_mangle_records:
                metrics_records = [FirewallCollector.metric_record(router_entry, record) for record in filter_mangle_records]
                filter_mangle_metrics = BaseCollector.counter_collector('firewall_mangle', 'Total amount of bytes matched by Mangle rules', metrics_records, 'bytes', ['name', 'log'])
                yield filter_mangle_metrics

        # ~*~*~*~*~*~ IPv6 ~*~*~*~*~*~
        if router_entry.config_entry.ipv6_firewall:
            firewall_filter_records_ipv6 =  FirewallMetricsDataSource.metric_records(router_entry, metric_labels = firewall_labels, filter_path='filter', ipv6=True)
            if firewall_filter_records_ipv6:           
                metrics_records_ipv6 = [FirewallCollector.metric_record(router_entry, record) for record in firewall_filter_records_ipv6]
                firewall_filter_metrics_ipv6 = BaseCollector.counter_collector('firewall_filter_ipv6', 'Total amount of bytes matched by firewall rules (IPv6)', metrics_records_ipv6, 'bytes', ['name', 'log'])
                yield firewall_filter_metrics_ipv6

            firewall_raw_records_ipv6 = FirewallMetricsDataSource.metric_records(router_entry, metric_labels = firewall_labels, filter_path='raw', ipv6=True)
            if firewall_raw_records_ipv6:      
                metrics_records_ipv6 = [FirewallCollector.metric_record(router_entry, record) for record in firewall_raw_records_ipv6]     
                firewall_raw_metrics_ipv6 = BaseCollector.counter_collector('firewall_raw_ipv6', 'Total amount of bytes matched by raw firewall rules (IPv6)', metrics_records_ipv6, 'bytes', ['name', 'log'])
                yield firewall_raw_metrics_ipv6

            filter_nat_records_ipv6 = FirewallMetricsDataSource.metric_records(router_entry, metric_labels = firewall_labels, filter_path='nat', ipv6=True)
            if filter_nat_records_ipv6:
                metrics_records_ipv6 = [FirewallCollector.metric_record(router_entry, record) for record in filter_nat_records_ipv6]
                filter_nat_metrics_ipv6 = BaseCollector.counter_collector('firewall_nat_ipv6', 'Total amount of bytes matched by NAT rules (IPv6)', metrics_records_ipv6, 'bytes', ['name', 'log'])
                yield filter_nat_metrics_ipv6

            filter_mangle_records_ipv6 = FirewallMetricsDataSource.metric_records(router_entry, metric_labels = firewall_labels, filter_path='mangle', ipv6=True)
            if filter_mangle_records_ipv6:
                metrics_records_ipv6 = [FirewallCollector.metric_record(router_entry, record) for record in filter_mangle_records_ipv6]
                filter_mangle_metrics_ipv6 = BaseCollector.counter_collector('firewall_mangle_ipv6', 'Total amount of bytes matched by Mangle rules (IPv6)', metrics_records_ipv6, 'bytes', ['name', 'log'])
                yield filter_mangle_metrics_ipv6

    # Helpers
    @staticmethod
    def metric_record(router_entry, firewall_record):
        name = f"| {firewall_record.get('chain', ' ')} | {firewall_record.get('action', ' ')} | {firewall_record.get('comment', ' ')}"
        bytes = firewall_record.get('bytes', 0)
        out_interface = firewall_record.get('out_interface')
        protocol = firewall_record.get('protocol')
        if out_interface:
            name = f"{name} | {out_interface}"
        if protocol:
            name = f"{name} | {protocol}"
        return {MKTXPConfigKeys.ROUTERBOARD_NAME: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_NAME],
                MKTXPConfigKeys.ROUTERBOARD_ADDRESS: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_ADDRESS],
                'name': name, 'log': firewall_record['log'], 'bytes': bytes}
