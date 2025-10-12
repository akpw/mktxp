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
from mktxp.collector.base_collector import BaseCollector
from mktxp.cli.config.config import MKTXPConfigKeys

# Case 1: Records with duplicates
records_with_duplicates = [
    {'label1': 'a', 'label2': 'b', 'value': 1},
    {'label1': 'c', 'label2': 'd', 'value': 2},
    {'label1': 'a', 'label2': 'b', 'value': 3},  # Duplicate of the first record
]
expected_with_duplicates = [
    {'label1': 'c', 'label2': 'd', 'value': 2},
    {'label1': 'a', 'label2': 'b', 'value': 3},  # The last one should be kept
]

# Case 2: Records without duplicates
records_without_duplicates = [
    {'label1': 'a', 'label2': 'b', 'value': 1},
    {'label1': 'c', 'label2': 'd', 'value': 2},
    {'label1': 'e', 'label2': 'f', 'value': 3},
]
expected_without_duplicates = records_without_duplicates

# Case 3: Empty list
records_empty = []
expected_empty = []


@pytest.mark.parametrize("input_records, expected_records", [
    (records_with_duplicates, expected_with_duplicates),
    (records_without_duplicates, expected_without_duplicates),
    (records_empty, expected_empty),
])
def test_de_duplicate_records(input_records, expected_records):
    metric_labels = ['label1', 'label2']
    deduplicated = list(BaseCollector._de_duplicate_records(input_records, metric_labels, verbose_reporting = True))

    assert len(deduplicated) == len(expected_records)
    assert sorted(str(d) for d in deduplicated) == sorted(str(d) for d in expected_records)

def test_add_custom_labels():
    """
    Test that _add_custom_labels correctly adds custom label names to metric labels.
    """
    metric_labels = ['interface', 'status']
    router_records = [{
        'interface': 'eth0',
        'status': 'up',
        MKTXPConfigKeys.CUSTOM_LABELS_METADATA_ID: {
            'dc': 'london',
            'rack': 'a1'
        }
    }]
    
    extended_labels = BaseCollector._add_custom_labels(metric_labels, router_records)
    
    assert 'interface' in extended_labels
    assert 'status' in extended_labels
    assert 'dc' in extended_labels
    assert 'rack' in extended_labels
    assert len(extended_labels) == 4

def test_add_custom_labels_no_duplicates():
    """
    Test that _add_custom_labels doesn't add duplicate labels.
    """
    metric_labels = ['interface', 'dc']  # 'dc' already exists
    router_records = [{
        'interface': 'eth0',
        MKTXPConfigKeys.CUSTOM_LABELS_METADATA_ID: {
            'dc': 'london',
            'rack': 'a1'
        }
    }]
    
    extended_labels = BaseCollector._add_custom_labels(metric_labels, router_records)
    
    assert extended_labels.count('dc') == 1  # Should not be duplicated
    assert 'interface' in extended_labels
    assert 'dc' in extended_labels
    assert 'rack' in extended_labels
    assert len(extended_labels) == 3

def test_add_custom_labels_empty_records():
    """
    Test that _add_custom_labels handles empty router records gracefully.
    """
    metric_labels = ['interface', 'status']
    router_records = []
    
    extended_labels = BaseCollector._add_custom_labels(metric_labels, router_records)
    
    assert extended_labels == metric_labels

def test_add_custom_labels_no_metadata():
    """
    Test that _add_custom_labels handles records without custom labels metadata.
    """
    metric_labels = ['interface', 'status']
    router_records = [{
        'interface': 'eth0',
        'status': 'up'
    }]
    
    extended_labels = BaseCollector._add_custom_labels(metric_labels, router_records)
    
    assert extended_labels == metric_labels

