# coding=utf8
# Copyright (c) 2020 Arseniy Kuznetsov
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import pytest
from unittest.mock import MagicMock, patch

from mktxp.collector.connection_collector import IPConnectionCollector
from mktxp.datasource.connection_ds import IPConnectionDatasource, IPConnectionStatsDatasource, IPConnectionTrafficDatasource
from mktxp.flow.router_entry import RouterEntry


def _build_mock_router_entry():
    mock_router_entry = MagicMock(spec=RouterEntry)
    mock_router_entry.router_name = "TestRouter"
    mock_router_entry.config_entry = MagicMock()
    mock_router_entry.config_entry.hostname = "testhost"
    mock_router_entry.config_entry.connections = False
    mock_router_entry.config_entry.connection_stats = False
    mock_router_entry.config_entry.connection_traffic = False
    mock_router_entry.api_connection = MagicMock()
    mock_router_entry.router_id = {'routerboard_name': 'test_router'}
    return mock_router_entry


def _configure_connection_api(mock_router_entry, *, ipv4_count = '0', ipv6_count = '0',
                              ipv4_records = None, ipv6_records = None, proplist = ''):
    mock_api = MagicMock()
    mock_router_entry.api_connection.router_api.return_value = mock_api

    if ipv4_records is None:
        ipv4_records = []
    if ipv6_records is None:
        ipv6_records = []

    def get_resource_side_effect(path):
        mock_resource = MagicMock()

        def call_side_effect(command, params):
            assert command == 'print'
            if params.get('count-only') == '':
                count_response = MagicMock()
                count_response.done_message = {'ret': ipv4_count if path == '/ip/firewall/connection/' else ipv6_count}
                return count_response

            assert params.get('proplist') == proplist
            return ipv4_records if path == '/ip/firewall/connection/' else ipv6_records

        mock_resource.call.side_effect = call_side_effect
        return mock_resource

    mock_api.get_resource.side_effect = get_resource_side_effect
    return mock_api


@pytest.mark.parametrize("ipv4_count, ipv6_count, should_make_stats_call", [
    ('0', '0', False),
    ('123', '0', True),
    ('0', '7', True),
])
def test_ip_connection_stats_datasource_checks_count_first(ipv4_count, ipv6_count, should_make_stats_call):
    """
    Verifies that IPConnectionStatsDatasource checks both IPv4 and IPv6 connection counters and
    avoids fetching the full stats list if both are empty.
    """
    mock_router_entry = _build_mock_router_entry()
    mock_api = _configure_connection_api(
        mock_router_entry,
        ipv4_count = ipv4_count,
        ipv6_count = ipv6_count,
        ipv4_records = [{'src-address': '1.1.1.1:123', 'src-port': '123', 'dst-address': '2.2.2.2:80', 'dst-port': '80', 'protocol': 'tcp'}],
        ipv6_records = [{'src-address': '[2001:db8::10]:5353', 'src-port': '5353', 'dst-address': '[2001:db8::20]:443', 'dst-port': '443', 'protocol': 'tcp'}],
        proplist = 'src-address,src-port,dst-address,dst-port,protocol'
    )

    result = IPConnectionStatsDatasource.metric_records(mock_router_entry)

    if should_make_stats_call:
        assert mock_api.get_resource.call_count == 4
        assert result is not None
        assert len(result) > 0
    else:
        assert mock_api.get_resource.call_count == 2
        assert result == []


def test_ip_connection_stats_datasource_supports_ipv4_and_ipv6():
    """
    Verifies that IPConnectionStatsDatasource keeps IPv6 addresses intact while still stripping
    transport ports from both IPv4 and IPv6 source addresses.
    """
    mock_router_entry = _build_mock_router_entry()
    _configure_connection_api(
        mock_router_entry,
        ipv4_count = '1',
        ipv6_count = '1',
        ipv4_records = [{'src-address': '1.1.1.1:123', 'src-port': '123', 'dst-address': '2.2.2.2:80', 'dst-port': '80', 'protocol': 'tcp'}],
        ipv6_records = [{'src-address': '[2001:db8::10]:5353', 'src-port': '5353',
                         'dst-address': '[2001:db8::20]:443', 'dst-port': '443', 'protocol': 'tcp'}],
        proplist = 'src-address,src-port,dst-address,dst-port,protocol'
    )

    result = IPConnectionStatsDatasource.metric_records(mock_router_entry)
    records_by_src = {record['src_address']: record for record in result}

    assert records_by_src['1.1.1.1']['dst_addresses'] == '2.2.2.2:80(tcp)'
    assert records_by_src['2001:db8::10']['dst_addresses'] == '[2001:db8::20]:443(tcp)'


