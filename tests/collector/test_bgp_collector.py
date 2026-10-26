from unittest.mock import Mock, patch

from mktxp.collector.bgp_collector import BGPCollector


def test_bgp_collector_exports_session_and_configuration_metrics():
    router_id = {
        'routerboard_name': 'router-a',
        'routerboard_address': '192.0.2.1',
    }
    router_entry = Mock()
    router_entry.config_entry.bgp = True
    router_entry.config_entry.custom_labels = False
    router_entry.router_id = router_id

    records_by_path = {
        'session': [{
            **router_id,
            'name': 'peer-a',
            'remote_address': '192.0.2.2',
            'remote_as': '64502',
            'local_as': '64501',
            'remote_afi': 'ip,ipv6',
            'local_afi': 'ip,ipv6',
            'remote_id': '192.0.2.2',
            'local_id': '192.0.2.1',
            'remote_capabilities': 'mp,as4',
            'local_capabilities': 'mp,as4',
            'last_notification': '',
            'remote_messages': '20',
            'remote_bytes': '2000',
            'local_messages': '10',
            'local_bytes': '1000',
            'prefix_count': '42',
            'output_prefix_count': '17',
            'established': 1,
            'uptime': '1000',
        }],
        'connection': [{
            **router_id,
            'name': 'peer-a',
            'remote_address': '192.0.2.2',
            'remote_as': '64502',
        }],
        'instance': [{
            **router_id,
            'name': 'main',
            'as': '64501',
            'router_id': '192.0.2.1',
        }],
    }

    def records(entry, **kwargs):
        assert entry is router_entry
        return records_by_path[kwargs.get('path', 'session')]

    with patch(
        'mktxp.collector.bgp_collector.BGPMetricsDataSource.metric_records',
        side_effect=records,
    ), patch(
        'mktxp.collector.bgp_collector.BGPMetricsDataSource.advertised_prefix_counts',
        return_value=[
            {'name': 'peer-a', 'afi': 'ipv4', 'count': 2},
            {'name': 'peer-a', 'afi': 'ipv6', 'count': 1},
        ],
    ) as advertised_prefix_counts:
        metrics = list(BGPCollector.collect(router_entry))

    assert [metric.name for metric in metrics] == [
        'mktxp_bgp_sessions',
        'mktxp_bgp_remote_messages',
        'mktxp_bgp_local_messages',
        'mktxp_bgp_remote_bytes',
        'mktxp_bgp_local_bytes',
        'mktxp_bgp_prefix_count',
        'mktxp_bgp_advertised_prefixes',
        'mktxp_bgp_advertised_prefix_count',
        'mktxp_bgp_established',
        'mktxp_bgp_uptime',
        'mktxp_bgp_connections',
        'mktxp_bgp_instances',
    ]
    session_labels = metrics[0].samples[0].labels
    assert session_labels['last_notification'] == ''
    assert session_labels['remote_capabilities'] == 'mp,as4'
    assert metrics[6].samples[0].value == 2
    assert metrics[6].samples[0].labels == {'name': 'peer-a', 'afi': 'ipv4'}
    assert metrics[7].samples[0].value == '17'
    assert metrics[8].samples[0].value == 1
    advertised_prefix_counts.assert_called_once_with(router_entry, ['peer-a'])


def test_bgp_collector_omits_advertised_prefix_metric_when_router_does_not_report_it():
    router_entry = Mock()
    router_entry.config_entry.bgp = True
    router_entry.config_entry.custom_labels = False
    router_entry.router_id = {
        'routerboard_name': 'router-a',
        'routerboard_address': '192.0.2.1',
    }
    session_record = {
        **router_entry.router_id,
        'name': 'peer-a',
        'established': 1,
    }

    def records(_entry, **kwargs):
        if kwargs.get('path') == 'connection':
            return []
        if kwargs.get('path') == 'instance':
            return []
        return [session_record]

    with patch(
        'mktxp.collector.bgp_collector.BGPMetricsDataSource.metric_records',
        side_effect=records,
    ), patch(
        'mktxp.collector.bgp_collector.BGPMetricsDataSource.advertised_prefix_counts',
        return_value=None,
    ):
        metrics = list(BGPCollector.collect(router_entry))

    assert not any(metric.name == 'mktxp_bgp_advertised_prefix_count' for metric in metrics)


def test_bgp_collector_exports_configured_connections_without_session_records():
    router_entry = Mock()
    router_entry.config_entry.bgp = True
    router_entry.config_entry.custom_labels = False
    router_entry.router_id = {
        'routerboard_name': 'router-a',
        'routerboard_address': '192.0.2.1',
    }
    connection_record = {
        **router_entry.router_id,
        'name': 'peer-a',
        'remote_address': '192.0.2.2',
        'remote_as': '64502',
    }

    def records(_entry, **kwargs):
        if kwargs.get('path') == 'connection':
            return [connection_record]
        return []

    with patch(
        'mktxp.collector.bgp_collector.BGPMetricsDataSource.metric_records',
        side_effect=records,
    ):
        metrics = list(BGPCollector.collect(router_entry))

    connections_metric = next(
        metric for metric in metrics if metric.name == 'mktxp_bgp_connections'
    )
    assert connections_metric.samples[0].labels['name'] == 'peer-a'


def test_bgp_collector_skips_when_disabled():
    router_entry = Mock()
    router_entry.config_entry.bgp = False

    with patch(
        'mktxp.collector.bgp_collector.BGPMetricsDataSource.metric_records'
    ) as metric_records:
        assert list(BGPCollector.collect(router_entry)) == []

    metric_records.assert_not_called()
