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

    def test_crs309_switch_chip_drops_use_packet_counter_without_fabricated_zeros(self):
        router_entry = Mock()
        router_entry.router_id = {
            'routerboard_name': 'core-sw-02',
            'routerboard_address': '10.10.200.52',
        }
        router_entry.config_entry.switch_port = True
        router_entry.config_entry.custom_labels = None
        resource = router_entry.api_connection.router_api().get_resource.return_value
        resource.call.return_value = [
            {'name': 'ether1', 'tx-drop-packet': '1216', 'tx-drop-byte': '8300000'},
            {'name': 'sfp-sfpplus1', 'tx-drop': '3'},
            {'name': 'sfp-sfpplus2'},
        ]

        metrics = {metric.name: metric for metric in SwitchPortCollector.collect(router_entry)}
        packets = metrics['mktxp_switch_tx_drop'].samples
        bytes_dropped = metrics['mktxp_switch_tx_drop_byte'].samples

        assert {(sample.labels['name'], int(sample.value)) for sample in packets} == {
            ('ether1', 1216), ('sfp-sfpplus1', 3),
        }
        assert {(sample.labels['name'], int(sample.value)) for sample in bytes_dropped} == {
            ('ether1', 8300000),
        }
        resource.call.assert_called_once_with('print', {'stats': 'detail'})

    @patch('mktxp.collector.switch_collector.SwitchPortMetricsDataSource.metric_records')
    def test_crs309_cpu_lane_drop_counts_are_summed(self, mock_metric_records):
        router_entry = Mock()
        router_entry.config_entry.switch_port = True
        mock_metric_records.return_value = [
            {'name': 'switch1-cpu', 'tx_drop_packet': '2,3', 'tx_drop_byte': '600,900'},
        ]

        metrics = {metric.name: metric for metric in SwitchPortCollector.collect(router_entry)}
        assert float(metrics['mktxp_switch_tx_drop'].samples[0].value) == 5
        assert float(metrics['mktxp_switch_tx_drop_byte'].samples[0].value) == 1500
