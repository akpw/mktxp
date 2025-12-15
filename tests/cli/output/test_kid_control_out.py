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
from unittest.mock import Mock, patch, MagicMock
import re
from datetime import timedelta
from mktxp.cli.output.kid_control_out import KidControlOutput
from mktxp.flow.processor.output import BaseOutputProcessor


@pytest.fixture
def mock_config_handler():
    ''' Create a mock config_handler with necessary attributes
    '''
    config_handler = Mock()
    config_handler.re_compiled = {}
    return config_handler


@pytest.fixture
def mock_router_entry():
    ''' Create a mock router entry with necessary attributes
    '''
    router_entry = Mock()
    router_entry.config_entry.interface_name_format = 'combined'
    router_entry.dhcp_records = {}
    router_entry.dhcp_record = Mock(return_value=None)
    return router_entry


# Test cases for device sorting scenarios
device_sorting_test_cases = [
    # Case 1: High traffic device should be sorted to top
    (
        "high_traffic_sorting",
        [
            {
                'name': 'Low Traffic', 'user': '', 'mac_address': 'AA:BB:CC:DD:EE:01',
                'ip_address': '192.168.1.10', 'rate_up': '1024', 'rate_down': '2048',
                'idle_time': '10s', 'bytes_up': '1000', 'bytes_down': '2000'
            },
            {
                'name': 'High Traffic', 'user': '', 'mac_address': 'AA:BB:CC:DD:EE:02',
                'ip_address': '192.168.1.11', 'rate_up': '1048576', 'rate_down': '10485760',
                'idle_time': '5s', 'bytes_up': '100000', 'bytes_down': '200000'
            }
        ],
        ['High Traffic', 'Low Traffic']
    ),
    
    # Case 2: Download heavy vs upload heavy
    (
        "download_vs_upload_heavy",
        [
            {
                'name': 'Upload Heavy', 'user': '', 'mac_address': 'DD:BB:CC:DD:EE:01',
                'ip_address': '192.168.1.40', 'rate_up': '10485760', 'rate_down': '1024',
                'idle_time': '5s', 'bytes_up': '1000000', 'bytes_down': '1000'
            },
            {
                'name': 'Download Heavy', 'user': '', 'mac_address': 'DD:BB:CC:DD:EE:02',
                'ip_address': '192.168.1.41', 'rate_up': '1024', 'rate_down': '20971520',
                'idle_time': '3s', 'bytes_up': '1000', 'bytes_down': '2000000'
            }
        ],
        ['Download Heavy', 'Upload Heavy']  # Download heavy has higher total (20MB vs 10MB)
    )
]


@pytest.mark.parametrize("case_name, device_records, expected_order", device_sorting_test_cases)
def test_kid_control_devices_sorting(case_name, device_records, expected_order, mock_router_entry, mock_config_handler, capsys):
    '''
    Test that Kid Control devices are properly sorted by total bandwidth (rate_up + rate_down).
    '''
    with patch('mktxp.datasource.kid_control_device_ds.KidDeviceMetricsDataSource.metric_records') as mock_metrics, \
         patch('mktxp.flow.processor.output.config_handler', mock_config_handler), \
         patch('mktxp.datasource.dhcp_ds.DHCPMetricsDataSource.metric_records'), \
         patch('humanize.naturaldelta') as mock_naturaldelta, \
         patch('os.get_terminal_size') as mock_terminal_size:
        
        mock_metrics.return_value = device_records
        mock_naturaldelta.return_value = "test time"
        mock_terminal_size.return_value = Mock(columns=120)  # Mock terminal width
        
        # Mock regex patterns
        mock_config_handler.re_compiled = {
            'duration_interval_rgx': re.compile(r'((?P<seconds>\d+)s)')
        }
        
        # Capture print output
        KidControlOutput.clients_summary(mock_router_entry)
        captured = capsys.readouterr()
        
        # Verify devices appear in expected order in the output
        output_lines = captured.out.split('\n')
        device_positions = {}
        
        for i, line in enumerate(output_lines):
            for device_name in expected_order:
                # Check for partial matches since table columns may truncate names
                device_key = device_name.split()[0]  # Use first word for matching
                if device_key in line and '|' in line:  # Table row with device name
                    if device_name not in device_positions:  # Take first occurrence
                        device_positions[device_name] = i
        
        # Check that all expected devices were found
        assert len(device_positions) == len(expected_order), f"Not all devices found in output for case {case_name}"
        
        # Verify ordering
        sorted_devices = sorted(device_positions.items(), key=lambda x: x[1])
        actual_order = [device[0] for device in sorted_devices]
        assert actual_order == expected_order, f"Device ordering incorrect for case {case_name}. Expected: {expected_order}, Got: {actual_order}"


