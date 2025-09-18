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
from unittest.mock import MagicMock, patch
from mktxp.flow.router_entry import RouterEntry
from mktxp.flow.router_connection import RouterAPIConnection

@pytest.fixture
def mock_api_connection():
    """Fixture to create a mock RouterAPIConnection"""
    connection = MagicMock(spec=RouterAPIConnection)
    connection.is_connected.return_value = False
    return connection

@pytest.fixture(params=[(True, True), (True, False), (False, True), (False, False)])
def router_entry(request, tmpdir, mock_api_connection):
    """Fixture to create a RouterEntry with different persistence settings."""
    
    persistent_pool, persistent_dhcp = request.param
    
    # Create temporary config files
    mktxp_conf = tmpdir.join("mktxp.conf")
    mktxp_conf.write("""
[test_router]
hostname = localhost
""")
    _mktxp_conf = tmpdir.join("_mktxp.conf")
    _mktxp_conf.write(f"""
[MKTXP]
persistent_router_connection_pool = {persistent_pool}
persistent_dhcp_cache = {persistent_dhcp}
compact_default_conf_values = False
verbose_mode = False
""")
    
    with patch('mktxp.flow.router_entry.RouterAPIConnection', return_value=mock_api_connection):
        from mktxp.cli.config.config import config_handler, CustomConfig
        config_handler(os_config=CustomConfig(str(tmpdir)))
        
        entry = RouterEntry('test_router')
        entry.persistent_pool = persistent_pool
        entry.persistent_dhcp_cache = persistent_dhcp
        return entry

@pytest.mark.parametrize(
    "initial_connected_state, connect_succeeds, expected_ready_state, expect_connect_call",
    [
        (True, None, True, False),
        (False, True, True, True),
        (False, False, False, True),
    ]
)
def test_is_ready_logic(initial_connected_state, connect_succeeds, expected_ready_state, expect_connect_call, router_entry, mock_api_connection):
    # Arrange
    mock_api_connection.is_connected.return_value = initial_connected_state
    if connect_succeeds is not None:
        def connect_side_effect():
            mock_api_connection.is_connected.return_value = connect_succeeds
        mock_api_connection.connect.side_effect = connect_side_effect

    # Act
    ready = router_entry.is_ready()

    # Assert
    assert ready is expected_ready_state
    if expect_connect_call:
        mock_api_connection.connect.assert_called_once()
    else:
        mock_api_connection.connect.assert_not_called()

def test_is_done_disconnects(router_entry, mock_api_connection):
    # Arrange
    # Setup child entries to test their disconnection as well
    dhcp_connection = MagicMock(spec=RouterAPIConnection)
    capsman_connection = MagicMock(spec=RouterAPIConnection)
    router_entry.dhcp_entry = MagicMock()
    router_entry.dhcp_entry.api_connection = dhcp_connection
    router_entry.capsman_entry = MagicMock()
    router_entry.capsman_entry.api_connection = capsman_connection

    # Act
    router_entry.is_done()

    # Assert
    if not router_entry.persistent_pool:
        mock_api_connection.disconnect.assert_called_once()
        dhcp_connection.disconnect.assert_called_once()
        capsman_connection.disconnect.assert_called_once()
    else:
        mock_api_connection.disconnect.assert_not_called()
        dhcp_connection.disconnect.assert_not_called()
        capsman_connection.disconnect.assert_not_called()

def test_is_done_dhcp_cache(router_entry):
    """
    Tests that the DHCP cache is cleared or not based on the persistent_dhcp_cache setting.
    """
    # Arrange
    router_entry.dhcp_records = [{'mac_address': '00:00:00:00:00:01', 'address': '1.1.1.1'}]
    assert router_entry._dhcp_records != {}

    # Act
    router_entry.is_done()

    # Assert
    if not router_entry.persistent_dhcp_cache:
        assert router_entry._dhcp_records == {}
    else:
        assert router_entry._dhcp_records != {}
