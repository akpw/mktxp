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
from mktxp.datasource.interface_ds import InterfaceTrafficMetricsDataSource


class InterfaceCollector(BaseCollector):
    ''' Router Interface Metrics collector
    '''        
    @staticmethod
    def collect(router_entry):
        if not router_entry.config_entry.interface:
            return

        interface_traffic_labels = ['disabled', 'name', 'comment', 'rx_byte', 'tx_byte', 'rx_packet', 'tx_packet',
                                    'rx_error', 'tx_error', 'rx_drop', 'tx_drop', 'link_downs', 'running', 'type']
        interface_traffic_translation_table = {
            'running': lambda value: '1' if value == 'true' else '0',
            'disabled': lambda value: '1' if value == 'true' else '0'
        }

        interface_traffic_records = InterfaceTrafficMetricsDataSource.metric_records(
            router_entry,
            metric_labels=interface_traffic_labels,
            translation_table=interface_traffic_translation_table,
        )

        if not interface_traffic_records:
            return

        yield BaseCollector.info_collector(
            'interface_comment',
            'The interface comment',
            interface_traffic_records,
            metric_labels=['name', 'comment']
        )

        yield BaseCollector.info_collector(
            'interface_type',
            'Interface type like ether, vrrp, eoip, gre-tunnel, ...',
            interface_traffic_records,
            metric_labels=['name', 'type']
        )

        yield BaseCollector.gauge_collector(
            'interface_running',
            'Current running status of the interface',
            interface_traffic_records,
            metric_key='running',
            metric_labels=['name']
        )

        yield BaseCollector.gauge_collector(
            'interface_disabled',
            'Current disabled status of the interface',
            interface_traffic_records,
            metric_key='disabled',
            metric_labels=['name']
        )

        yield BaseCollector.counter_collector(
            'interface_rx_byte',
            'Number of received bytes',
            interface_traffic_records,
            'rx_byte',
            ['name']
        )

        yield BaseCollector.counter_collector(
            'interface_tx_byte',
            'Number of transmitted bytes',
            interface_traffic_records,
            'tx_byte',
            ['name']
        )

        yield BaseCollector.counter_collector(
            'interface_rx_packet',
            'Number of packets received',
            interface_traffic_records,
            'rx_packet',
            ['name']
        )

        yield BaseCollector.counter_collector(
            'interface_tx_packet',
            'Number of transmitted packets',
            interface_traffic_records,
            'tx_packet',
            ['name']
        )

        yield BaseCollector.counter_collector(
            'interface_rx_error',
            'Number of packets received with an error',
            interface_traffic_records,
            'rx_error',
            ['name']
        )

        yield BaseCollector.counter_collector(
            'interface_tx_error',
            'Number of packets transmitted with an error',
            interface_traffic_records,
            'tx_error',
            ['name']
        )

        yield BaseCollector.counter_collector(
            'interface_rx_drop',
            'Number of received packets being dropped',
            interface_traffic_records,
            'rx_drop',
            ['name']
        )

        yield BaseCollector.counter_collector(
            'interface_tx_drop',
            'Number of transmitted packets being dropped',
            interface_traffic_records,
            'tx_drop',
            ['name']
        )

        yield BaseCollector.counter_collector(
            'link_downs',
            'Number of times link went down',
            interface_traffic_records,
            'link_downs',
            ['name']
        )
