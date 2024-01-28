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

        interface_traffic_labels = ['name', 'comment']
        interface_traffic_values = ['rx_byte', 'tx_byte', 'rx_packet', 'tx_packet', 'rx_error', 'tx_error', 'rx_drop', 'tx_drop', 'link_downs']

        interface_traffic_records = InterfaceTrafficMetricsDataSource.metric_records(router_entry, metric_labels = interface_traffic_labels + interface_traffic_values)

        if interface_traffic_records:
            rx_byte_metric = BaseCollector.counter_collector('interface_rx_byte', 'Number of received bytes', interface_traffic_records, 'rx_byte', interface_traffic_labels)
            yield rx_byte_metric

            tx_byte_metric = BaseCollector.counter_collector('interface_tx_byte', 'Number of transmitted bytes', interface_traffic_records, 'tx_byte', interface_traffic_labels)
            yield tx_byte_metric

            rx_packet_metric = BaseCollector.counter_collector('interface_rx_packet', 'Number of packets received', interface_traffic_records, 'rx_packet', interface_traffic_labels)
            yield rx_packet_metric

            tx_packet_metric = BaseCollector.counter_collector('interface_tx_packet', 'Number of transmitted packets', interface_traffic_records, 'tx_packet', interface_traffic_labels)
            yield tx_packet_metric

            rx_error_metric = BaseCollector.counter_collector('interface_rx_error', 'Number of packets received with an error', interface_traffic_records, 'rx_error', interface_traffic_labels)
            yield rx_error_metric

            tx_error_metric = BaseCollector.counter_collector('interface_tx_error', 'Number of packets transmitted with an error', interface_traffic_records, 'tx_error', interface_traffic_labels)
            yield tx_error_metric

            rx_drop_metric = BaseCollector.counter_collector('interface_rx_drop', 'Number of received packets being dropped', interface_traffic_records, 'rx_drop', interface_traffic_labels)
            yield rx_drop_metric

            tx_drop_metric = BaseCollector.counter_collector('interface_tx_drop', 'Number of transmitted packets being dropped', interface_traffic_records, 'tx_drop', interface_traffic_labels)
            yield tx_drop_metric

            link_downs_metric = BaseCollector.counter_collector('link_downs', 'Number of times link went down', interface_traffic_records, 'link_downs', interface_traffic_labels)
            yield link_downs_metric
