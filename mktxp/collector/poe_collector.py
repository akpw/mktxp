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
from mktxp.datasource.poe_ds import POEMetricsDataSource


class POECollector(BaseCollector):
    ''' POE Metrics collector
    '''    
    @staticmethod
    def collect(router_entry):
        if not router_entry.config_entry.poe:
            return

        poe_labels = ['name', 'poe_out', 'poe_priority', 'poe_voltage', 'poe_out_status', 'poe_out_voltage', 'poe_out_current', 'poe_out_power']
        poe_records = POEMetricsDataSource.metric_records(router_entry, include_comments = True, metric_labels = poe_labels)  

        if poe_records:
            poe_metrics = BaseCollector.info_collector('poe', 'POE Metrics', poe_records, poe_labels)
            yield poe_metrics
            
