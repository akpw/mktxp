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


class MonitorCollector(BaseCollector):
    ''' Ethernet Interface Monitor Metrics collector
    '''    
    @staticmethod
    def collect(router_entry):
        if not router_entry.config_entry.monitor:
            return

        monitor_labels = ['status', 'rate', 'full_duplex', 'name', 'comment', 'sfp_temperature']
        monitor_records = InterfaceMonitorMetricsDataSource.metric_records(router_entry, metric_labels = monitor_labels, include_comments = True)   
        if monitor_records:
            monitor_status_metrics = BaseCollector.gauge_collector('interface_status', 'Current interface link status', monitor_records, 'status', ['name', 'comment'])
            yield monitor_status_metrics

            monitor_rates_metrics = BaseCollector.gauge_collector('interface_rate', 'Actual interface connection data rate', monitor_records, 'rate', ['name', 'comment'])
            yield monitor_rates_metrics

            monitor_rates_metrics = BaseCollector.gauge_collector('interface_full_duplex', 'Full duplex data transmission', monitor_records, 'full_duplex', ['name', 'comment'])
            yield monitor_rates_metrics

            sfp_temperature_metrics = BaseCollector.gauge_collector('interface_sfp_temperature', 'Current SFP temperature', monitor_records, 'sfp_temperature', ['name', 'comment'])
            yield sfp_temperature_metrics



