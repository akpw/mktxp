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

class BaseWireGuardPeerDataSource:
    @staticmethod
    def rewrite_interface_names(router_entry, metric_records):
        for metric_record in metric_records:
            if metric_record.get('comment'):
                metric_record['name'] = BaseOutputProcessor.format_interface_name(
                    metric_record['name'],
                    metric_record['comment'],
                    router_entry.config_entry.interface_name_format
                )

        return metric_records


class WireguardPeerTrafficMetricsDataSource(BaseWireGuardPeerDataSource):
    """ Wireguard Peer Traffic Metrics data provider
    """
    @staticmethod
    def metric_records(router_entry, *, metric_labels, translation_table=None):
        metric_labels = metric_labels or []
        try:
            # get stats for all existing interfaces
            metric_stats_records = router_entry.api_connection.router_api().get_resource(
                '/interface/wireguard/peers'
            ).call(
                'print'
            )
            metric_stats_records = BaseWireGuardPeerDataSource.rewrite_interface_names(router_entry, metric_stats_records)
            return BaseDSProcessor.trimmed_records(
                router_entry=router_entry,
                router_records=metric_stats_records,
                metric_labels=metric_labels,
                translation_table=translation_table,
            )
        except Exception as exc:
            print(f'Error getting interface traffic stats info from router {router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None

