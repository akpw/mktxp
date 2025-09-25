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
from mktxp.cli.output.address_list_out import AddressListOutput
from mktxp.flow.processor.output import BaseOutputProcessor


@pytest.fixture
def mock_router_entry():
    ''' Create a mock router entry with necessary attributes
    '''
    router_entry = Mock()
    router_entry.router_name = "TestRouter"
    router_entry.config_entry.hostname = "192.168.1.1"
    return router_entry


# Test cases for invalid address list inputs
invalid_input_test_cases = [
    ("empty_string", "", "No address lists specified"),
    ("whitespace_only", "  ,  , ", "No valid address list names provided"),
]


# Test cases for timeout formatting
timeout_format_test_cases = [
    # Zero/None cases
    ("zero_string", "0", ""),
    ("none_value", None, ""),
    # Valid RouterOS format conversions
    ("time_only", "9h7m24s", "09:07:24"),
    ("day_with_time", "1d16h45m4s", "1d 16:45:04"),
    ("week_day_time", "1w4d12h55m42s", "1w4d 12:55:42"),
    # Invalid format
    ("invalid_string", "invalid", "invalid"),
]


# Test cases for RouterOS to UI format conversion
ros_to_ui_conversion_test_cases = [
    ("seconds_only", "30s", "00:00:30"),
    ("minutes_seconds", "5m30s", "00:05:30"),
    ("hours_minutes_seconds", "2h30m45s", "02:30:45"),
    ("day_hours_minutes_seconds", "1d2h30m45s", "1d 02:30:45"),
    ("week_only", "1w", "1w 00:00:00"),
    ("weeks_days", "2w3d", "2w3d 00:00:00"),
]


class TestAddressListOutput:
    
    @pytest.mark.parametrize("case_name, input_string, expected_message", invalid_input_test_cases)
    def test_clients_summary_invalid_inputs(self, case_name, input_string, expected_message, mock_router_entry, capsys):
        ''' Test handling of invalid address list inputs
        '''
        AddressListOutput.clients_summary(mock_router_entry, input_string)
        
        captured = capsys.readouterr()
        assert expected_message in captured.out
        
    def test_parse_address_lists_string(self):
        ''' Test that address list string parsing works correctly
        '''
        # Test with comma-separated values and whitespace
        test_string = "list1, list2 ,  list3  , , list4"
        expected = ["list1", "list2", "list3", "list4"]
        
        result = [name.strip() for name in test_string.split(',') if name.strip()]
        assert result == expected
    
    @pytest.mark.parametrize("case_name, input_value, expected_output", timeout_format_test_cases)
    def test_format_timeout(self, case_name, input_value, expected_output):
        ''' Test timeout formatting with various input values
        '''
        result = AddressListOutput._format_timeout(input_value)
        assert result == expected_output
    
    @pytest.mark.parametrize("case_name, ros_format, expected_ui_format", ros_to_ui_conversion_test_cases)
    def test_convert_ros_to_ui_format(self, case_name, ros_format, expected_ui_format):
        ''' Test RouterOS to UI format conversion function directly
        '''
        result = AddressListOutput._convert_ros_to_ui_format(ros_format)
        assert result == expected_ui_format

    @patch('mktxp.cli.output.address_list_out.AddressListMetricsDataSource.metric_records')
    def test_collect_records_ipv4(self, mock_metric_records, mock_router_entry):
        ''' Test collecting IPv4 records
        '''
        mock_metric_records.return_value = [
            {'list': 'test_list', 'address': '192.168.1.1', 'dynamic': 'false', 'disabled': 'false', 'comment': 'Test'}
        ]
        
        result = AddressListOutput._collect_records(mock_router_entry, ['test_list'], 'ip')
        
        assert len(result) == 1
        mock_metric_records.assert_called_once()
    
    @patch('mktxp.cli.output.address_list_out.AddressListMetricsDataSource.metric_records')
    def test_collect_records_exception(self, mock_metric_records, mock_router_entry, capsys):
        ''' Test handling of exception during record collection
        '''
        mock_metric_records.side_effect = Exception("API Error")
        
        result = AddressListOutput._collect_records(mock_router_entry, ['test_list'], 'ip')
        
        assert result == []
        captured = capsys.readouterr()
        assert "Error getting IP address list info" in captured.out

    @patch('mktxp.cli.output.address_list_out.AddressListOutput._collect_records')
    def test_clients_summary_no_records(self, mock_collect_records, mock_router_entry, capsys):
        ''' Test behavior when no records are found
        '''
        mock_collect_records.return_value = []
        
        AddressListOutput.clients_summary(mock_router_entry, "test_list")
        
        captured = capsys.readouterr()
        assert "No address list entries found" in captured.out


