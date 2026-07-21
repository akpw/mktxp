from unittest.mock import Mock, patch

from mktxp.collector.interface_collector import InterfaceCollector


def test_interface_collector_skips_when_interface_disabled():
    mock_router_entry = Mock()
    mock_router_entry.config_entry.interface = False

    with patch('mktxp.datasource.interface_ds.InterfaceTrafficMetricsDataSource.metric_records') as mock_ds:
        results = list(InterfaceCollector.collect(mock_router_entry))

    mock_ds.assert_not_called()
    assert results == []


def test_interface_collector_yields_interface_metrics_when_enabled():
    mock_router_entry = Mock()
    mock_router_entry.config_entry.interface = True
    mock_router_entry.config_entry.interface_with_default_name = False

    mock_traffic_records = [{'name': 'ether1', 'running': 'true'}]

    with patch('mktxp.datasource.interface_ds.InterfaceTrafficMetricsDataSource.metric_records') as mock_ds, \
         patch('mktxp.datasource.interface_ds.InterfaceMetricsDataSource.metric_records') as mock_vlan_ds, \
         patch('mktxp.collector.base_collector.BaseCollector.info_collector') as mock_info, \
         patch('mktxp.collector.base_collector.BaseCollector.gauge_collector') as mock_gauge, \
         patch('mktxp.collector.base_collector.BaseCollector.counter_collector') as mock_counter:
        mock_ds.return_value = mock_traffic_records
        mock_vlan_ds.return_value = [{'name': 'vlan1', 'vlan_id': '10', 'interface': 'ether1'}]
        mock_info.side_effect = ['comment-metric', 'type-metric', 'mac-address-metric', 'default-name-metric', 'vlan-info-metric']
        mock_gauge.side_effect = ['running-metric', 'disabled-metric', 'actual-mtu-metric']
        mock_counter.side_effect = [
            'rx-byte-metric', 'tx-byte-metric', 'rx-packet-metric', 'tx-packet-metric',
            'rx-error-metric', 'tx-error-metric', 'rx-drop-metric', 'tx-drop-metric',
            'link-downs-metric'
        ]

        results = list(InterfaceCollector.collect(mock_router_entry))

    mock_ds.assert_called_once()
    assert results[0:4] == ['comment-metric', 'type-metric', 'running-metric', 'disabled-metric']

def test_interface_collector_with_default_name_enabled():
    mock_router_entry = Mock()
    mock_router_entry.config_entry.interface = True
    mock_router_entry.config_entry.interface_with_default_name = True

    mock_traffic_records = [{'name': 'ether1', 'default_name': 'ether1', 'running': 'true'}]

    with patch('mktxp.datasource.interface_ds.InterfaceTrafficMetricsDataSource.metric_records') as mock_ds, \
         patch('mktxp.datasource.interface_ds.InterfaceMetricsDataSource.metric_records') as mock_vlan_ds, \
         patch('mktxp.collector.base_collector.BaseCollector.info_collector') as mock_info, \
         patch('mktxp.collector.base_collector.BaseCollector.gauge_collector') as mock_gauge, \
         patch('mktxp.collector.base_collector.BaseCollector.counter_collector') as mock_counter:
        mock_ds.return_value = mock_traffic_records
        mock_vlan_ds.return_value = [{'name': 'vlan1', 'vlan_id': '10', 'interface': 'ether1'}]
        
        # mock returns to avoid StopIteration on list conversion
        mock_info.side_effect = ['info']*5
        mock_gauge.side_effect = ['gauge']*3
        mock_counter.side_effect = ['counter']*9

        list(InterfaceCollector.collect(mock_router_entry))

    # Assert that the counter_collector was called with base_labels = ['name', 'default_name']
    assert mock_counter.call_count == 9
    first_call_args = mock_counter.call_args_list[0][0]
    assert first_call_args[0] == 'interface_rx_byte'
    assert first_call_args[4] == ['name', 'default_name']
