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
from mktxp.datasource.health_ds import HealthMetricsDataSource


class HealthCollector(BaseCollector):
    ''' System Health Metrics collector
    '''    
    @staticmethod
    def collect(router_entry):
        health_labels = ['voltage', 'temperature']
        health_records = HealthMetricsDataSource.metric_records(router_entry, metric_labels = health_labels)   
        if health_records:
            voltage_metrics = BaseCollector.gauge_collector('system_routerboard_voltage', 'Supplied routerboard voltage', health_records, 'voltage')
            yield voltage_metrics

            temperature_metrics = BaseCollector.gauge_collector('system_routerboard_temperature', ' Routerboard current temperature', health_records, 'temperature')
            yield temperature_metrics
