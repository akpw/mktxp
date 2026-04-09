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
from mktxp.datasource.wireguard_ds import WireguardPeerTrafficMetricsDataSource
from mktxp.utils.utils import parse_mkt_uptime


class WireGuardPeerCollector(BaseCollector):
    """ Router Interface Metrics collector
    """

    @staticmethod
    def collect(router_entry):
        if not router_entry.config_entry.wireguard_peers:
            return

        interface_traffic_labels = ['disabled', 'name', 'comment', 'rx', 'tx', 'interface', 'current_endpoint_address',
                                    'current_endpoint_port', 'allowed_address', 'last_handshake']
        interface_traffic_translation_table = {
            'disabled': lambda value: '1' if value == 'true' else '0',
            'last_handshake': parse_mkt_uptime,
        }

        interface_traffic_records = WireguardPeerTrafficMetricsDataSource.metric_records(
            router_entry,
            metric_labels=interface_traffic_labels,
            translation_table=interface_traffic_translation_table,
        )

        if not interface_traffic_records:
            return

        labels = [
            'name', 'interface', 'comment', 'current_endpoint_address',
            'current_endpoint_port', 'allowed_address'
        ]

        yield BaseCollector.gauge_collector(
            'peer_disabled',
            'Current disabled status of the interface',
            interface_traffic_records,
            metric_key='disabled',
            metric_labels=labels
        )

        yield BaseCollector.counter_collector(
            'peer_rx',
            'Number of received bytes',
            interface_traffic_records,
            'rx',
            labels
        )

        yield BaseCollector.counter_collector(
            'peer_tx',
            'Number of transmitted bytes',
            interface_traffic_records,
            'tx',
            labels
        )

        yield BaseCollector.gauge_collector(
            'last_handshake',
            'Time since last handshake with peer',
            interface_traffic_records,
            'last_handshake',
            labels
        )
