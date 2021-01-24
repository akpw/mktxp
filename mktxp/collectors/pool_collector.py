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

from mktxp.cli.config.config import MKTXPConfigKeys
from mktxp.collectors.base_collector import BaseCollector

class PoolCollector(BaseCollector):
    ''' IP Pool Metrics collector
    '''    
    @staticmethod
    def collect(router_metric):
        # initialize all pool counts, including those currently not used
        pool_records = router_metric.pool_records(['name'])
        if pool_records:
            pool_used_labels = ['pool']
            pool_used_counts = {pool_record['name']: 0 for pool_record in pool_records}

            # for pools in usage, calculate the current numbers
            pool_used_records = router_metric.pool_used_records(pool_used_labels)
            for pool_used_record in pool_used_records:
                pool_used_counts[pool_used_record['pool']] = pool_used_counts.get(pool_used_record['pool'], 0) + 1

           # compile used-per-pool records
            used_per_pool_records = [{ MKTXPConfigKeys.ROUTERBOARD_NAME: router_metric.router_id[MKTXPConfigKeys.ROUTERBOARD_NAME],
                                       MKTXPConfigKeys.ROUTERBOARD_ADDRESS: router_metric.router_id[MKTXPConfigKeys.ROUTERBOARD_ADDRESS],
                                       'pool': key, 'count': value} for key, value in pool_used_counts.items()]
            
            # yield used-per-pool metrics
            used_per_pool_metrics = BaseCollector.gauge_collector('ip_pool_used', 'Number of used addresses per IP pool', used_per_pool_records, 'count', ['pool'])
            yield used_per_pool_metrics
