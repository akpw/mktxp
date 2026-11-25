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

import pytest
from unittest.mock import Mock, patch
from mktxp.datasource.address_list_ds import AddressListMetricsDataSource


def test_count_selected_records_success():
    mock_router_entry = Mock()
    mock_router_entry.router_name = "test_router"
    mock_router_entry.config_entry.hostname = "10.0.0.1"

    with patch('mktxp.datasource.base_ds.BaseDSProcessor.count_records') as mock_count:
        mock_count.side_effect = lambda router, api_path, api_query: 15 if api_query.get('list') == 'listA' else 30

        result = AddressListMetricsDataSource.count_selected_records(
            mock_router_entry, ['listA', 'listB'], 'ip'
        )

        assert result == {'listA': 15, 'listB': 30}
        assert mock_count.call_count == 2
        mock_count.assert_any_call(
            mock_router_entry, api_path='/ip/firewall/address-list', api_query={'list': 'listA'}
        )
        mock_count.assert_any_call(
            mock_router_entry, api_path='/ip/firewall/address-list', api_query={'list': 'listB'}
        )


def test_count_selected_records_partial_failure():
    mock_router_entry = Mock()
    mock_router_entry.router_name = "test_router"
    mock_router_entry.config_entry.hostname = "10.0.0.1"

    with patch('mktxp.datasource.base_ds.BaseDSProcessor.count_records') as mock_count:
        # listA succeeds with 5, listB fails and returns None
        mock_count.side_effect = lambda router, api_path, api_query: 5 if api_query.get('list') == 'listA' else None

        result = AddressListMetricsDataSource.count_selected_records(
            mock_router_entry, ['listA', 'listB'], 'ip'
        )

        assert result == {'listA': 5}
