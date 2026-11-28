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
            'ls-retransmits': '0',
            'ls-requests': '1',
            'db-summaries': '2',
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
            'ls-retransmits': '3',
            'ls-requests': '0',
            'db-summaries': '0',
        },
    ]
    router_entry.api_connection.router_api.return_value.get_resource.return_value.get.return_value = raw_neighbors

    with patch(
        'mktxp.datasource.ospf_ds.BaseDSProcessor.count_records',
        return_value=18,
    ):
        metrics = {m.name: m for m in OSPFCollector.collect(router_entry)}

    assert list(metrics.keys()) == [
        'mktxp_ospf_neighbors',
        'mktxp_ospf_neighbor_state',
        'mktxp_ospf_neighbor_full',
        'mktxp_ospf_neighbor_state_changes',
        'mktxp_ospf_neighbor_adjacency',
        'mktxp_ospf_neighbor_ls_retransmits',
        'mktxp_ospf_neighbor_ls_requests',
        'mktxp_ospf_neighbor_db_summaries',
        'mktxp_ospf_area_neighbors_count',
        'mktxp_ospf_lsa_count',
    ]

    info_samples = metrics['mktxp_ospf_neighbors'].samples
    assert info_samples[0].labels['state'] == 'Full'
    assert info_samples[0].labels['area'] == 'backbone'
    assert info_samples[0].labels['interface'] == ''
    assert info_samples[1].labels['state'] == '2-Way'

    state_samples = {s.labels['router_id']: s.value for s in metrics['mktxp_ospf_neighbor_state'].samples}
    assert state_samples == {'10.21.0.2': 7, '10.21.0.3': 3}

    full_samples = {s.labels['router_id']: s.value for s in metrics['mktxp_ospf_neighbor_full'].samples}
    assert full_samples == {'10.21.0.2': '1', '10.21.0.3': '0'}

    changes_samples = {s.labels['router_id']: s.value for s in metrics['mktxp_ospf_neighbor_state_changes'].samples}
    assert changes_samples == {'10.21.0.2': '6', '10.21.0.3': '2'}

    adjacency_samples = {s.labels['router_id']: float(s.value) for s in metrics['mktxp_ospf_neighbor_adjacency'].samples}
    assert adjacency_samples == {'10.21.0.2': 3600000.0, '10.21.0.3': 0.0}

    retrans_samples = {s.labels['router_id']: s.value for s in metrics['mktxp_ospf_neighbor_ls_retransmits'].samples}
    assert retrans_samples == {'10.21.0.2': '0', '10.21.0.3': '3'}

    req_samples = {s.labels['router_id']: s.value for s in metrics['mktxp_ospf_neighbor_ls_requests'].samples}
    assert req_samples == {'10.21.0.2': '1', '10.21.0.3': '0'}

    db_samples = {s.labels['router_id']: s.value for s in metrics['mktxp_ospf_neighbor_db_summaries'].samples}
    assert db_samples == {'10.21.0.2': '2', '10.21.0.3': '0'}

    area_sample = metrics['mktxp_ospf_area_neighbors_count'].samples[0]
    assert area_sample.value == 2
    assert area_sample.labels == {
        **router_id,
        'instance': 'ospf-instance-1',
        'area': 'backbone',
    }

    assert metrics['mktxp_ospf_lsa_count'].samples[0].value == 18
    assert metrics['mktxp_ospf_lsa_count'].samples[0].labels == router_id


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

    # ROS 6 neighbor records include 'interface' and omit 'area'
    raw_neighbors = [
        {
            'instance': 'default',
            'interface': 'ether2',
            'router-id': '10.1.100.90',
            'address': '10.1.1.122',
            'state': 'Full',
            'state-changes': '4',
            'ls-retransmits': '0',
            'ls-requests': '0',
            'db-summaries': '0',
            'adjacency': '2m',
        }
    ]
    router_entry.api_connection.router_api.return_value.get_resource.return_value.get.return_value = raw_neighbors

    with patch(
        'mktxp.datasource.ospf_ds.BaseDSProcessor.count_records',
        return_value=None,
    ):
        metrics = {m.name: m for m in OSPFCollector.collect(router_entry)}

    assert list(metrics.keys()) == [
        'mktxp_ospf_neighbors',
        'mktxp_ospf_neighbor_state',
        'mktxp_ospf_neighbor_full',
        'mktxp_ospf_neighbor_state_changes',
        'mktxp_ospf_neighbor_adjacency',
        'mktxp_ospf_neighbor_ls_retransmits',
        'mktxp_ospf_neighbor_ls_requests',
        'mktxp_ospf_neighbor_db_summaries',
    ]
    assert metrics['mktxp_ospf_neighbors'].samples[0].labels['area'] == ''
    assert metrics['mktxp_ospf_neighbors'].samples[0].labels['interface'] == 'ether2'
    assert metrics['mktxp_ospf_neighbor_state'].samples[0].value == 7
    assert metrics['mktxp_ospf_neighbor_full'].samples[0].value == '1'
    assert float(metrics['mktxp_ospf_neighbor_adjacency'].samples[0].value) == 120000.0


def test_ospf_collector_exports_ros7_omitted_ls_counters_as_zero():
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

    # ROS 7 omits ls-retransmits / ls-requests / db-summaries while they are 0
    raw_neighbors = [
        {
            'instance': 'ospf-instance-1',
            'area': 'backbone',
            'interface': 'gre-tunnel1',
            'router-id': '198.51.100.1',
            'address': '203.0.113.1',
            'state': 'Full',
            'state-changes': '5',
            'adjacency': '3d4h',
        },
        {
            'instance': 'ospf-instance-1',
            'area': 'backbone',
            'interface': 'gre-tunnel2',
            'router-id': '198.51.100.2',
            'address': '203.0.113.5',
            'state': 'Full',
            'state-changes': '5',
            'adjacency': '3d4h',
            'ls-retransmits': '7',
        },
    ]
    router_entry.api_connection.router_api.return_value.get_resource.return_value.get.return_value = raw_neighbors

    with patch(
        'mktxp.datasource.ospf_ds.BaseDSProcessor.count_records',
        return_value=None,
    ):
        metrics = {m.name: m for m in OSPFCollector.collect(router_entry)}

    def by_interface(name):
        return {s.labels['interface']: s.value for s in metrics[name].samples}

    assert by_interface('mktxp_ospf_neighbor_ls_retransmits') == {'gre-tunnel1': '0', 'gre-tunnel2': '7'}
    assert by_interface('mktxp_ospf_neighbor_ls_requests') == {'gre-tunnel1': '0', 'gre-tunnel2': '0'}
    assert by_interface('mktxp_ospf_neighbor_db_summaries') == {'gre-tunnel1': '0', 'gre-tunnel2': '0'}


def test_ospf_collector_skips_when_disabled():
    router_entry = Mock()
    router_entry.config_entry.ospf = False

    with patch(
        'mktxp.collector.ospf_collector.OSPFMetricsDataSource.neighbor_records'
    ) as neighbor_records:
        assert list(OSPFCollector.collect(router_entry)) == []

    neighbor_records.assert_not_called()
