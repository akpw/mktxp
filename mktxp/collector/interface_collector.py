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
            
        interface_traffic_labels = ['name', 'comment', 'rx_byte', 'tx_byte', 'rx_packet', 'tx_packet', 'rx_error', 'tx_error', 'rx_drop', 'tx_drop']
        interface_traffic_records = InterfaceTrafficMetricsDataSource.metric_records(router_entry, metric_labels = interface_traffic_labels)   

        if interface_traffic_records:
            for interface_traffic_record in interface_traffic_records:
                if interface_traffic_record.get('comment'):
                    interface_traffic_record['name'] = interface_traffic_record['comment'] if router_entry.config_entry.use_comments_over_names \
                                                                                else f"{interface_traffic_record['name']} ({interface_traffic_record['comment']})"

            rx_byte_metric = BaseCollector.counter_collector('interface_rx_byte', 'Number of received bytes', interface_traffic_records, 'rx_byte', ['name'])
            yield rx_byte_metric

            tx_byte_metric = BaseCollector.counter_collector('interface_tx_byte', 'Number of transmitted bytes', interface_traffic_records, 'tx_byte', ['name'])
            yield tx_byte_metric

            rx_packet_metric = BaseCollector.counter_collector('interface_rx_packet', 'Number of packets received', interface_traffic_records, 'rx_packet', ['name'])
            yield rx_packet_metric

            tx_packet_metric = BaseCollector.counter_collector('interface_tx_packet', 'Number of transmitted packets', interface_traffic_records, 'tx_packet', ['name'])
            yield tx_packet_metric

            rx_error_metric = BaseCollector.counter_collector('interface_rx_error', 'Number of packets received with an error', interface_traffic_records, 'rx_error', ['name'])
            yield rx_error_metric

            tx_error_metric = BaseCollector.counter_collector('interface_tx_error', 'Number of packets transmitted with an error', interface_traffic_records, 'tx_error', ['name'])
            yield tx_error_metric

            rx_drop_metric = BaseCollector.counter_collector('interface_rx_drop', 'Number of received packets being dropped', interface_traffic_records, 'rx_drop', ['name'])
            yield rx_drop_metric

            tx_drop_metric = BaseCollector.counter_collector('interface_tx_drop', 'Number of transmitted packets being dropped', interface_traffic_records, 'tx_drop', ['name'])
            yield tx_drop_metric
