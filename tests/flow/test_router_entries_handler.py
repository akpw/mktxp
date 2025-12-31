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


def test_module_only_entries_skipped_in_default_collection(monkeypatch):
    from mktxp.flow import router_entries_handler as reh

    class DummyEntry:
        def __init__(self, name, module_only):
            self.name = name
            self.module_only = module_only

    class DummyConfigHandler:
        def registered_entries(self):
            return ['module_only_entry', 'regular_entry']

        def registered_entry(self, name):
            return True

        def config_entry(self, name):
            if name == 'module_only_entry':
                return DummyEntry(name, module_only=True)
            return DummyEntry(name, module_only=False)

    def fake_router_entry(name):
        return Mock(config_entry=Mock(enabled=True, module_only=False), router_name=name)

    monkeypatch.setattr(reh, 'config_handler', DummyConfigHandler())
    monkeypatch.setattr(reh, 'RouterEntry', fake_router_entry)
    monkeypatch.setattr(reh.RouterEntriesHandler, '_set_child_entries', lambda _: None)

    handler = reh.RouterEntriesHandler()
    entries = list(handler.router_entries)

    assert len(entries) == 1
    assert entries[0].router_name == 'regular_entry'
