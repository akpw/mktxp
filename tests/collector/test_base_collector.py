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
