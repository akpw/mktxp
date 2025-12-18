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
from mktxp.flow.processor.output import BaseOutputProcessor


class NetwatchMetricsDataSource:
    ''' Netwatch Metrics data provider
    '''             
    @staticmethod
    def metric_records(router_entry, *, metric_labels=None, translation_table=None):
        if metric_labels is None:
            metric_labels = []                
        try:
            netwatch_records = router_entry.api_connection.router_api().get_resource('/tool/netwatch').get()
            netwatch_records = [entry for entry in netwatch_records if entry.get('disabled', 'false') != 'true']

            # since addition in ROS v7.14, name is supported natively
            for netwatch_record in netwatch_records:
                # Determine the primary identifier: use 'name' if set, fallback to 'host'
                name = netwatch_record.get('name') or netwatch_record.get('host')
                comment = netwatch_record.get('comment')

                # Apply the centralized formatting
                netwatch_record['name'] = BaseOutputProcessor.format_interface_name(
                    name,
                    comment,
                    router_entry.config_entry.interface_name_format
                )
            return BaseDSProcessor.trimmed_records(router_entry, router_records = netwatch_records, translation_table = translation_table, metric_labels = metric_labels)
        except Exception as exc:
            print(f'Error getting Netwatch info from router {router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None