def test_gauge_collector_with_custom_labels():
    """
    Integration test: Test that gauge_collector properly incorporates custom labels.
    """
    router_records = [{
        'interface': 'eth0',
        'bytes': 1000,
        MKTXPConfigKeys.ROUTERBOARD_NAME: 'router1',
        MKTXPConfigKeys.ROUTERBOARD_ADDRESS: '192.168.1.1',
        MKTXPConfigKeys.CUSTOM_LABELS_METADATA_ID: {
            'dc': 'london',
            'rack': 'a1'
        }
    }]
    
    metric_labels = ['interface']
    collector = BaseCollector.gauge_collector(
        'test_metric', 
        'Test metric with custom labels', 
        router_records, 
        'bytes',
        metric_labels=metric_labels,
        verbose_reporting=False
    )
    
    # Check that the collector was created with the right labels
    assert collector.name == 'mktxp_test_metric'
    # The labels should include original + router ID + custom labels
    expected_labels = ['interface', 'routerboard_name', 'routerboard_address', 'dc', 'rack']
    assert set(collector._labelnames) == set(expected_labels)

def test_counter_collector_with_custom_labels():
    """
    Integration test: Test that counter_collector properly incorporates custom labels.
    """
    router_records = [{
        'interface': 'eth0',
        'packets': 5000,
        MKTXPConfigKeys.ROUTERBOARD_NAME: 'router1',
        MKTXPConfigKeys.ROUTERBOARD_ADDRESS: '192.168.1.1',
        MKTXPConfigKeys.CUSTOM_LABELS_METADATA_ID: {
            'environment': 'prod',
            'service': 'web'
        }
    }]
    
    metric_labels = ['interface']
    collector = BaseCollector.counter_collector(
        'test_counter', 
        'Test counter with custom labels', 
        router_records, 
        'packets',
        metric_labels=metric_labels,
        verbose_reporting=False
    )
    
    # Check that the collector was created with the right labels
    assert collector.name == 'mktxp_test_counter'
    # The labels should include original + router ID + custom labels
    expected_labels = ['interface', 'routerboard_name', 'routerboard_address', 'environment', 'service']
    assert set(collector._labelnames) == set(expected_labels)

def test_info_collector_with_custom_labels():
    """
    Integration test: Test that info_collector properly incorporates custom labels.
    """
    router_records = [{
        'interface': 'eth0',
        'status': 'up',
        MKTXPConfigKeys.ROUTERBOARD_NAME: 'router1',
        MKTXPConfigKeys.ROUTERBOARD_ADDRESS: '192.168.1.1',
        MKTXPConfigKeys.CUSTOM_LABELS_METADATA_ID: {
            'location': 'datacenter-1',
            'owner': 'team-alpha'
        }
    }]
    
    metric_labels = ['interface', 'status']
    collector = BaseCollector.info_collector(
        'test_info', 
        'Test info with custom labels', 
        router_records,
        metric_labels=metric_labels,
        verbose_reporting=False
    )
    
    # Check that the collector was created with the right labels
    assert collector.name == 'mktxp_test_info'
    # The labels should include original + router ID + custom labels
    expected_labels = ['interface', 'status', 'routerboard_name', 'routerboard_address', 'location', 'owner']
    assert set(collector._labelnames) == set(expected_labels)

def test_gauge_collector_with_generator_input():
    """
    Test that gauge_collector handles generator input correctly without crashing.
    """
    def record_generator(data):
        yield from data

    router_records_data = [{
        'interface': 'eth0',
        'bytes': 1000,
        MKTXPConfigKeys.ROUTERBOARD_NAME: 'router1',
        MKTXPConfigKeys.ROUTERBOARD_ADDRESS: '192.168.1.1',
        MKTXPConfigKeys.CUSTOM_LABELS_METADATA_ID: {'dc': 'london'}
    }]

    # Test with a non-empty generator
    generator = record_generator(router_records_data)
    collector = BaseCollector.gauge_collector(
        'test_metric_gen',
        'Test metric with generator',
        generator,
        'bytes'
    )
    # The main check is that this doesn't raise an exception.
    assert len(collector.samples) == 1

    # Test with an empty generator
    empty_generator = record_generator([])
    collector_empty = BaseCollector.gauge_collector(
        'test_metric_empty_gen',
        'Test metric with empty generator',
        empty_generator,
        'bytes'
    )
    assert len(collector_empty.samples) == 0
