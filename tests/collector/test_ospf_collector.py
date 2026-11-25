from unittest.mock import Mock, patch

from mktxp.collector.ospf_collector import OSPFCollector


def test_ospf_collector_exports_neighbors_and_lsa_count_ros7():
    router_id = {
        'routerboard_name': 'router-a',
        'routerboard_address': '192.0.2.1',
    }
    router_entry = Mock()
    router_entry.router_name = 'router-a'
    router_entry.config_entry.hostname = '192.0.2.1'
    router_entry.config_entry.ospf = True
    router_entry.config_entry.custom_labels = None
    router_entry.router_id = router_id

    raw_neighbors = [
        {
            'instance': 'ospf-instance-1',
            'area': 'backbone',
            'router-id': '10.21.0.2',
            'address': '10.21.0.2',
            'state': 'Full',
            'state-changes': '6',
            'adjacency': '1h',
            'priority': '1',
        },
        {
            'instance': 'ospf-instance-1',
            'area': 'backbone',
            'router-id': '10.21.0.3',
            'address': '10.21.0.3',
            'state': '2-Way',
            'state-changes': '2',
            'adjacency': '',
            'priority': '1',
        },
    ]
    router_entry.api_connection.router_api.return_value.get_resource.return_value.get.return_value = raw_neighbors

    with patch(
        'mktxp.datasource.ospf_ds.BaseDSProcessor.count_records',
        return_value=18,
    ):
        metrics = list(OSPFCollector.collect(router_entry))

    assert [m.name for m in metrics] == [
        'mktxp_ospf_neighbors',
        'mktxp_ospf_neighbor_full',
        'mktxp_ospf_neighbor_state_changes',
        'mktxp_ospf_neighbor_adjacency',
        'mktxp_ospf_lsa_count',
    ]

    info_samples = metrics[0].samples
    assert info_samples[0].labels['state'] == 'Full'
    assert info_samples[0].labels['area'] == 'backbone'
    assert info_samples[1].labels['state'] == '2-Way'

    full_samples = {s.labels['router_id']: s.value for s in metrics[1].samples}
    assert full_samples == {'10.21.0.2': '1', '10.21.0.3': '0'}

    changes_samples = {s.labels['router_id']: s.value for s in metrics[2].samples}
    assert changes_samples == {'10.21.0.2': '6', '10.21.0.3': '2'}

    adjacency_samples = {s.labels['router_id']: float(s.value) for s in metrics[3].samples}
    assert adjacency_samples == {'10.21.0.2': 3600000.0, '10.21.0.3': 0.0}

    assert metrics[4].samples[0].value == 18
    assert metrics[4].samples[0].labels == router_id


def test_ospf_collector_handles_ros6_records_without_area():
    router_id = {
        'routerboard_name': 'ros6-router',
        'routerboard_address': '192.0.2.2',
    }
    router_entry = Mock()
    router_entry.router_name = 'ros6-router'
    router_entry.config_entry.hostname = '192.0.2.2'
    router_entry.config_entry.ospf = True
    router_entry.config_entry.custom_labels = None
    router_entry.router_id = router_id

    # ROS 6 neighbor records omit 'area'
    raw_neighbors = [
        {
            'instance': 'default',
            'router-id': '10.1.100.90',
            'address': '10.1.1.122',
            'state': 'Full',
            'state-changes': '4',
            'adjacency': '2m',
        }
    ]
    router_entry.api_connection.router_api.return_value.get_resource.return_value.get.return_value = raw_neighbors

    with patch(
        'mktxp.datasource.ospf_ds.BaseDSProcessor.count_records',
        return_value=None,
    ):
        metrics = list(OSPFCollector.collect(router_entry))

    assert [m.name for m in metrics] == [
        'mktxp_ospf_neighbors',
        'mktxp_ospf_neighbor_full',
        'mktxp_ospf_neighbor_state_changes',
        'mktxp_ospf_neighbor_adjacency',
    ]
    assert metrics[0].samples[0].labels['area'] == ''
    assert metrics[1].samples[0].value == '1'
    assert float(metrics[3].samples[0].value) == 120000.0


def test_ospf_collector_skips_when_disabled():
    router_entry = Mock()
    router_entry.config_entry.ospf = False

    with patch(
        'mktxp.collector.ospf_collector.OSPFMetricsDataSource.neighbor_records'
    ) as neighbor_records:
        assert list(OSPFCollector.collect(router_entry)) == []

    neighbor_records.assert_not_called()
