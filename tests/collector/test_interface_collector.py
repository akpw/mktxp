import pytest
from unittest.mock import Mock, patch
from mktxp.collector.interface_collector import InterfaceCollector


def test_interface_collector_bridge_vlan_yield():
    """
    Tests that the interface collector correctly yields bridge VLAN metrics
    when the configuration enables it.
    """
    # 1. Setup Mocks
    mock_router_entry = Mock()

    # We must set 'interface' to True to pass the first guard clause in collect()
    mock_router_entry.config_entry.interface = True
    mock_router_entry.config_entry.bridge_vlan = True

    # Mock data for traffic metrics (required to pass the second guard clause)
    mock_traffic_records = [{'name': 'ether1', 'running': 'true'}]

    # Mock data for VLAN metrics
    mock_vlan_records = [
        {
            'name': 'bridge-local-vlan-10',
            'bridge': 'bridge-local',
            'vlan_ids': '10',
            'current_tagged': 'sfp1',
            'current_untagged': 'ether1'
        }
    ]

    # 2. Patch the Data Sources and BaseCollector
    # We need to patch InterfaceTrafficMetricsDataSource so it doesn't return None and exit early
    with patch('mktxp.datasource.interface_ds.InterfaceTrafficMetricsDataSource.metric_records') as mock_traffic_ds, \
         patch('mktxp.datasource.interface_ds.BridgeVlanMetricsDataSource.metric_records') as mock_vlan_ds, \
         patch('mktxp.collector.base_collector.BaseCollector.info_collector') as mock_info:

        mock_traffic_ds.return_value = mock_traffic_records
        mock_vlan_ds.return_value = mock_vlan_records
        mock_info.return_value = "MockedMetricObject"

        # 3. Execute
        collector = InterfaceCollector()
        results = list(collector.collect(mock_router_entry))

        # 4. Assertions
        # Verify the Bridge VLAN Data Source was called
        mock_vlan_ds.assert_called_once_with(
            mock_router_entry,
            metric_labels=['name', 'bridge', 'vlan_ids', 'current_tagged', 'current_untagged']
        )

        assert "MockedMetricObject" in results


def test_interface_collector_bridge_vlan_disabled():
    """
    Ensures bridge VLAN metrics are NOT yielded if disabled in config.
    """
    mock_router_entry = Mock()
    mock_router_entry.config_entry.bridge_vlan = False

    with patch('mktxp.datasource.interface_ds.BridgeVlanMetricsDataSource.metric_records') as mock_ds:
        collector = InterfaceCollector()
        list(collector.collect(mock_router_entry))

        # Verify DS was never touched
        mock_ds.assert_not_called()
