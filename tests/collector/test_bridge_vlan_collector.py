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

from mktxp.collector.bridge_vlan_collector import BridgeVlanCollector


def test_bridge_vlan_collector_yields_metrics_when_enabled():
    mock_router_entry = Mock()
    mock_router_entry.config_entry.bridge_vlan = True

    mock_vlan_records = [
        {
            'name': 'bridge-local-vlan-10',
            'bridge': 'bridge-local',
            'vlan_ids': '10',
            'current_tagged': 'sfp1',
            'current_untagged': 'ether1'
        }
    ]

    with patch('mktxp.collector.bridge_vlan_collector.BridgeVlanMetricsDataSource.metric_records') as mock_ds, \
         patch('mktxp.collector.base_collector.BaseCollector.info_collector') as mock_info:
        mock_ds.return_value = mock_vlan_records
        mock_info.return_value = 'bridge-vlan-metric'

        results = list(BridgeVlanCollector.collect(mock_router_entry))

    mock_ds.assert_called_once_with(
        mock_router_entry,
        metric_labels=['name', 'bridge', 'vlan_ids', 'current_tagged', 'current_untagged']
    )
    assert results == ['bridge-vlan-metric']


def test_bridge_vlan_collector_skips_when_disabled():
    mock_router_entry = Mock()
    mock_router_entry.config_entry.bridge_vlan = False

    with patch('mktxp.collector.bridge_vlan_collector.BridgeVlanMetricsDataSource.metric_records') as mock_ds:
        results = list(BridgeVlanCollector.collect(mock_router_entry))

    mock_ds.assert_not_called()
    assert results == []
