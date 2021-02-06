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
from mktxp.datasource.identity_ds import IdentityMetricsDataSource


class IdentityCollector(BaseCollector):
    ''' System Identity Metrics collector
    '''     
    @staticmethod
    def collect(router_entry):
        identity_labels = ['name']
        identity_records = IdentityMetricsDataSource.metric_records(router_entry, metric_labels = identity_labels)                
        if identity_records:
            identity_metrics = BaseCollector.info_collector('system_identity', 'System identity', identity_records, identity_labels)
            yield identity_metrics

