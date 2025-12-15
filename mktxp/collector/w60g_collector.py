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
from mktxp.datasource.interface_ds import InterfaceMonitorMetricsDataSource


class W60gCollector(BaseCollector):
    """ W60G Interface Monitor Metrics collector
    """
    @staticmethod
    def collect(router_entry):
        if not router_entry.config_entry.w60g:
            return

        monitor_labels = [
            'baseband_temperature',
            'connected',
            'distance',
            'frequency',
            'name',
            'remote_address',
            'rf_temperature',
            'rssi',
            'signal',
            'tx_mcs',
            'tx_packet_error_rate',
            'tx_phy_rate',
            'tx_sector_info',
            'tx_sector',
        ]

        translation_table = {
            'connected': lambda value: '1' if value == 'true' else '0',
            'distance': lambda value: value.strip('m'),
            'name': lambda value: value if value else '',
            'tx_packet_error_rate': lambda value: value.strip('%')
        }
        monitor_records = InterfaceMonitorMetricsDataSource.metric_records(
            router_entry,
            metric_labels=monitor_labels,
            translation_table=translation_table,
            kind='w60g',
            running_only=False
        )

        if not monitor_records:
            return

        yield BaseCollector.gauge_collector(
            'w60g_baseband_temperature',
            'Baseband unit temperature',
            monitor_records,
            'baseband_temperature',
            ['name']
        )

        connected_records = [monitor_record for monitor_record in monitor_records if monitor_record.get('connected', None)]
        yield BaseCollector.gauge_collector(
            'w60g_connected',
            'Connected status',
            connected_records,
            'connected',
            ['name']
        )

        yield BaseCollector.gauge_collector(
            'w60g_distance',
            'Distance to W60G peer',
            monitor_records,
            'distance',
            ['name']
        )

        yield BaseCollector.gauge_collector(
            'w60g_frequency',
            'Frequency of W60G link',
            monitor_records,
            'frequency',
            ['name']
        )

        yield BaseCollector.info_collector(
            'w60g_remote_address',
            'MAC address of W60G peer',
            monitor_records,
            metric_labels=['name', 'remote_address']
        )

        yield BaseCollector.gauge_collector(
            'w60g_rf_temperature',
            'RF module temperature',
            monitor_records,
            'rf_temperature',
            ['name']
        )

        yield BaseCollector.gauge_collector(
            'w60g_rssi',
            'Link Received Signal Strength Indicator (RSSI)',
            monitor_records,
            'rssi',
            ['name']
        )

        yield BaseCollector.gauge_collector(
            'w60g_signal',
            'Link Signal Strength',
            monitor_records,
            'signal',
            ['name']
        )

        yield BaseCollector.gauge_collector(
            'w60g_tx_mcs',
            'Transmission MCS',
            monitor_records,
            'tx_mcs',
            ['name']
        )

        yield BaseCollector.gauge_collector(
            'w60g_tx_packet_error_rate',
            'Transmission error rate (percentage)',
            monitor_records,
            'tx_packet_error_rate',
            ['name']
        )

        rate_records = [monitor_record for monitor_record in monitor_records if monitor_record.get('tx_phy_rate', None)]
        yield BaseCollector.gauge_collector(
            'w60g_tx_phy_rate',
            'Transmission PHY rate',
            rate_records,
            'tx_phy_rate',
            ['name']
        )

        yield BaseCollector.info_collector(
            'w60g_tx_sector',
            'Transmission sector info (alignment)',
            monitor_records,
            metric_labels=['name','tx_sector_info']
        )

        yield BaseCollector.gauge_collector(
            'w60g_tx_sector',
            'Transmission sector number',
            monitor_records,
            'tx_sector',
            ['name']
        )
