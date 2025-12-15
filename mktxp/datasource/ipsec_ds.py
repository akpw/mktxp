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


class IPSecMetricsDataSource:
    """IPSec Metrics data provider"""
    @staticmethod
    def metric_records(router_entry, *, metric_labels=None, translation_table=None):
        if metric_labels is None:
            metric_labels = []

        try:
            ipsec_records = router_entry.api_connection.router_api().get_resource('/ip/ipsec/active-peers').call('print', {'stats': ''})
            for record in ipsec_records:
                # Format name with comment using centralized function
                if 'comment' in record:
                    record['name'] = BaseOutputProcessor.format_interface_name(
                        record['name'],
                        record['comment'],
                        router_entry.config_entry.interface_name_format
                    )

            return BaseDSProcessor.trimmed_records(router_entry, router_records=ipsec_records,
                                                   metric_labels=metric_labels, translation_table=translation_table)
        except Exception as exc:
            print(f'Error getting IPSec active-peers info from router {router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None