@pytest.mark.parametrize("rate_input, expected_display, expected_numeric", [
    # Raw numeric rates
    ("1024", "1 Kbps", 1024),
    ("1048576", "1 Mbps", 1048576),
    ("0", "0 bps", 0),
    ("512", "512 bps", 512),
    # Empty/None handling
    ("", "0 bps", 0),
    (None, "0 bps", 0),
])
def test_rate_parsing_and_formatting(rate_input, expected_display, expected_numeric, mock_config_handler):
    '''
    Test that rate parsing works correctly for both display formatting and numeric sorting.
    '''
    with patch('mktxp.flow.processor.output.config_handler', mock_config_handler):
        # Mock regex patterns
        mock_config_handler.re_compiled = {
            'rates_rgx': re.compile(r'(\d*(?:\.\d*)?)([GgMmKk]bps?)')
        }
        
        # Test parse_bitrates for display
        if rate_input:
            display_result = BaseOutputProcessor.parse_bitrates(rate_input)
            assert display_result == expected_display
        
        # Test parse_numeric_rate for sorting
        numeric_result = BaseOutputProcessor.parse_numeric_rate(rate_input or '0')
        assert numeric_result == expected_numeric


def test_no_kid_control_records(mock_router_entry, capsys):
    '''
    Test behavior when no Kid Control device records are available.
    '''
    with patch('mktxp.datasource.kid_control_device_ds.KidDeviceMetricsDataSource.metric_records') as mock_metrics:
        mock_metrics.return_value = []
        
        KidControlOutput.clients_summary(mock_router_entry)
        captured = capsys.readouterr()
        
        assert "No Kid Control device records" in captured.out


def test_no_kid_control_records(mock_router_entry, capsys):
    '''
    Test behavior when no Kid Control device records are available.
    '''
    with patch('mktxp.datasource.kid_control_device_ds.KidDeviceMetricsDataSource.metric_records') as mock_metrics:
        mock_metrics.return_value = []
        
        KidControlOutput.clients_summary(mock_router_entry)
        captured = capsys.readouterr()
        
        assert "No Kid Control device records" in captured.out


def test_parse_numeric_rate_edge_cases():
    '''
    Test parse_numeric_rate with various edge cases.
    '''
    test_cases = [
        ('', 0),
        ('0', 0),
        (None, 0),
        ('invalid', 0),
        ('1.5 Kbps', 1500),
        ('2.5 Mbps', 2500000),
        ('0.5 Gbps', 500000000),
        ('100 bps', 100),
        ('100', 100),
        ('1000000', 1000000),
    ]
    
    for input_val, expected in test_cases:
        result = BaseOutputProcessor.parse_numeric_rate(input_val)
        assert result == expected, f"Failed for input {input_val}: expected {expected}, got {result}"


def test_zero_rate_bitrates_formatting(mock_config_handler):
    '''
    Test that zero rates are properly handled in parse_bitrates to avoid log domain errors.
    '''
    with patch('mktxp.flow.processor.output.config_handler', mock_config_handler):
        mock_config_handler.re_compiled = {}
        
        # Test zero rate handling
        assert BaseOutputProcessor.parse_bitrates('0') == '0 bps'
        assert BaseOutputProcessor.parse_bitrates(0) == '0 bps'
        
        # Test negative rates (edge case)
        assert BaseOutputProcessor.parse_bitrates('-1') == '0 bps'


def test_combined_rate_calculation_sorting():
    '''
    Test that the combined rate calculation (rate_up + rate_down) works correctly for sorting.
    '''
    # Test case where download heavy device should rank higher than upload heavy
    device1_up = BaseOutputProcessor.parse_numeric_rate('1048576')    # 1MB up
    device1_down = BaseOutputProcessor.parse_numeric_rate('20971520') # 20MB down
    device1_total = device1_up + device1_down                        # 21MB total
    
    device2_up = BaseOutputProcessor.parse_numeric_rate('10485760')   # 10MB up
    device2_down = BaseOutputProcessor.parse_numeric_rate('1048576')  # 1MB down
    device2_total = device2_up + device2_down                        # 11MB total
    
    # Device 1 (download heavy) should have higher total and be sorted first
    assert device1_total > device2_total
    assert device1_total == 22020096  # 1MB + 20MB in bps
    assert device2_total == 11534336  # 10MB + 1MB in bps
