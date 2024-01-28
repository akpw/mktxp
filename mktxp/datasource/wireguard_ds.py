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
from mktxp.utils.utils import parse_mkt_time_duration

class WireguardMetricsDataSource:
    ''' Wireguard Metrics data provider
    '''

    @staticmethod
    def metric_records(router_entry, *, metric_labels = None, add_router_id = True):
        if metric_labels is None:
            metric_labels = []
        try:
            wireguard_interface_records = router_entry.api_connection.router_api().get_resource(f'/interface/wireguard').get()
            return BaseDSProcessor.trimmed_records(router_entry, router_records = wireguard_interface_records, metric_labels = metric_labels)

        except Exception as exc:
            print(f'Error getting wireguard interface table info from router{router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None


class WireguardPeerMetricsDataSource:
    ''' Wireguard Peer Metrics data provider
    '''

    @staticmethod
    def metric_records(router_entry, *, metric_labels = None, add_router_id = True):
        if metric_labels is None:
            metric_labels = []
        try:
            wireguard_peer_records = router_entry.api_connection.router_api().get_resource(f'/interface/wireguard/peers').get(disabled='false')

            #translation rules
            translation_table = {
                'last_handshake': lambda c: parse_mkt_time_duration(c) if c else 0
            }

            return BaseDSProcessor.trimmed_records(router_entry, router_records = wireguard_peer_records, metric_labels = metric_labels, add_router_id = add_router_id, translation_table=translation_table)

        except Exception as exc:
            print(f'Error getting wireguard peer table from router{router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None
