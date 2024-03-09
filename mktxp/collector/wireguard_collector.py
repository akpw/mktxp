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
from mktxp.datasource.wireguard_ds import WireguardMetricsDataSource, WireguardPeerMetricsDataSource
from mktxp.flow.processor.output import BaseOutputProcessor


class WireguardCollector(BaseCollector):
    '''Wireguard collector'''
    @staticmethod
    def collect(router_entry):
        if not router_entry.config_entry.wireguard:
            return

        wg_interface_labels = ['id', 'name', 'mtu', 'listen_port', 'public_key', 'comment', 'running']
        wg_interface_records = WireguardMetricsDataSource.metric_records(router_entry, metric_labels=wg_interface_labels)
        if wg_interface_records:
            wg_interface_metrics = BaseCollector.info_collector('wireguard_interfaces', 'Wireguard Interfaces', wg_interface_records, wg_interface_labels)
            yield wg_interface_metrics

        if wg_interface_records:
            if router_entry.config_entry.wireguard_peers:
                wg_peer_info_labels = ['id', 'name', 'interface', 'public_key', 'endpoint_address', 'endpoint_port', 'current_endpoint_address', 'current_endpoint_port', 'allowed_address', 'comment']
                wg_peer_values = ['tx', 'rx', 'last_handshake']
                wg_peer_records = WireguardPeerMetricsDataSource.metric_records(router_entry, metric_labels = wg_peer_info_labels + wg_peer_values)

                peer_info = BaseCollector.info_collector('wireguard_peer', 'Wireguard Peer Info', wg_peer_records, wg_peer_info_labels)
                yield peer_info

                wg_peer_labels = ['id', 'interface', 'name', 'comment']
                last_handshake_metrics = BaseCollector.gauge_collector('wireguard_peer_last_handshake', 'Wireguard Peer Last Handshake', wg_peer_records, 'last_handshake', wg_peer_labels)
                yield last_handshake_metrics

                tx_byte_metrics = BaseCollector.counter_collector('wireguard_peer_tx_bytes', 'Wireguard Peer TX Bytes', wg_peer_records, 'tx', wg_peer_labels)
                yield tx_byte_metrics
                rx_byte_metrics = BaseCollector.counter_collector('wireguard_peer_rx_bytes', 'Wireguard Peer RX Bytes', wg_peer_records, 'rx', wg_peer_labels)
                yield rx_byte_metrics
