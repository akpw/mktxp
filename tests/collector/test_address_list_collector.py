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
        if path == '/ip/firewall/address-list':
            def get_side_effect(list=None):
                return [r for r in ip_response if r.get('list') == list]
            mock_resource.get.side_effect = get_side_effect
        elif path == '/ipv6/firewall/address-list':
            def get_side_effect(list=None):
                return [r for r in ipv6_response if r.get('list') == list]
            mock_resource.get.side_effect = get_side_effect
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

    expected_ipv4_info_samples = len([r for r in ip_response if r['list'] in ipv4_lists_cleaned]) if ipv4_lists_cleaned else 0
    expected_ipv6_info_samples = len([r for r in ipv6_response if r['list'] in ipv6_lists_cleaned]) if ipv6_lists_cleaned else 0
    
    AddressListCollector._get_list_names = original_get_list_names

    expected_metrics_count = 0
    if expected_ipv4_info_samples > 0:
        expected_metrics_count += 2
    if expected_ipv6_info_samples > 0:
        expected_metrics_count += 2
        
    assert len(metrics) == expected_metrics_count

    if expected_ipv4_info_samples > 0:
        ipv4_info_metric = next((m for m in metrics if m.name == 'mktxp_firewall_address_list'), None)
        assert ipv4_info_metric is not None
        assert len(ipv4_info_metric.samples) == expected_ipv4_info_samples
        
        ipv4_count_metric = next((m for m in metrics if m.name == 'mktxp_firewall_address_list_entries_count'), None)
        assert ipv4_count_metric is not None
        assert len(ipv4_count_metric.samples) > 0
        for sample in ipv4_count_metric.samples:
            assert sample.labels[MKTXPConfigKeys.ROUTERBOARD_NAME] == 'test_router'
            assert sample.labels[MKTXPConfigKeys.ROUTERBOARD_ADDRESS] == '1.2.3.4'


    if expected_ipv6_info_samples > 0:
        ipv6_info_metric = next((m for m in metrics if m.name == 'mktxp_firewall_address_list_ipv6'), None)
        assert ipv6_info_metric is not None
        assert len(ipv6_info_metric.samples) == expected_ipv6_info_samples
        
        ipv6_count_metric = next((m for m in metrics if m.name == 'mktxp_firewall_address_list_entries_count_ipv6'), None)
        assert ipv6_count_metric is not None
        assert len(ipv6_count_metric.samples) > 0
        for sample in ipv6_count_metric.samples:
            assert sample.labels[MKTXPConfigKeys.ROUTERBOARD_NAME] == 'test_router'
            assert sample.labels[MKTXPConfigKeys.ROUTERBOARD_ADDRESS] == '1.2.3.4'
