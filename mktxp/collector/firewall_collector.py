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
        if not router_entry.config_entry.firewall:
            return

        # initialize all pool counts, including those currently not used
        firewall_labels = ['chain', 'action', 'bytes', 'comment', 'log']
        
        firewall_filter_records = FirewallMetricsDataSource.metric_records(router_entry, metric_labels = firewall_labels)   
        if firewall_filter_records:           
            metris_records = [FirewallCollector.metric_record(router_entry, record) for record in firewall_filter_records]
            firewall_filter_metrics = BaseCollector.counter_collector('firewall_filter', 'Total amount of bytes matched by firewall rules', metris_records, 'bytes', ['name', 'log'])
            yield firewall_filter_metrics

        firewall_raw_records = FirewallMetricsDataSource.metric_records(router_entry, metric_labels = firewall_labels, raw = True)        
        if firewall_raw_records:      
            metris_records = [FirewallCollector.metric_record(router_entry, record) for record in firewall_raw_records]     
            firewall_raw_metrics = BaseCollector.counter_collector('firewall_raw', 'Total amount of bytes matched by raw firewall rules', metris_records, 'bytes', ['name', 'log'])
            yield firewall_raw_metrics

    # Helpers
    @staticmethod
    def metric_record(router_entry, firewall_record):
        name = f"| {firewall_record['chain']} | {firewall_record['action']} | {firewall_record['comment']}"
        bytes = firewall_record['bytes']
        return {MKTXPConfigKeys.ROUTERBOARD_NAME: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_NAME],
                MKTXPConfigKeys.ROUTERBOARD_ADDRESS: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_ADDRESS],
                'name': name, 'log': firewall_record['log'], 'bytes': bytes}