def test_ip_connection_datasource_exposes_total_ipv4_and_ipv6_counts():
    """
    Verifies that IPConnectionDatasource returns combined and per-family connection totals.
    """
    mock_router_entry = _build_mock_router_entry()
    _configure_connection_api(
        mock_router_entry,
        ipv4_count = '123',
        ipv6_count = '7',
    )

    result = IPConnectionDatasource.metric_records(mock_router_entry, include_stack_counts = True)

    assert result[0]['count'] == '130'
    assert result[0]['ipv4_count'] == '123'
    assert result[0]['ipv6_count'] == '7'


def test_ip_connection_traffic_datasource_supports_ipv4_and_ipv6():
    """
    Verifies that IPConnectionTrafficDatasource aggregates active connection byte counters for both
    IPv4 and IPv6 records.
    """
    mock_router_entry = _build_mock_router_entry()
    _configure_connection_api(
        mock_router_entry,
        ipv4_count = '2',
        ipv6_count = '1',
        ipv4_records = [
            {'src-address': '1.1.1.1:123', 'src-port': '123', 'dst-address': '2.2.2.2:80', 'dst-port': '80',
             'protocol': 'tcp', 'orig-bytes': '10', 'repl-bytes': '20'},
            {'src-address': '1.1.1.1:123', 'src-port': '123', 'dst-address': '2.2.2.2:80', 'dst-port': '80',
             'protocol': 'tcp', 'orig-bytes': '1', 'repl-bytes': '2'},
        ],
        ipv6_records = [
            {'src-address': '[2001:db8::10]:5353', 'src-port': '5353', 'dst-address': '[2001:db8::20]:443', 'dst-port': '443',
             'protocol': 'tcp', 'orig-bytes': '100', 'repl-bytes': '200'},
        ],
        proplist = 'src-address,src-port,dst-address,dst-port,protocol,orig-bytes,repl-bytes'
    )

    result = IPConnectionTrafficDatasource.metric_records(mock_router_entry)
    records_by_key = {(record['src_address'], record['dst_address'], record['protocol']): record for record in result}

    assert records_by_key[('1.1.1.1', '2.2.2.2', 'tcp')]['upload_bytes'] == 11
    assert records_by_key[('1.1.1.1', '2.2.2.2', 'tcp')]['download_bytes'] == 22
    assert records_by_key[('1.1.1.1', '2.2.2.2', 'tcp')]['total_bytes'] == 33
    assert records_by_key[('2001:db8::10', '2001:db8::20', 'tcp')]['total_bytes'] == 300


def test_ip_connection_collector_collects_connection_traffic_metrics():
    """
    Verifies that IPConnectionCollector emits the per-connection traffic metrics only when the
    dedicated feature flag is enabled.
    """
    mock_router_entry = _build_mock_router_entry()
    mock_router_entry.config_entry.connection_traffic = True

    connection_traffic_records = [{'src_address': '1.1.1.1',
                                   'dst_address': '2.2.2.2',
                                   'protocol': 'tcp',
                                   'upload_bytes': 10,
                                   'download_bytes': 20,
                                   'total_bytes': 30}]

    with patch('mktxp.collector.connection_collector.IPConnectionTrafficDatasource.metric_records',
               return_value = connection_traffic_records), \
         patch('mktxp.collector.connection_collector.BaseOutputProcessor.augment_record'):
        metrics = list(IPConnectionCollector.collect(mock_router_entry))

    metric_names = [metric.name for metric in metrics]
    assert metric_names == ['mktxp_connection_upload_bytes', 'mktxp_connection_download_bytes', 'mktxp_connection_total_bytes']


def test_ip_connection_collector_collects_total_ipv4_and_ipv6_metrics():
    """
    Verifies that IPConnectionCollector emits combined and per-family connection totals.
    """
    mock_router_entry = _build_mock_router_entry()
    mock_router_entry.config_entry.connections = True

    connection_records = [{'count': '130', 'ipv4_count': '123', 'ipv6_count': '7'}]

    with patch('mktxp.collector.connection_collector.IPConnectionDatasource.metric_records',
               return_value = connection_records):
        metrics = list(IPConnectionCollector.collect(mock_router_entry))

    metric_names = [metric.name for metric in metrics]
    assert metric_names == ['mktxp_ip_connections_total', 'mktxp_ipv4_connections_total', 'mktxp_ipv6_connections_total']
