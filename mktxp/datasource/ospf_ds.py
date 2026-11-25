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


class OSPFMetricsDataSource:
    """OSPF metrics data provider (compatible with RouterOS 6 and 7)."""

    @staticmethod
    def neighbor_records(router_entry, *, metric_labels=None, translation_table=None):
        if metric_labels is None:
            metric_labels = []
        try:
            ospf_records = (
                router_entry.api_connection.router_api()
                .get_resource('/routing/ospf/neighbor')
                .get()
            )
            return BaseDSProcessor.trimmed_records(
                router_entry,
                router_records=ospf_records,
                metric_labels=metric_labels,
                translation_table=translation_table,
            )
        except Exception as exc:
            print(
                f'Error getting OSPF neighbors info from router '
                f'{router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}'
            )
            return None

    @staticmethod
    def lsa_count(router_entry):
        try:
            count = BaseDSProcessor.count_records(
                router_entry,
                api_path='/routing/ospf/lsa',
            )
            if count is None:
                return None
            return BaseDSProcessor.trimmed_records(
                router_entry,
                router_records=[{'count': count}],
                metric_labels=['count'],
            )
        except Exception as exc:
            print(
                f'Error getting OSPF LSA count from router '
                f'{router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}'
            )
            return None
