# coding=utf8
## Copyright (c) 2024 Arseniy Kuznetsov
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
from mktxp.datasource.interface_ds import InterfaceMetricsDataSource
from mktxp.utils.utils import parse_mkt_uptime


class IPIPCollector(BaseCollector):
    """ IPIP Metrics collector
    """
    @staticmethod
    def collect(router_entry):
        if not router_entry.config_entry.ipip:
            return

        default_labels = ['name', 'local_address', 'remote_address']
        interface_records = InterfaceMetricsDataSource.metric_records(
            router_entry,
            kind='ipip',
            additional_proplist=['mtu', 'actual-mtu', 'local-address', 'remote-address'],
        )

        if interface_records:
            yield BaseCollector.gauge_collector(
                'interface_mtu',
                'Current used MTU for this interface',
                interface_records,
                metric_key='actual_mtu',
                metric_labels=default_labels + ['mtu']
            )
