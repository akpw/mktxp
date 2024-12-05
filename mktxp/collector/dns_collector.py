# coding=utf8
# Copyright (c) 2020 Arseniy Kuznetsov
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.


from mktxp.cli.config.config import MKTXPConfigKeys
from mktxp.collector.base_collector import BaseCollector
from mktxp.datasource.dns_ds import DNSDataSource


class DNSCollector(BaseCollector):
    '''Dns Collector'''

    @staticmethod
    def collect(router_entry):
        allowed_properties = {'cache_size', 'cache_used'}
        if not router_entry.config_entry.dns:
            return

        record = DNSDataSource.metric_records(router_entry)

        if not record:
            return

        keys = list(record.keys())
        metrics = []

        for key in keys:
            if key not in allowed_properties:
                continue

            metric_record = {
                MKTXPConfigKeys.ROUTERBOARD_NAME: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_NAME],
                MKTXPConfigKeys.ROUTERBOARD_ADDRESS: router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_ADDRESS],
                'property': key,
                'value': int(record[key]) * 1024
            }
            metrics.append(metric_record)

        yield BaseCollector.gauge_collector(
            'dns_info',
            'DNS info',
            metrics,
            'value',
            metric_labels=['property']
        )
