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
from mktxp.datasource.interface_ds import InterfaceMonitorMetricsDataSource
from mktxp.utils.utils import parse_mkt_uptime


class LTECollector(BaseCollector):
    ''' LTE Metrics collector
    '''
    @staticmethod
    def collect(router_entry):
        if not router_entry.config_entry.lte:
            return

        monitor_labels = ['pin_status', 'registration_status', 'functionality', 'current_operator', 'access_technology', 'session_uptime', 'subscriber_number', 'rsrp', 'rsrq']
        translation_table = {
                'pin_status': lambda value: '1' if value=='ok' else '0',
                'registration_status': lambda value: '1' if value=='registered' else '0',
                'session_uptime': lambda value:  parse_mkt_uptime(value)
                }
        monitor_records = InterfaceMonitorMetricsDataSource.metric_records(router_entry,
                                                                           translation_table=translation_table,
                                                                           kind = 'lte',
                                                                           running_only = False)
        if monitor_records:
            yield BaseCollector.gauge_collector('lte_pin_status', 'Pin status', monitor_records, 'pin_status', [])
            yield BaseCollector.gauge_collector('lte_registration_status', 'Registration status', monitor_records, 'registration_status', [])
            yield BaseCollector.info_collector('lte_current_operator', 'LTE operator', monitor_records, ['current_operator', 'access_technology', 'functionality', 'subscriber_number'])
            yield BaseCollector.gauge_collector('lte_session_uptime', 'LTE session uptime', monitor_records, 'session_uptime', [])

            # specific labels
            rsrp_records = [monitor_record for monitor_record in monitor_records if monitor_record.get('rsrp')]
            rsrq_records = [monitor_record for monitor_record in monitor_records if monitor_record.get('rsrq')]
            sinr_records = [monitor_record for monitor_record in monitor_records if monitor_record.get('sinr')]
            rssi_records = [monitor_record for monitor_record in monitor_records if monitor_record.get('rssi')]

            if rsrp_records:
                yield BaseCollector.gauge_collector('lte_rsrp', 'LTE Reference Signal Received Qualityrsrp value', rsrp_records, 'rsrp', [])
            if rsrq_records:
                yield BaseCollector.gauge_collector('lte_rsrq', 'LTE Referenz Signal Received Power value', rsrq_records, 'rsrq', [])
            if sinr_records:
                yield BaseCollector.gauge_collector('lte_sinr', 'LTE signal to noise ratio value', sinr_records, 'sinr', [])
            if rssi_records:
                yield BaseCollector.gauge_collector('lte_rssi', 'Received Signal Strength Indicator', rssi_records, 'rssi', [])
