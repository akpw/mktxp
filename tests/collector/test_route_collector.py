from unittest.mock import Mock, patch

from mktxp.collector.route_collector import RouteCollector


def test_route_collector_exports_total_and_active_metrics_for_ipv4_and_ipv6():
    router_id = {
        'routerboard_name': 'router-a',
        'routerboard_address': '192.0.2.1',
    }
    router_entry = Mock()
    router_entry.config_entry.route = True
    router_entry.config_entry.ipv6_route = True
    router_entry.config_entry.custom_labels = False
    router_entry.router_id = router_id

    v4_counts = {
        'total_routes': 17,
        'active_routes': 14,
        'routes_per_protocol': {'static': 6, 'ospf': 5},
        'active_routes_per_protocol': {'static': 3, 'ospf': 5},
    }
    v6_counts = {
        'total_routes': 10,
        'active_routes': 8,
        'routes_per_protocol': {'static': 4},
        'active_routes_per_protocol': {'static': 2},
    }

    with patch(
        'mktxp.collector.route_collector.RouteMetricsDataSource.metric_records',
        side_effect=[v4_counts, v6_counts],
    ):
        metrics = {m.name: m for m in RouteCollector.collect(router_entry)}

    assert set(metrics.keys()) == {
        'mktxp_routes_total_routes',
        'mktxp_routes_active_routes',
        'mktxp_routes_protocol_count',
        'mktxp_routes_active_protocol_count',
        'mktxp_routes_total_routes_ipv6',
        'mktxp_routes_active_routes_ipv6',
        'mktxp_routes_protocol_count_ipv6',
        'mktxp_routes_active_protocol_count_ipv6',
    }

    assert metrics['mktxp_routes_total_routes'].samples[0].value == 17
    assert metrics['mktxp_routes_active_routes'].samples[0].value == 14
    v4_active_proto = {
        s.labels['protocol']: s.value
        for s in metrics['mktxp_routes_active_protocol_count'].samples
    }
    assert v4_active_proto == {'static': 3, 'ospf': 5}

    assert metrics['mktxp_routes_total_routes_ipv6'].samples[0].value == 10
    assert metrics['mktxp_routes_active_routes_ipv6'].samples[0].value == 8
    v6_active_proto = {
        s.labels['protocol']: s.value
        for s in metrics['mktxp_routes_active_protocol_count_ipv6'].samples
    }
    assert v6_active_proto == {'static': 2}
