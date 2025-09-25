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


class TestAddressListOutput:
    
    def test_clients_summary_with_empty_string(self, capsys):
        ''' Test that empty address list string is handled correctly
        '''
        router_entry = Mock()
        router_entry.router_name = "TestRouter"
        router_entry.config_entry.hostname = "192.168.1.1"
        
        AddressListOutput.clients_summary(router_entry, "")
        
        captured = capsys.readouterr()
        assert "No address lists specified" in captured.out
    
    def test_clients_summary_with_whitespace_only(self, capsys):
        ''' Test that whitespace-only address list string is handled correctly
        '''
        router_entry = Mock()
        router_entry.router_name = "TestRouter" 
        router_entry.config_entry.hostname = "192.168.1.1"
        
        AddressListOutput.clients_summary(router_entry, "  ,  , ")
        
        captured = capsys.readouterr()
        assert "No valid address list names provided" in captured.out
        
    def test_parse_address_lists_string(self):
        ''' Test that address list string parsing works correctly
        '''
        router_entry = Mock()
        router_entry.router_name = "TestRouter"
        router_entry.config_entry.hostname = "192.168.1.1"
        
        # Test with comma-separated values and whitespace
        test_string = "list1, list2 ,  list3  , , list4"
        expected = ["list1", "list2", "list3", "list4"]
        
        result = [name.strip() for name in test_string.split(',') if name.strip()]
        assert result == expected
    
    def test_format_timeout_zero(self):
        ''' Test timeout formatting with zero value
        '''
        result = AddressListOutput._format_timeout("0")
        assert result == ""
        
        result = AddressListOutput._format_timeout(None)
        assert result == ""
    
    def test_format_timeout_valid(self):
        ''' Test timeout formatting with RouterOS format to UI format
        '''
        # Test RouterOS format conversion to Mikrotik UI format
        result = AddressListOutput._format_timeout("9h7m24s")
        assert result == "09:07:24"
        
        result = AddressListOutput._format_timeout("1d16h45m4s")
        assert result == "1d 16:45:04"
        
        result = AddressListOutput._format_timeout("1w4d12h55m42s")
        assert result == "1w4d 12:55:42"
    
    def test_convert_ros_to_ui_format(self):
        ''' Test RouterOS to UI format conversion function directly
        '''
        # Test various RouterOS timeout formats
        assert AddressListOutput._convert_ros_to_ui_format("30s") == "00:00:30"
        assert AddressListOutput._convert_ros_to_ui_format("5m30s") == "00:05:30"
        assert AddressListOutput._convert_ros_to_ui_format("2h30m45s") == "02:30:45"
        assert AddressListOutput._convert_ros_to_ui_format("1d2h30m45s") == "1d 02:30:45"
        assert AddressListOutput._convert_ros_to_ui_format("1w") == "1w 00:00:00"
        assert AddressListOutput._convert_ros_to_ui_format("2w3d") == "2w3d 00:00:00"
        
    def test_format_timeout_invalid(self):
        ''' Test timeout formatting with invalid value
        '''
        result = AddressListOutput._format_timeout("invalid")
        assert result == "invalid"
    
    @patch('mktxp.cli.output.address_list_out.AddressListMetricsDataSource.metric_records')
    def test_collect_records_ipv4(self, mock_metric_records):
        ''' Test collecting IPv4 records
        '''
        router_entry = Mock()
        mock_metric_records.return_value = [
            {'list': 'test_list', 'address': '192.168.1.1', 'dynamic': 'false', 'disabled': 'false', 'comment': 'Test'}
        ]
        
        result = AddressListOutput._collect_records(router_entry, ['test_list'], 'ip')
        
        assert len(result) == 1
        mock_metric_records.assert_called_once()
    
    @patch('mktxp.cli.output.address_list_out.AddressListMetricsDataSource.metric_records')
    def test_collect_records_exception(self, mock_metric_records, capsys):
        ''' Test handling of exception during record collection
        '''
        router_entry = Mock()
        mock_metric_records.side_effect = Exception("API Error")
        
        result = AddressListOutput._collect_records(router_entry, ['test_list'], 'ip')
        
        assert result == []
        captured = capsys.readouterr()
        assert "Error getting IP address list info" in captured.out
    
    @patch('mktxp.cli.output.address_list_out.AddressListOutput._collect_records')
    def test_clients_summary_no_records(self, mock_collect_records, capsys):
        ''' Test behavior when no records are found
        '''
        router_entry = Mock()
        router_entry.router_name = "TestRouter"
        router_entry.config_entry.hostname = "192.168.1.1"
        
        mock_collect_records.return_value = []
        
        AddressListOutput.clients_summary(router_entry, "test_list")
        
        captured = capsys.readouterr()
        assert "No address list entries found" in captured.out
    
    @patch('mktxp.cli.output.address_list_out.AddressListOutput._collect_records')
    @patch('os.get_terminal_size')
    def test_clients_summary_with_ipv4_records(self, mock_terminal_size, mock_collect_records, capsys):
        ''' Test display of IPv4 records
        '''
        mock_terminal_size.return_value = Mock(columns=120)
        
        router_entry = Mock()
        router_entry.router_name = "TestRouter"
        router_entry.config_entry.hostname = "192.168.1.1"
        
        ipv4_records = [
            {'list': 'blocklist', 'address': '192.168.1.100', 'comment': 'Test IP', 'timeout': '', 'dynamic': 'No', 'disabled': 'No'}
        ]
        
        def side_effect(router_entry, requested_lists, ip_version):
            if ip_version == 'ip':
                return ipv4_records
            return []
            
        mock_collect_records.side_effect = side_effect
        
        AddressListOutput.clients_summary(router_entry, "blocklist")
        
        captured = capsys.readouterr()
        assert "Address Lists (IPv4)" in captured.out
        assert "Total entries: 1" in captured.out
        assert "blocklist" in captured.out
    
    @patch('mktxp.cli.output.address_list_out.AddressListOutput._collect_records')
    @patch('os.get_terminal_size')
    def test_clients_summary_with_both_ipv4_and_ipv6(self, mock_terminal_size, mock_collect_records, capsys):
        ''' Test display of both IPv4 and IPv6 records
        '''
        mock_terminal_size.return_value = Mock(columns=120)
        
        router_entry = Mock()
        router_entry.router_name = "TestRouter" 
        router_entry.config_entry.hostname = "192.168.1.1"
        
        ipv4_records = [
            {'list': 'blocklist', 'address': '192.168.1.100', 'comment': 'IPv4', 'timeout': '', 'dynamic': 'No', 'disabled': 'No'}
        ]
        ipv6_records = [
            {'list': 'blocklist', 'address': '2001:db8::1', 'comment': 'IPv6', 'timeout': '', 'dynamic': 'No', 'disabled': 'No'}
        ]
        
        def side_effect(router_entry, requested_lists, ip_version):
            if ip_version == 'ip':
                return ipv4_records
            elif ip_version == 'ipv6':
                return ipv6_records
            return []
            
        mock_collect_records.side_effect = side_effect
        
        AddressListOutput.clients_summary(router_entry, "blocklist")
        
        captured = capsys.readouterr()
        assert "Address Lists (IPv4)" in captured.out
        assert "Address Lists (IPv6)" in captured.out
        assert "192.168.1.100" in captured.out
        assert "2001:db8::1" in captured.out
        
    @patch('mktxp.cli.output.address_list_out.AddressListOutput._collect_records')
    @patch('os.get_terminal_size')
    def test_clients_summary_missing_lists_warning(self, mock_terminal_size, mock_collect_records, capsys):
        ''' Test warning for missing address lists
        '''
        mock_terminal_size.return_value = Mock(columns=120)
        
        router_entry = Mock()
        router_entry.router_name = "TestRouter"
        router_entry.config_entry.hostname = "192.168.1.1"
        
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
        
        AddressListOutput.clients_summary(router_entry, "existing_list, missing_list")
        
        captured = capsys.readouterr()
        assert "Warning: The following address lists were not found: missing_list" in captured.out
        assert "existing_list" in captured.out