import pytest
from unittest.mock import Mock, patch
from mktxp.flow.router_entries_handler import RouterEntriesHandler

@patch('mktxp.flow.router_entries_handler.config_handler')
def test_set_child_entries_with_invalid_remote_dhcp_entry(mock_config_handler, capsys):
    # Test case: remote_dhcp_entry is a boolean - this should be treated as an unregistered entry
    mock_router_entry = Mock()
    mock_router_entry.router_name = "TestRouter"
    mock_router_entry.config_entry.remote_dhcp_entry = True
    mock_router_entry.config_entry.remote_capsman_entry = None
    
    # Mock registered_entry to return None for boolean values (as it would in real ConfigObj)
    mock_config_handler.registered_entry.return_value = None

    RouterEntriesHandler._set_child_entries(mock_router_entry)

    captured = capsys.readouterr()
    assert "Error in configuration for TestRouter: remote_dhcp_entry must a name of another router entry or 'None', but it is 'True'. Ignoring." in captured.out
    mock_config_handler.registered_entry.assert_called_with(True)

@patch('mktxp.flow.router_entries_handler.config_handler')
def test_set_child_entries_with_valid_remote_dhcp_entry(mock_config_handler, capsys):
    # Test case: remote_dhcp_entry is a valid string
    mock_router_entry = Mock()
    mock_router_entry.router_name = "TestRouter"
    mock_router_entry.config_entry.remote_dhcp_entry = "AnotherRouter"
    mock_router_entry.config_entry.remote_capsman_entry = None
    mock_config_handler.registered_entry.return_value = True

    with patch('mktxp.flow.router_entries_handler.RouterEntry') as mock_router_entry_class:
        RouterEntriesHandler._set_child_entries(mock_router_entry)

    mock_config_handler.registered_entry.assert_called_with("AnotherRouter")
    mock_router_entry_class.assert_called_with("AnotherRouter")
