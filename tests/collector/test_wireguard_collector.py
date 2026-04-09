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

from unittest.mock import Mock, patch

from mktxp.collector.wireguard_collector import WireGuardPeerCollector


def test_wireguard_collector_yields_metrics_when_enabled():
    mock_router_entry = Mock()
    mock_router_entry.config_entry.wireguard_peers = True

    mock_records = [
        {
            'name': 'peer-a',
            'interface': 'wg0',
            'comment': 'peer a',
            'current_endpoint_address': '1.2.3.4',
            'current_endpoint_port': '51820',
            'allowed_address': '10.0.0.2/32',
            'disabled': '0',
            'rx': '123',
            'tx': '456',
            'last_handshake': 30,
        }
    ]

    with patch('mktxp.collector.wireguard_collector.WireguardPeerTrafficMetricsDataSource.metric_records') as mock_ds, \
         patch('mktxp.collector.base_collector.BaseCollector.gauge_collector') as mock_gauge, \
         patch('mktxp.collector.base_collector.BaseCollector.counter_collector') as mock_counter:
        mock_ds.return_value = mock_records
        mock_gauge.side_effect = ['disabled-metric', 'handshake-metric']
        mock_counter.side_effect = ['rx-metric', 'tx-metric']

        results = list(WireGuardPeerCollector.collect(mock_router_entry))

    mock_ds.assert_called_once()
    assert results == ['disabled-metric', 'rx-metric', 'tx-metric', 'handshake-metric']


def test_wireguard_collector_skips_when_disabled():
    mock_router_entry = Mock()
    mock_router_entry.config_entry.wireguard_peers = False

    with patch('mktxp.collector.wireguard_collector.WireguardPeerTrafficMetricsDataSource.metric_records') as mock_ds:
        results = list(WireGuardPeerCollector.collect(mock_router_entry))

    mock_ds.assert_not_called()
    assert results == []
