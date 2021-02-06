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
from mktxp.datasource.mktxp_ds import MKTXPMetricsDataSource


class MKTXPCollector(BaseCollector):
    ''' System Identity Metrics collector
    '''     
    @staticmethod
    def collect(router_entry):
        mktxp_records = MKTXPMetricsDataSource.metric_records(router_entry)
        if mktxp_records:
            mktxp_duration_metric = BaseCollector.counter_collector('collection_time', 'Total time spent collecting metrics in milliseconds', mktxp_records, 'duration', ['name'])
            yield mktxp_duration_metric


