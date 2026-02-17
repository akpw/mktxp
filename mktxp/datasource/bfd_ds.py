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


from mktxp.datasource.base_ds import BaseDSProcessor
from mktxp.datasource.system_resource_ds import SystemResourceMetricsDataSource
from mktxp.utils.utils import routerOS7_version


class BFDMetricsDataSource:
    """Bidirectional Forwarding Detection (BFD) data provider"""
    @staticmethod
    def metric_records(router_entry, *, metric_labels=None, translation_table=None):
        if metric_labels is None:
            metric_labels = []
        try:
            bfd_routing_path = "/routing/bfd/session"

            is_ros7 = routerOS7_version(SystemResourceMetricsDataSource.os_version(router_entry))

            # legacy 6.x versions use a different path
            if not is_ros7:
                bfd_routing_path = "/routing/bfd/neighbor"

            bfd_records = router_entry.api_connection.router_api().get_resource(bfd_routing_path).get()

            if not is_ros7:
                # Normalize ROS 6 records to match ROS 7 keys
                for record in bfd_records:
                    if 'address' in record:
                        record['remote-address'] = record['address']
                    if 'interface' in record:
                        record['local-address'] = record['interface']

            return BaseDSProcessor.trimmed_records(
                router_entry,
                router_records=bfd_records,
                metric_labels=metric_labels,
                translation_table=translation_table
            )
        except Exception as exc:
            print(f"Error getting BFD sessions info from router {router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}")
            return None
