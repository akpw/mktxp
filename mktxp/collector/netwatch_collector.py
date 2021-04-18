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
from mktxp.datasource.netwatch_ds import NetwatchMetricsDataSource


class NetwatchCollector(BaseCollector):
    ''' Netwatch Metrics collector
    '''    
    @staticmethod
    def collect(router_entry):
        if not router_entry.config_entry.netwatch:
            return

        netwatch_labels = ['host', 'timeout', 'interval', 'since', 'status', 'comment', 'name']
        netwatch_records = NetwatchMetricsDataSource.metric_records(router_entry, metric_labels = netwatch_labels)  

        if netwatch_records:
            yield BaseCollector.info_collector('netwatch', 'Netwatch Info Metrics', netwatch_records, netwatch_labels)

            yield BaseCollector.gauge_collector('netwatch_status', 'Netwatch Status Metrics', netwatch_records, 'status', ['name'])
            