# Test cases for complex display scenarios
display_scenario_test_cases = [
    (
        "ipv4_only",
        {
            'ipv4_records': [{'list': 'blocklist', 'address': '192.168.1.100', 'comment': 'Test IP', 'timeout': '', 'dynamic': 'No', 'disabled': 'No'}],
            'ipv6_records': [],
        },
        ["Address Lists (IPv4)", "Total entries: 1", "blocklist"],
        ["Address Lists (IPv6)"]
    ),
    (
        "both_ipv4_and_ipv6", 
        {
            'ipv4_records': [{'list': 'blocklist', 'address': '192.168.1.100', 'comment': 'IPv4', 'timeout': '', 'dynamic': 'No', 'disabled': 'No'}],
            'ipv6_records': [{'list': 'blocklist', 'address': '2001:db8::1', 'comment': 'IPv6', 'timeout': '', 'dynamic': 'No', 'disabled': 'No'}],
        },
        ["Address Lists (IPv4)", "Address Lists (IPv6)", "192.168.1.100", "2001:db8::1"],
        []
    ),
]


class TestAddressListDisplayScenarios:
    ''' Test complex display scenarios with mocked data
    '''
    
    @pytest.mark.parametrize("scenario_name, test_data, expected_in_output, not_expected_in_output", display_scenario_test_cases)
    @patch('mktxp.cli.output.address_list_out.AddressListOutput._collect_records')
    @patch('os.get_terminal_size')
    def test_display_scenarios(self, mock_terminal_size, mock_collect_records, scenario_name, test_data, expected_in_output, not_expected_in_output, mock_router_entry, capsys):
        ''' Test various display scenarios with different record combinations
        '''
        mock_terminal_size.return_value = Mock(columns=120)
        
        def side_effect(router_entry, requested_lists, ip_version):
            if ip_version == 'ip':
                return test_data['ipv4_records']
            elif ip_version == 'ipv6':
                return test_data['ipv6_records']
            return []
            
        mock_collect_records.side_effect = side_effect
        
        AddressListOutput.clients_summary(mock_router_entry, "blocklist")
        
        captured = capsys.readouterr()
        
        # Check expected content is in output
        for expected_text in expected_in_output:
            assert expected_text in captured.out, f"Expected '{expected_text}' not found in output for scenario {scenario_name}"
            
        # Check content that should not be in output
        for not_expected_text in not_expected_in_output:
            assert not_expected_text not in captured.out, f"Unexpected '{not_expected_text}' found in output for scenario {scenario_name}"
    
    @patch('mktxp.cli.output.address_list_out.AddressListOutput._collect_records')
    @patch('os.get_terminal_size')
    def test_missing_lists_warning(self, mock_terminal_size, mock_collect_records, mock_router_entry, capsys):
        ''' Test warning for missing address lists
        '''
        mock_terminal_size.return_value = Mock(columns=120)
        
        # Only return records for 'existing_list', not 'missing_list'
        ipv4_records = [
            {'list': 'existing_list', 'address': '192.168.1.100', 'comment': '', 'timeout': '', 'dynamic': 'No', 'disabled': 'No'}
        ]
        
        def side_effect(router_entry, requested_lists, ip_version):
            if ip_version == 'ip':
                # Only return records for existing_list, filter out missing_list
                return [r for r in ipv4_records if r['list'] in requested_lists and r['list'] == 'existing_list']
            return []
            
        mock_collect_records.side_effect = side_effect
        
        AddressListOutput.clients_summary(mock_router_entry, "existing_list, missing_list")
        
        captured = capsys.readouterr()
        assert "Warning: The following address lists were not found: missing_list" in captured.out
        assert "existing_list" in captured.out
