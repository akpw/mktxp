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
from unittest.mock import Mock, patch
from mktxp.collector.user_collector import UserCollector

# MikroTik when format: YYYY-MM-DD HH:MM:SS
# Case 1: Records with duplicates
records_with_duplicates = [
    {'name': 'user1', 'when': '2024-12-18 10:54:02', 'address': 'a1', 'via': 'v1', 'group': 'g1'},
    {'name': 'user2', 'when': '2024-12-18 10:55:02', 'address': 'a2', 'via': 'v2', 'group': 'g2'},
    {'name': 'user1', 'when': '2024-12-18 10:54:02', 'address': 'a1', 'via': 'v1', 'group': 'g1'},  # Duplicate
]
expected_names_1 = {'user1', 'user2'}

# Case 2: No duplicates
records_without_duplicates = [
    {'name': 'user1', 'when': '2024-12-18 10:54:02', 'address': 'a1', 'via': 'v1', 'group': 'g1'},
    {'name': 'user2', 'when': '2024-12-18 10:55:02', 'address': 'a2', 'via': 'v2', 'group': 'g2'},
]
expected_names_2 = {'user1', 'user2'}

# Case 3: All duplicates
records_all_duplicates = [
    {'name': 'user1', 'when': '2024-12-18 10:54:02', 'address': 'a1', 'via': 'v1', 'group': 'g1'},
    {'name': 'user1', 'when': '2024-12-18 10:54:02', 'address': 'a1', 'via': 'v1', 'group': 'g1'},
]
expected_names_3 = {'user1'}


@pytest.mark.parametrize("input_records, expected_sample_count, expected_names", [
    (records_with_duplicates, 2, expected_names_1),
    (records_without_duplicates, 2, expected_names_2),
    (records_all_duplicates, 1, expected_names_3),
])
@patch('mktxp.datasource.user_ds.UserMetricsDataSource.metric_records')
def test_user_collector_deduplicates_records(mock_metric_records, input_records, expected_sample_count, expected_names):
    """
    Tests that the UserCollector correctly de-duplicates records
    from the data source before creating metrics.
    """
    # 1. Setup mock data and objects
    mock_router_entry = Mock()
    mock_router_entry.config_entry.user = True
    mock_metric_records.return_value = input_records

    # 2. Call the collector
    metrics = list(UserCollector.collect(mock_router_entry))

    # 3. Assert the results
    assert len(metrics) == 1
    
    user_metric = metrics[0]
    assert user_metric.name == 'mktxp_active_users_info'
    assert len(user_metric.samples) == expected_sample_count

    # Check that the correct samples are present
    sample_names = {s.labels['name'] for s in user_metric.samples}
    assert sample_names == expected_names
