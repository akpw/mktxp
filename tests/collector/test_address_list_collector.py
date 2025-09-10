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
from unittest.mock import MagicMock, call
from collections import defaultdict
from mktxp.collector.address_list_collector import AddressListCollector
from mktxp.cli.config.config import config_handler, MKTXPConfigKeys

@pytest.mark.parametrize("address_list_config, ipv6_address_list_config", [
    ("MyList, AnotherList", "AnotherList"),
    (["MyList", "AnotherList"], ["AnotherList"]),
    ("MyList,, ", None),
    (None, "AnotherList"),
    ("None", "None"),
    (None, None)
])
def test_address_list_collector(address_list_config, ipv6_address_list_config):
    """
    Verifies that AddressListCollector processes the address list data correctly.
    """
    config_handler()
    # Mocking the router_entry and its components
    mock_router_entry = MagicMock()
    mock_router_entry.config_entry.address_list = address_list_config
    mock_router_entry.config_entry.ipv6_address_list = ipv6_address_list_config
    mock_router_entry.router_name = "TestRouter"
    mock_router_entry.config_entry.hostname = "testhost"
    mock_router_entry.api_connection = MagicMock()
    mock_router_entry.router_id = {
        MKTXPConfigKeys.ROUTERBOARD_NAME: 'test_router',
        MKTXPConfigKeys.ROUTERBOARD_ADDRESS: '1.2.3.4'
    }

    # Mock the API call & responses
    mock_api = MagicMock()
    mock_router_entry.api_connection.router_api.return_value = mock_api
    
    ip_response = [
        {'list': 'MyList', 'address': '192.168.1.1', 'dynamic': 'false', 'timeout': '0s', 'disabled': 'false', 'comment': ''},
        {'list': 'MyList', 'address': '192.168.1.2', 'dynamic': 'true', 'timeout': '1d2h3m4s', 'disabled': 'false', 'comment': 'dynamic entry'},
        {'list': 'AnotherList', 'address': '10.0.0.1', 'dynamic': 'false', 'timeout': None, 'disabled': 'false', 'comment': ''}
    ]
    ipv6_response = [
        {'list': 'AnotherList', 'address': '::1', 'dynamic': 'false', 'timeout': '0s', 'disabled': 'true', 'comment': ''}
    ]

    def get_resource_side_effect(path):
        mock_resource = MagicMock()
        response_data = ip_response if path == '/ip/firewall/address-list' else ipv6_response

        def get_side_effect(list=None):
            return [r for r in response_data if r.get('list') == list]
        mock_resource.get.side_effect = get_side_effect

        def call_side_effect(command, params, query):
            assert command == 'print'
            assert params == {'count-only': ''}
            
            filtered_response = response_data
            if 'list' in query:
                filtered_response = [r for r in filtered_response if r.get('list') == query['list']]
            if 'dynamic' in query:
                is_dynamic = query['dynamic'] == 'yes'
                filtered_response = [r for r in filtered_response if (r.get('dynamic') == 'true') == is_dynamic]

            return MagicMock(done_message={'ret': str(len(filtered_response))})
        mock_resource.call.side_effect = call_side_effect
        
        return mock_resource

    mock_api.get_resource.side_effect = get_resource_side_effect

    # Test the method of focus
    metrics = list(AddressListCollector.collect(mock_router_entry))
    
    # Restore the original _get_list_names to use in the test assertions
    original_get_list_names = AddressListCollector._get_list_names
    AddressListCollector._get_list_names = lambda v: [n.strip() for n in v.split(',')] if isinstance(v, str) and v.lower() != 'none' else v if isinstance(v, list) else []

    ipv4_lists = AddressListCollector._get_list_names(address_list_config)
    ipv6_lists = AddressListCollector._get_list_names(ipv6_address_list_config)

    # Clean up empty strings from the list of names for correct sample count
    ipv4_lists_cleaned = [name for name in ipv4_lists if name] if ipv4_lists else []
    ipv6_lists_cleaned = [name for name in ipv6_lists if name] if ipv6_lists else []

    AddressListCollector._get_list_names = original_get_list_names

    expected_metrics_count = 0
    if ipv4_lists_cleaned:
        expected_metrics_count += 1  # info metric
        expected_metrics_count += 1  # all lists count
        expected_metrics_count += 1  # selected lists count
        
    if ipv6_lists_cleaned:
        expected_metrics_count += 1  # info metric
        expected_metrics_count += 1  # all lists count
        expected_metrics_count += 1  # selected lists count
        
    assert len(metrics) == expected_metrics_count

    if ipv4_lists_cleaned:
        _assert_metrics_for_ip_version(metrics, 'ip', ipv4_lists_cleaned, ip_response)

    if ipv6_lists_cleaned:
        _assert_metrics_for_ip_version(metrics, 'ipv6', ipv6_lists_cleaned, ipv6_response)


def _assert_metrics_for_ip_version(metrics, ip_version, lists_cleaned, response):
    ipv6_suffix = '_ipv6' if ip_version == 'ipv6' else ''

    # Assert info metric
    info_metric = next((m for m in metrics if m.name == f'mktxp_firewall_address_list{ipv6_suffix}'), None)
    assert info_metric is not None
    expected_info_samples = len([r for r in response if r['list'] in lists_cleaned])
    assert len(info_metric.samples) == expected_info_samples

    # Assert all lists counts
    all_counts_metric = next((m for m in metrics if m.name == f'mktxp_firewall_address_list_all_count{ipv6_suffix}'), None)
    assert all_counts_metric is not None
    assert len(all_counts_metric.samples) == 3 # total, dynamic, static
    for sample in all_counts_metric.samples:
        count_type = sample.labels['count_type']
        is_dynamic = count_type == 'dynamic'
        expected_count = len([r for r in response if (r.get('dynamic') == 'true') == is_dynamic]) if count_type != 'total' else len(response)
        assert sample.value == expected_count

    # Assert selected lists counts
    selected_counts_metric = next((m for m in metrics if m.name == f'mktxp_firewall_address_list_selected_count{ipv6_suffix}'), None)
    assert selected_counts_metric is not None
    assert len(selected_counts_metric.samples) == len(lists_cleaned)
    for sample in selected_counts_metric.samples:
        list_name = sample.labels['list']
        expected_count = len([r for r in response if r['list'] == list_name])
        assert sample.value == expected_count
