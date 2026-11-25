from unittest.mock import Mock, patch

from mktxp.datasource.ospf_ds import OSPFMetricsDataSource


def test_ospf_datasource_fetches_neighbors_and_trims_records():
    router_entry = Mock()
    router_entry.router_name = 'router-a'
    router_entry.config_entry.hostname = '192.0.2.1'
    router_entry.config_entry.custom_labels = None
    router_entry.router_id = {
        'routerboard_name': 'router-a',
        'routerboard_address': '192.0.2.1',
    }
    raw_records = [
        {
            'instance': 'ospf-instance-1',
            'area': 'backbone',
            'router-id': '10.21.0.2',
            'address': '10.21.0.2',
            'state': 'Full',
            'state-changes': '6',
            'adjacency': '11h40m54s',
            'priority': '1',
        }
    ]
    router_entry.api_connection.router_api.return_value.get_resource.return_value.get.return_value = raw_records

    result = OSPFMetricsDataSource.neighbor_records(
        router_entry,
        metric_labels=['instance', 'area', 'router_id', 'address', 'state', 'state_changes'],
    )

    router_entry.api_connection.router_api.return_value.get_resource.assert_called_once_with(
        '/routing/ospf/neighbor'
    )
    assert result == [
        {
            'routerboard_name': 'router-a',
            'routerboard_address': '192.0.2.1',
            'instance': 'ospf-instance-1',
            'area': 'backbone',
            'router_id': '10.21.0.2',
            'address': '10.21.0.2',
            'state': 'Full',
            'state_changes': '6',
        }
    ]


def test_ospf_datasource_lsa_count_uses_count_only_and_preserves_router_id():
    router_entry = Mock()
    router_entry.router_name = 'router-a'
    router_entry.config_entry.hostname = '192.0.2.1'
    router_entry.config_entry.custom_labels = None
    router_entry.router_id = {
        'routerboard_name': 'router-a',
        'routerboard_address': '192.0.2.1',
    }

    with patch(
        'mktxp.datasource.ospf_ds.BaseDSProcessor.count_records',
        return_value=42,
    ) as count_records:
        result = OSPFMetricsDataSource.lsa_count(router_entry)

    count_records.assert_called_once_with(router_entry, api_path='/routing/ospf/lsa')
    assert result == [
        {
            'routerboard_name': 'router-a',
            'routerboard_address': '192.0.2.1',
            'count': 42,
        }
    ]


def test_ospf_datasource_handles_errors_gracefully():
    router_entry = Mock()
    router_entry.router_name = 'router-a'
    router_entry.config_entry.hostname = '192.0.2.1'
    router_entry.api_connection.router_api.side_effect = RuntimeError('api boom')

    assert OSPFMetricsDataSource.neighbor_records(router_entry) is None

    with patch(
        'mktxp.datasource.ospf_ds.BaseDSProcessor.count_records',
        return_value=None,
    ):
        assert OSPFMetricsDataSource.lsa_count(router_entry) is None
