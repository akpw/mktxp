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

from unittest.mock import MagicMock, patch
from mktxp.collector.capsman_collector import CapsmanCollector

registration_records = [
    {'interface': 'cap1', 'ssid': 'Home', 'mac_address': 'AA:BB:CC:DD:EE:01', 'tx_rate': '866.6Mbps-80MHz/2S/SGI', 'rx_rate': '144.4Mbps',
     'rx_signal': '-61', 'uptime': '1d2h3m4s', 'bytes': '1000,2000', 'band': '5ghz-ac'},
    {'interface': 'cap1', 'ssid': 'Home', 'mac_address': 'AA:BB:CC:DD:EE:02', 'tx_rate': 'unknown', 'rx_rate': '6Mbps',
     'rx_signal': '-75', 'uptime': '45s', 'bytes': '10,20', 'band': '2ghz-n'},
]

VOLATILE_LABELS = {'uptime', 'rx_signal', 'tx_rate', 'rx_rate'}
CLIENT_GAUGE_LABELS = {'dhcp_name', 'mac_address', 'routerboard_name', 'routerboard_address'}


def _router_entry():
    router_entry = MagicMock()
    router_entry.dhcp_records = [{'mac_address': 'AA:BB:CC:DD:EE:01'}]
    router_entry.dhcp_record.return_value = {'host_name': 'Device1', 'address': '10.0.0.5'}
    router_entry.config_entry.interface_name_format = 'name'
    return router_entry


def _metrics_by_name(metrics):
    return {metric.name: metric for metric in metrics}


@patch('mktxp.collector.capsman_collector.CapsmanInterfacesDatasource.metric_records', return_value=None)
@patch('mktxp.collector.capsman_collector.CapsmanCapsMetricsDataSource.metric_records', return_value=None)
@patch('mktxp.collector.capsman_collector.CapsmanRegistrationsMetricsDataSource.metric_records')
def test_capsman_client_metrics(mock_registrations, mock_caps, mock_interfaces):
    mock_registrations.return_value = [dict(record) for record in registration_records]
    router_entry = _router_entry()
    router_entry.config_entry.capsman = True
    router_entry.config_entry.capsman_clients = True

    metrics = _metrics_by_name(CapsmanCollector.collect(router_entry))

    assert {'mktxp_capsman_clients_uptime_seconds', 'mktxp_capsman_clients_tx_rate_bps',
            'mktxp_capsman_clients_rx_rate_bps', 'mktxp_capsman_clients_signal_strength',
            'mktxp_capsman_clients_devices'} <= set(metrics)

    # info labels are stable identity only
    info = metrics['mktxp_capsman_clients_devices']
    assert len(info.samples) == 2
    for sample in info.samples:
        assert not VOLATILE_LABELS & set(sample.labels)
        assert {'dhcp_name', 'dhcp_address', 'ssid', 'interface', 'mac_address', 'band'} <= set(sample.labels)

    # volatile values are gauges keyed like the existing per-client gauges
    for name in ('mktxp_capsman_clients_uptime_seconds', 'mktxp_capsman_clients_tx_rate_bps', 'mktxp_capsman_clients_rx_rate_bps'):
        for sample in metrics[name].samples:
            assert set(sample.labels) == CLIENT_GAUGE_LABELS

    uptime = {s.labels['mac_address']: s.value for s in metrics['mktxp_capsman_clients_uptime_seconds'].samples}
    assert uptime == {'AA:BB:CC:DD:EE:01': 93784, 'AA:BB:CC:DD:EE:02': 45}

    rx_rate = {s.labels['mac_address']: s.value for s in metrics['mktxp_capsman_clients_rx_rate_bps'].samples}
    assert rx_rate == {'AA:BB:CC:DD:EE:01': 144400000, 'AA:BB:CC:DD:EE:02': 6000000}

    # the unparseable tx_rate sample is dropped, the rest of the collection is intact
    tx_rate = {s.labels['mac_address']: s.value for s in metrics['mktxp_capsman_clients_tx_rate_bps'].samples}
    assert tx_rate == {'AA:BB:CC:DD:EE:01': 866600000}
