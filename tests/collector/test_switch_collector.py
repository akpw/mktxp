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
from mktxp.collector.switch_collector import SwitchPortCollector


class TestSwitchDropMetrics:
    @patch('mktxp.collector.switch_collector.SwitchPortMetricsDataSource.metric_records')
    def test_collects_rx_tx_drop(self, mock_metric_records):
        mock_router_entry = Mock()
        mock_router_entry.config_entry.switch_port = True
        mock_metric_records.return_value = [
            {
                'name': 'ether1',
                'driver_rx_byte': '1',
                'driver_rx_packet': '1',
                'driver_tx_byte': '1',
                'driver_tx_packet': '1',
                'rx_bytes': '1',
                'rx_broadcast': '1',
                'rx_pause': '1',
                'rx_multicast': '1',
                'rx_fcs_error': '1',
                'rx_align_error': '1',
                'rx_fragment': '1',
                'rx_overflow': '1',
                'tx_bytes': '1',
                'tx_broadcast': '1',
                'tx_pause': '1',
                'tx_multicast': '1',
                'tx_underrun': '1',
                'tx_collision': '1',
                'tx_deferred': '1',
                'rx_drop': '7',
                'tx_drop': '3',
            }
        ]

        metrics = list(SwitchPortCollector.collect(mock_router_entry))
        metrics_by_name = {metric.name: metric for metric in metrics}

        assert 'mktxp_switch_rx_drop' in metrics_by_name
        assert 'mktxp_switch_tx_drop' in metrics_by_name

        rx_samples = [sample for sample in metrics_by_name['mktxp_switch_rx_drop'].samples if sample.name.endswith('_total')]
        tx_samples = [sample for sample in metrics_by_name['mktxp_switch_tx_drop'].samples if sample.name.endswith('_total')]

        assert any(sample.labels['name'] == 'ether1' and float(sample.value) == 7 for sample in rx_samples)
        assert any(sample.labels['name'] == 'ether1' and float(sample.value) == 3 for sample in tx_samples)

        called_labels = mock_metric_records.call_args.kwargs['metric_labels']
        assert 'rx_drop' in called_labels
        assert 'tx_drop' in called_labels
