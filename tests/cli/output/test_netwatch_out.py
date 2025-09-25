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
from mktxp.cli.output.netwatch_out import NetwatchOutput
from mktxp.flow.processor.output import BaseOutputProcessor


@pytest.fixture
def mock_router_entry():
    ''' Create a mock router entry with necessary attributes
    '''
    router_entry = Mock()
    router_entry.router_name = "TestRouter"
    router_entry.config_entry.hostname = "192.168.1.1"
    return router_entry


class TestNetwatchOutput:

    @patch('mktxp.cli.output.netwatch_out.NetwatchMetricsDataSource.metric_records')
    def test_collect_records_success(self, mock_metric_records, mock_router_entry):
        ''' Test successful record collection
        '''
        mock_metric_records.return_value = [
            {
                'name': 'Test Host', 'host': '192.168.1.100', 'comment': 'Test',
                'status': 'up', 'type': 'icmp', 'since': 'jan/01/2023 12:00:00', 
                'timeout': '1s', 'interval': '1m'
            }
        ]
        
        result = NetwatchOutput._collect_records(mock_router_entry)
        
        assert len(result) == 1
        mock_metric_records.assert_called_once()
    
    @patch('mktxp.cli.output.netwatch_out.NetwatchMetricsDataSource.metric_records')
    def test_collect_records_exception(self, mock_metric_records, mock_router_entry, capsys):
        ''' Test handling of exception during record collection
        '''
        mock_metric_records.side_effect = Exception("API Error")
        
        result = NetwatchOutput._collect_records(mock_router_entry)
        
        assert result == []
        captured = capsys.readouterr()
        assert "Error getting netwatch info" in captured.out

    @patch('mktxp.cli.output.netwatch_out.NetwatchOutput._collect_records')
    def test_clients_summary_no_records(self, mock_collect_records, mock_router_entry, capsys):
        ''' Test behavior when no records are found
        '''
        mock_collect_records.return_value = []
        
        NetwatchOutput.clients_summary(mock_router_entry)
        
        captured = capsys.readouterr()
        assert "No netwatch entries found" in captured.out


# Test cases for display scenarios
display_scenario_test_cases = [
    (
        "all_up",
        [
            {'name': 'Host1', 'host': '192.168.1.1', 'comment': 'Test1', 'status': 'Up', 'type': 'icmp', 'since': 'jan/01/2023', 'timeout': '1s', 'interval': '1m'},
            {'name': 'Host2', 'host': '192.168.1.2', 'comment': 'Test2', 'status': 'Up', 'type': 'icmp', 'since': 'jan/01/2023', 'timeout': '1s', 'interval': '1m'},
        ],
        ["Netwatch Entries:", "Total entries: 2", "Up: 2", "Down: 0", "Host1", "Host2"],
        []
    ),
    (
        "mixed_status",
        [
            {'name': 'Host1', 'host': '192.168.1.1', 'comment': 'Test1', 'status': 'Up', 'type': 'icmp', 'since': 'jan/01/2023', 'timeout': '1s', 'interval': '1m'},
            {'name': 'Host2', 'host': '192.168.1.2', 'comment': 'Test2', 'status': 'Down', 'type': 'icmp', 'since': 'jan/01/2023', 'timeout': '1s', 'interval': '1m'},
        ],
        ["Netwatch Entries:", "Total entries: 2", "Up: 1", "Down: 1", "Host1", "Host2"],
        []
    ),
    (
        "all_down", 
        [
            {'name': 'Host1', 'host': '192.168.1.1', 'comment': 'Test1', 'status': 'Down', 'type': 'icmp', 'since': 'jan/01/2023', 'timeout': '1s', 'interval': '1m'},
        ],
        ["Netwatch Entries:", "Total entries: 1", "Up: 0", "Down: 1", "Host1"],
        []
    ),
]


class TestNetwatchDisplayScenarios:
    '''Test complex display scenarios with mocked data'''
    
    @pytest.mark.parametrize("scenario_name, test_records, expected_in_output, not_expected_in_output", display_scenario_test_cases)
    @patch('mktxp.cli.output.netwatch_out.NetwatchOutput._collect_records')
    @patch('os.get_terminal_size')
    def test_display_scenarios(self, mock_terminal_size, mock_collect_records, scenario_name, test_records, expected_in_output, not_expected_in_output, mock_router_entry, capsys):
        ''' Test various display scenarios with different record combinations
        '''
        mock_terminal_size.return_value = Mock(columns=120)
        mock_collect_records.return_value = test_records
        
        NetwatchOutput.clients_summary(mock_router_entry)
        
        captured = capsys.readouterr()
        
        # Check expected content is in output
        for expected_text in expected_in_output:
            assert expected_text in captured.out, f"Expected '{expected_text}' not found in output for scenario {scenario_name}"
            
        # Check content that should not be in output
        for not_expected_text in not_expected_in_output:
            assert not_expected_text not in captured.out, f"Unexpected '{not_expected_text}' found in output for scenario {scenario_name}"
    
    @patch('mktxp.cli.output.netwatch_out.NetwatchOutput._collect_records')
    @patch('os.get_terminal_size')
    def test_record_sorting(self, mock_terminal_size, mock_collect_records, mock_router_entry, capsys):
        ''' Test that records are properly sorted by name then host
        '''
        mock_terminal_size.return_value = Mock(columns=120)
        
        # Unsorted test records
        test_records = [
            {'name': 'ZHost', 'host': '192.168.1.3', 'comment': 'Test3', 'status': 'Up', 'type': 'icmp', 'since': 'jan/01/2023', 'timeout': '1s', 'interval': '1m'},
            {'name': 'AHost', 'host': '192.168.1.2', 'comment': 'Test2', 'status': 'Up', 'type': 'icmp', 'since': 'jan/01/2023', 'timeout': '1s', 'interval': '1m'},
            {'name': 'AHost', 'host': '192.168.1.1', 'comment': 'Test1', 'status': 'Up', 'type': 'icmp', 'since': 'jan/01/2023', 'timeout': '1s', 'interval': '1m'},
        ]
        
        mock_collect_records.return_value = test_records
        
        NetwatchOutput.clients_summary(mock_router_entry)
        
        captured = capsys.readouterr()
        
        # Find positions of each host in the output
        lines = captured.out.split('\n')
        positions = {}
        for i, line in enumerate(lines):
            if 'AHost' in line and '192.168.1.1' in line:
                positions['AHost_1'] = i
            elif 'AHost' in line and '192.168.1.2' in line:
                positions['AHost_2'] = i
            elif 'ZHost' in line:
                positions['ZHost'] = i
        
        # Check sorting: AHost entries should come before ZHost
        # and within AHost entries, 192.168.1.1 should come before 192.168.1.2
        assert len(positions) == 3, "Not all hosts found in output"
        assert positions['AHost_1'] < positions['AHost_2'], "AHost entries not sorted correctly by host"
        assert positions['AHost_2'] < positions['ZHost'], "Entries not sorted correctly by name"