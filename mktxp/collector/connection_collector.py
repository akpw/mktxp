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
from mktxp.datasource.connection_ds import IPConnectionDatasource


class IPConnectionCollector(BaseCollector):
    ''' IP Connection Metrics collector
    '''    
    @staticmethod
    def collect(router_entry):
        if not router_entry.config_entry.connections:
           return
           
        connection_records = IPConnectionDatasource.metric_records(router_entry)
        if connection_records:

            connection_metrics = BaseCollector.gauge_collector('ip_connections_total', 'Number of IP connections', connection_records, 'count',)
            yield connection_metrics
