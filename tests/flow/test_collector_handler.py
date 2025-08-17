import pytest
from unittest.mock import MagicMock, Mock
from mktxp.flow.collector_handler import CollectorHandler

@pytest.fixture
def mock_router_entry():
    """Fixture to create a mock RouterEntry"""
    entry = MagicMock()
    entry.is_ready.return_value = True
    return entry

@pytest.fixture
def mock_entries_handler(mock_router_entry):
    """Fixture to create a mock RouterEntriesHandler"""
    handler = MagicMock()
    handler.router_entries = [mock_router_entry]
    return handler

@pytest.fixture
def mock_collector_registry():
    """Fixture to create a mock CollectorRegistry"""
    registry = MagicMock()
    mock_collect_func = Mock(return_value=[]) 
    registry.registered_collectors = {'mock_collector': mock_collect_func}
    registry.bandwidthCollector.collect.return_value = []
    return registry

@pytest.mark.parametrize(
    "is_ready, is_done_called",
    [
        (True, True),
        (False, False),
    ]
)
def test_collect_sync_lifecycle(is_ready, is_done_called, mock_entries_handler, mock_collector_registry, mock_router_entry):
    # Arrange
    mock_router_entry.is_ready.return_value = is_ready
    handler = CollectorHandler(mock_entries_handler, mock_collector_registry)
    
    # Act
    list(handler.collect_sync())

    # Assert
    mock_router_entry.is_ready.assert_called_once()
    if is_done_called:
        mock_router_entry.is_done.assert_called_once()
    else:
        mock_router_entry.is_done.assert_not_called()
