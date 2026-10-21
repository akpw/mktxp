from unittest.mock import Mock, call, patch

from mktxp.datasource.bgp_ds import BGPMetricsDataSource


def test_bgp_datasource_reads_routeros7_resource_for_requested_path():
    router_entry = Mock()
    records = [{'name': 'main'}]
    router_entry.api_connection.router_api.return_value.get_resource.return_value.get.return_value = records

    with patch(
        'mktxp.datasource.bgp_ds.SystemResourceMetricsDataSource.os_version',
        return_value='7.15',
    ), patch(
        'mktxp.datasource.bgp_ds.BaseDSProcessor.trimmed_records',
        return_value=[{'name': 'main'}],
    ) as trim_records:
        result = BGPMetricsDataSource.metric_records(
            router_entry, metric_labels=['name'], path='instance'
        )

    router_entry.api_connection.router_api.return_value.get_resource.assert_called_once_with(
        '/routing/bgp/instance'
    )
    trim_records.assert_called_once()
    assert result == [{'name': 'main'}]


def test_bgp_datasource_uses_legacy_peer_path_and_skips_unsupported_paths():
    router_entry = Mock()
    router_entry.api_connection.router_api.return_value.get_resource.return_value.get.return_value = []

    with patch(
        'mktxp.datasource.bgp_ds.SystemResourceMetricsDataSource.os_version',
        return_value='6.49',
    ), patch('mktxp.datasource.bgp_ds.routerOS7_version', return_value=False):
        assert BGPMetricsDataSource.metric_records(router_entry, path='instance') == []
        connection_result = BGPMetricsDataSource.metric_records(
            router_entry, path='connection'
        )
        session_result = BGPMetricsDataSource.metric_records(
            router_entry, path='session'
        )

    assert router_entry.api_connection.router_api.return_value.get_resource.call_args_list == [
        call('/routing/bgp/peer'),
        call('/routing/bgp/peer'),
    ]
    assert connection_result == []
    assert session_result == []


def test_bgp_datasource_counts_advertisements_with_count_only_queries():
    router_entry = Mock()

    with patch(
        'mktxp.datasource.bgp_ds.SystemResourceMetricsDataSource.os_version',
        return_value='7.15',
    ), patch(
        'mktxp.datasource.bgp_ds.BaseDSProcessor.count_records',
        side_effect=[2, 1],
    ) as count_records:
        result = BGPMetricsDataSource.advertised_prefix_counts(
            router_entry, ['peer-a']
        )

    assert result == [
        {'peer': 'peer-a', 'afi': 'ipv4', 'count': 2},
        {'peer': 'peer-a', 'afi': 'ipv6', 'count': 1},
    ]
    assert count_records.call_args_list[0].kwargs == {
        'api_path': '/routing/bgp/advertisements',
        'api_query': {'peer': 'peer-a', 'afi': 'ip'},
    }
    assert count_records.call_args_list[1].kwargs == {
        'api_path': '/routing/bgp/advertisements',
        'api_query': {'peer': 'peer-a', 'afi': 'ipv6'},
    }


def test_bgp_datasource_keeps_successful_counts_when_one_query_fails():
    router_entry = Mock()

    with patch(
        'mktxp.datasource.bgp_ds.SystemResourceMetricsDataSource.os_version',
        return_value='7.15',
    ), patch(
        'mktxp.datasource.bgp_ds.BaseDSProcessor.count_records',
        side_effect=[2, None],
    ):
        result = BGPMetricsDataSource.advertised_prefix_counts(router_entry, ['peer-a'])

    assert result == [{'peer': 'peer-a', 'afi': 'ipv4', 'count': 2}]
