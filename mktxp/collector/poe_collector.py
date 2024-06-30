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
            poe_info_labels = ['name', 'poe_out', 'poe_priority', 'poe_voltage', 'poe_out_status']
            poe_metrics = BaseCollector.info_collector('poe', 'POE Info Metrics', poe_records, poe_info_labels)
            yield poe_metrics

            for poe_record in poe_records:
                if 'poe_out_voltage' in poe_record:
                    poe_voltage_metrics = BaseCollector.gauge_collector('poe_out_voltage', 'POE Out Voltage', [poe_record, ], 'poe_out_voltage', ['name'])
                    yield poe_voltage_metrics

                if 'poe_out_current' in poe_record:
                    poe_current_metrics = BaseCollector.gauge_collector('poe_out_current', 'POE Out Current', [poe_record, ], 'poe_out_current', ['name'])
                    yield poe_current_metrics

                if 'poe_out_power' in poe_record:
                    poe_power_metrics = BaseCollector.gauge_collector('poe_out_power', 'POE Out Power', [poe_record, ], 'poe_out_power', ['name'])
                    yield poe_power_metrics

