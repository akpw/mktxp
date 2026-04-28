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



class _StubMetric:
    """Identifiable placeholder for a yielded metric family."""
    def __init__(self, label):
        self.label = label
    def __eq__(self, other):
        return isinstance(other, _StubMetric) and other.label == self.label
    def __hash__(self):
        return hash((type(self), self.label))
    def __repr__(self):
        return f'_StubMetric({self.label!r})'


def _system_entry_stub(mci):
    """Build a stand-in for config_handler.system_entry that the handler reads."""
    return type('SysEntry', (), {
        'minimal_collect_interval': mci,
        'fetch_routers_in_parallel': False,
        'max_worker_threads': 1,
        'verbose_mode': False,
    })()


def _make_handler(per_call_metrics):
    from mktxp.flow.collector_handler import CollectorHandler

    router_entry = MagicMock()
    router_entry.is_ready.return_value = True
    router_entry.time_spent = {}

    entries_handler = MagicMock()
    entries_handler.router_entries = [router_entry]

    registry = MagicMock()
    registry.bandwidthCollector.collect.return_value = []

    iterator = iter(per_call_metrics)
    def collect_func(_entry):
        try:
            yield from next(iterator)
        except StopIteration:
            return

    registry.registered_collectors = {'mock_collector': collect_func}
    return CollectorHandler(entries_handler, registry)


def test_collect_caches_and_replays_on_mci_defer(monkeypatch):
    """When MCI defers, the handler must yield the cached metric families
    instead of an empty registry — otherwise Prometheus drops every mktxp_*
    series for that scrape and dashboards show false-down."""
    from mktxp.flow import collector_handler as ch_mod

    fresh = [_StubMetric('a'), _StubMetric('b')]
    handler = _make_handler([fresh])

    fake_cfg = MagicMock()
    fake_cfg.system_entry = _system_entry_stub(mci=5)
    monkeypatch.setattr(ch_mod, 'config_handler', fake_cfg)

    first = list(handler.collect())
    assert first == fresh, 'first scrape should yield freshly collected metrics'

    # Second call lands well within MCI; the inner collector iterator is
    # exhausted, so without the cache the result would be empty.
    second = list(handler.collect())
    assert second == fresh, 'within-MCI scrape must replay the cached metrics'


def test_empty_collection_does_not_clobber_cache(monkeypatch):
    """If a fresh collection produces nothing (e.g., all routers not_ready),
    the cache must be preserved so the next within-MCI scrape still has data."""
    from mktxp.flow import collector_handler as ch_mod

    seed = [_StubMetric('seed')]
    handler = _make_handler([seed, []])

    fake_cfg = MagicMock()
    fake_cfg.system_entry = _system_entry_stub(mci=0)
    monkeypatch.setattr(ch_mod, 'config_handler', fake_cfg)

    assert list(handler.collect()) == seed

    # Force a successful but empty collection (MCI=0 → always runs fresh).
    assert list(handler.collect()) == []

    # Bump MCI so the next call defers; cache should still hold the seed.
    fake_cfg.system_entry = _system_entry_stub(mci=60)
    assert list(handler.collect()) == seed
