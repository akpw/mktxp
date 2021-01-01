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


class CapsmanCollector(BaseCollector):
    ''' CAPsMAN Metrics collector
    '''    
    @staticmethod
    def collect(router_metric):
        resource_labels = ['uptime', 'version', 'free-memory', 'total-memory', 
                           'cpu', 'cpu-count', 'cpu-frequency', 'cpu-load', 
                           'free-hdd-space', 'total-hdd-space', 
                           'architecture-name', 'board-name']
        resource_records = router_metric.resource_records(resource_labels)
        if not resource_records:
            return

        resource_metrics = BaseCollector.info_collector('resource', 'resource', resource_records, resource_labels)
        yield resource_metrics

