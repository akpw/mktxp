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
from unittest.mock import MagicMock
from mktxp.datasource.connection_ds import IPConnectionStatsDatasource
from mktxp.flow.router_entry import RouterEntry

@pytest.mark.parametrize("connection_count_str, should_make_stats_call", [
    ('0', False),   # Scenario with zero connections
    ('123', True),  # Scenario with non-zero connections
])
def test_ip_connection_stats_datasource_checks_count_first(connection_count_str, should_make_stats_call):
    """
    Verifies that IPConnectionStatsDatasource checks the connection count and avoids fetching the full stats list if the count is 0
    """
    # Mocking the router_entry and its components
    mock_router_entry = MagicMock(spec=RouterEntry)
    mock_router_entry.router_name = "TestRouter"
    mock_router_entry.config_entry = MagicMock()
    mock_router_entry.config_entry.hostname = "testhost"
    mock_router_entry.api_connection = MagicMock()
    mock_router_entry.router_id = {'routerboard_name': 'test_router'}

    # Mock the API call & responces
    mock_api = MagicMock()
    mock_router_entry.api_connection.router_api.return_value = mock_api
    call_mock = mock_api.get_resource.return_value.call
    count_response = MagicMock()
    count_response.done_message = {'ret': connection_count_str}
    
    stats_response = [{'src-address': '1.1.1.1:123', 'dst-address': '2.2.2.2:80', 'protocol': 'tcp'}]

    # Side effect function to route calls based on arguments
    def api_call_router(*args, **kwargs):
        params = args[1]
        if params.get('count-only') == '':
            return count_response
        elif params.get('proplist') == 'src-address,dst-address,protocol':
            return stats_response
        return MagicMock()

    call_mock.side_effect = api_call_router

    # Test the method of focus
    result = IPConnectionStatsDatasource.metric_records(mock_router_entry)
    if should_make_stats_call:
        # This one should have been called twice, once for count and once for the stats
        assert call_mock.call_count == 2
        assert result is not None
        assert len(result) > 0
        assert result[0]['src_address'] == '1.1.1.1'
    else:
        # And this just once for the count
        call_mock.assert_called_once()
        assert result == []
