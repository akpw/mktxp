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

from mktxp.collectors.base_collector import BaseCollector
from mktxp.router_metric import RouterMetric


class WLANCollector(BaseCollector):
    ''' Wireless Metrics collector
    '''    
    @staticmethod
    def collect(router_metric):
        monitor_labels = ['channel', 'noise_floor', 'overall_tx_ccq']
        monitor_records = router_metric.interface_monitor_records(monitor_labels, 'wireless')
        if not monitor_records:
            return

        # sanitize records for relevant labels
        noise_floor_records = [monitor_record for monitor_record in monitor_records if monitor_record.get('noise_floor')]
        tx_ccq_records = [monitor_record for monitor_record in monitor_records if monitor_record.get('overall_tx_ccq')]

        if noise_floor_records:
            noise_floor_metrics = BaseCollector.gauge_collector('wlan_noise_floor', 'Noise floor threshold', noise_floor_records, 'noise_floor', ['channel'])
            yield noise_floor_metrics

        if tx_ccq_records:
            overall_tx_ccq_metrics = BaseCollector.gauge_collector('wlan_overall_tx_ccq', ' Client Connection Quality for transmitting', tx_ccq_records, 'overall_tx_ccq', ['channel'])
            yield overall_tx_ccq_metrics
