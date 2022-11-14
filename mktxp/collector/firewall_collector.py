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
        firewall_labels = ['chain', 'action', 'bytes', 'comment', 'log']

        if router_entry.config_entry.firewall:
            # ~*~*~*~*~*~ IPv4 ~*~*~*~*~*~
            firewall_filter_records = FirewallMetricsDataSource.metric_records_ipv4(router_entry, metric_labels = firewall_labels)   
            if firewall_filter_records:           
                metrics_records = [FirewallCollector.metric_record(router_entry, record) for record in firewall_filter_records]
                firewall_filter_metrics = BaseCollector.counter_collector('firewall_filter', 'Total amount of bytes matched by firewall rules', metrics_records, 'bytes', ['name', 'log'])
                yield firewall_filter_metrics

            firewall_raw_records = FirewallMetricsDataSource.metric_records_ipv4(router_entry, metric_labels = firewall_labels, raw = True)        
            if firewall_raw_records:      
                metrics_records = [FirewallCollector.metric_record(router_entry, record) for record in firewall_raw_records]     
                firewall_raw_metrics = BaseCollector.counter_collector('firewall_raw', 'Total amount of bytes matched by raw firewall rules', metrics_records, 'bytes', ['name', 'log'])
                yield firewall_raw_metrics

        # ~*~*~*~*~*~ IPv6 ~*~*~*~*~*~
        if router_entry.config_entry.ipv6_firewall:
            firewall_filter_records_ipv6 =  FirewallMetricsDataSource.metric_records_ipv6(router_entry, metric_labels = firewall_labels)
            if firewall_filter_records_ipv6:           
                metrics_records_ipv6 = [FirewallCollector.metric_record(router_entry, record) for record in firewall_filter_records_ipv6]
                firewall_filter_metrics_ipv6 = BaseCollector.counter_collector('firewall_filter_ipv6', 'Total amount of bytes matched by firewall rules (IPv6)', metrics_records_ipv6, 'bytes', ['name', 'log'])
                yield firewall_filter_metrics_ipv6

            firewall_raw_records_ipv6 = FirewallMetricsDataSource.metric_records_ipv6(router_entry, metric_labels = firewall_labels, raw = True)        
            if firewall_raw_records_ipv6:      
                metrics_records_ipv6 = [FirewallCollector.metric_record(router_entry, record) for record in firewall_raw_records_ipv6]     
                firewall_raw_metrics_ipv6 = BaseCollector.counter_collector('firewall_raw_ipv6', 'Total amount of bytes matched by raw firewall rules (IPv6)', metrics_records_ipv6, 'bytes', ['name', 'log'])
                yield firewall_raw_metrics_ipv6

    # Helpers
    @staticmethod
    def metric_record(router_entry, firewall_record):
        name = f"| {firewall_record['chain']} | {firewall_record['action']} | {firewall_record['comment']}"
        bytes = firewall_record['bytes']
        return {MKTXPConfigKeys.ROUTERBOARD_NAME: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_NAME],
                MKTXPConfigKeys.ROUTERBOARD_ADDRESS: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_ADDRESS],
                'name': name, 'log': firewall_record['log'], 'bytes': bytes}
