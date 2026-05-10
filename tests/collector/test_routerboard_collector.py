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

from mktxp.collector.routerboard_collector import RouterboardCollector


def test_routerboard_collector_yields_inventory_and_upgrade_metrics():
    mock_router_entry = Mock()
    mock_router_entry.config_entry.routerboard = True

    mock_records = [{
        'routerboard': 'true',
        'model': 'RB5009',
        'serial_number': 'ABC123',
        'firmware_type': 'routerboot',
        'factory_firmware': '7.12',
        'current_firmware': '7.14',
        'upgrade_firmware': '7.16',
    }]

    with patch('mktxp.collector.routerboard_collector.RouterboardMetricsDataSource.metric_records') as mock_ds, \
         patch('mktxp.collector.base_collector.BaseCollector.info_collector') as mock_info, \
         patch('mktxp.collector.base_collector.BaseCollector.gauge_collector') as mock_gauge:
        mock_ds.return_value = mock_records
        mock_info.return_value = 'routerboard-info'
        mock_gauge.return_value = 'routerboard-upgrade'

        results = list(RouterboardCollector.collect(mock_router_entry))

    mock_ds.assert_called_once_with(
        mock_router_entry,
        metric_labels=[
            'routerboard',
            'model',
            'serial_number',
            'firmware_type',
            'factory_firmware',
            'current_firmware',
            'upgrade_firmware',
        ]
    )
    assert mock_records[0]['firmware_upgrade_available'] == 1
    assert results == ['routerboard-info', 'routerboard-upgrade']


def test_routerboard_collector_skips_when_disabled():
    mock_router_entry = Mock()
    mock_router_entry.config_entry.routerboard = False

    with patch('mktxp.collector.routerboard_collector.RouterboardMetricsDataSource.metric_records') as mock_ds:
        results = list(RouterboardCollector.collect(mock_router_entry))

    mock_ds.assert_not_called()
    assert results == []
