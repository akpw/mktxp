from unittest.mock import Mock, call, patch

from mktxp.datasource.route_ds import RouteMetricsDataSource


def test_route_datasource_counts_total_and_active_routes_ipv4():
    router_entry = Mock()

    with patch(
        'mktxp.datasource.route_ds.BaseDSProcessor.count_records',
        side_effect=[17, 14, 6, 3, 5, 5],
    ) as count_records:
        result = RouteMetricsDataSource.metric_records(
            router_entry,
            metric_labels=['static', 'ospf'],
        )

    assert result == {
        'total_routes': 17,
        'active_routes': 14,
        'routes_per_protocol': {'static': 6, 'ospf': 5},
        'active_routes_per_protocol': {'static': 3, 'ospf': 5},
    }
    assert count_records.call_args_list == [
        call(router_entry, api_path='/ip/route'),
        call(router_entry, api_path='/ip/route', api_query={'active': 'yes'}),
        call(router_entry, api_path='/ip/route', api_query={'static': 'yes'}),
        call(router_entry, api_path='/ip/route', api_query={'static': 'yes', 'active': 'yes'}),
        call(router_entry, api_path='/ip/route', api_query={'ospf': 'yes'}),
        call(router_entry, api_path='/ip/route', api_query={'ospf': 'yes', 'active': 'yes'}),
    ]


def test_route_datasource_counts_total_and_active_routes_ipv6():
    router_entry = Mock()

    with patch(
        'mktxp.datasource.route_ds.BaseDSProcessor.count_records',
        side_effect=[10, 8, 4, 2],
    ) as count_records:
        result = RouteMetricsDataSource.metric_records(
            router_entry,
            metric_labels=['static'],
            ipv6=True,
        )

    assert result == {
        'total_routes': 10,
        'active_routes': 8,
        'routes_per_protocol': {'static': 4},
        'active_routes_per_protocol': {'static': 2},
    }
    assert count_records.call_args_list[0] == call(router_entry, api_path='/ipv6/route')
    assert count_records.call_args_list[1] == call(
        router_entry, api_path='/ipv6/route', api_query={'active': 'yes'}
    )


def test_route_datasource_returns_none_on_count_error():
    router_entry = Mock()

    with patch(
        'mktxp.datasource.route_ds.BaseDSProcessor.count_records',
        side_effect=[10, None],
    ):
        assert RouteMetricsDataSource.metric_records(router_entry, metric_labels=['static']) is None
