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
from mktxp.datasource.switch_ds import SwitchPortMetricsDataSource


class SwitchPortCollector(BaseCollector):
    '''Switch Port collector'''
    @staticmethod
    def collect(router_entry):
        if not router_entry.config_entry.switch_port:
            return

        switch_port_labels = ['name', 'driver_rx_byte', 'driver_rx_packet', 'driver_tx_byte',  'driver_tx_packet', 
                              'rx_bytes', 'rx_broadcast', 'rx_pause', 'rx_multicast', 'rx_fcs_error', 'rx_align_error', 'rx_fragment', 'rx_overflow', 
                              'tx_bytes', 'tx_broadcast', 'tx_pause', 'tx_multicast', 'tx_underrun', 'tx_collision', 'tx_deferred']

        switch_port_records = SwitchPortMetricsDataSource.metric_records(router_entry, metric_labels = switch_port_labels)
        if switch_port_records:
            for record in switch_port_records:
                for field in switch_port_labels[1:]:
                    if field in record and ',' in record[field]: # https://help.mikrotik.com/docs/display/ROS/Switch+Chip+Features#SwitchChipFeatures-Statistics
                        # Sum each CPU lane for the total
                        record[field] = str(sum([int(count) for count in record[field].split(",")]))
            yield BaseCollector.counter_collector('switch_driver_rx_byte', 'Total count of received bytes', switch_port_records, 'driver_rx_byte', ['name'])
            yield BaseCollector.counter_collector('switch_driver_rx_packet', 'Total count of received packets', switch_port_records, 'driver_rx_packet', ['name'])
            yield BaseCollector.counter_collector('switch_driver_tx_byte', 'Total count of transmitted bytes', switch_port_records, 'driver_tx_byte', ['name'])
            yield BaseCollector.counter_collector('switch_driver_tx_packet', 'Total count of transmitted packets', switch_port_records, 'driver_tx_packet', ['name'])
            yield BaseCollector.counter_collector('switch_rx_bytes', 'Total count of received bytes', switch_port_records, 'rx_bytes', ['name'])
            yield BaseCollector.counter_collector('switch_rx_broadcast', 'Total count of received broadcast frames', switch_port_records, 'rx_broadcast', ['name'])
            yield BaseCollector.counter_collector('switch_rx_pause', 'Total count of received pause frames', switch_port_records, 'rx_pause', ['name'])
            yield BaseCollector.counter_collector('switch_rx_multicast', 'Total count of received multicast frames', switch_port_records, 'rx_multicast', ['name'])
            yield BaseCollector.counter_collector('switch_rx_fcs_error', 'Total count of received frames with incorrect checksum', switch_port_records, 'rx_fcs_error', ['name'])
            yield BaseCollector.counter_collector('switch_rx_align_error', 'Total count of received align error event', switch_port_records, 'rx_align_error', ['name'])
            yield BaseCollector.counter_collector('switch_rx_fragment', 'Total count of received fragmented frames', switch_port_records, 'rx_fragment', ['name'])
            yield BaseCollector.counter_collector('switch_rx_overflow', 'Total count of received overflowed frames', switch_port_records, 'rx_overflow', ['name'])
            yield BaseCollector.counter_collector('switch_tx_bytes', 'Total count of transmitted bytes', switch_port_records, 'tx_bytes', ['name'])
            yield BaseCollector.counter_collector('switch_tx_broadcast', 'Total count of transmitted broadcast frames', switch_port_records, 'tx_broadcast', ['name'])
            yield BaseCollector.counter_collector('switch_tx_pause', 'Total count of transmitted pause frames', switch_port_records, 'tx_pause', ['name'])
            yield BaseCollector.counter_collector('switch_tx_multicast', 'Total count of transmitted multicast frames', switch_port_records, 'tx_multicast', ['name'])
            yield BaseCollector.counter_collector('switch_tx_underrun', 'Total count of transmitted underrun packets', switch_port_records, 'tx_underrun', ['name'])
            yield BaseCollector.counter_collector('switch_tx_collision', 'Total count of transmitted frames that made collisions', switch_port_records, 'tx_collision', ['name'])
            yield BaseCollector.counter_collector('switch_tx_deferred', 'Total count of transmitted frames that were delayed on its first transmit attempt', switch_port_records, 'tx_deferred', ['name'])
