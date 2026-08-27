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
from mktxp.flow.processor.output import BaseOutputProcessor
from mktxp.cli.output.capsman_out import CapsmanOutput
from mktxp.cli.output.dhcp_out import DHCPOutput
from mktxp.cli.options import MKTXPOptionsParser


@pytest.fixture
def mock_router_entry():
    router_entry = Mock()
    router_entry.router_name = "TestRouter"
    router_entry.config_entry.hostname = "192.168.1.1"
    router_entry.config_entry.interface_name_format = "name"
    router_entry.wireless_type = "capsman"
    return router_entry


class TestPatternParsing:
    def test_parse_patterns_empty(self):
        assert BaseOutputProcessor.parse_patterns(None) == []
        assert BaseOutputProcessor.parse_patterns("") == []
        assert BaseOutputProcessor.parse_patterns("   ") == []
        assert BaseOutputProcessor.parse_patterns(";;;") == []

    def test_parse_patterns_single(self):
        assert BaseOutputProcessor.parse_patterns("wlan-5G") == ["wlan-5G"]
        assert BaseOutputProcessor.parse_patterns("  Pro  ") == ["Pro"]

    def test_parse_patterns_semicolon_delimited(self):
        assert BaseOutputProcessor.parse_patterns("wlan-5G;Pro") == ["wlan-5G", "Pro"]
        assert BaseOutputProcessor.parse_patterns("wlan-5G; Pro; 10.0.0") == ["wlan-5G", "Pro", "10.0.0"]

    def test_parse_patterns_list_input(self):
        assert BaseOutputProcessor.parse_patterns(["wlan-5G;Pro", "10.0.0"]) == ["wlan-5G", "Pro", "10.0.0"]


class TestRecordMatching:
    @pytest.fixture
    def sample_record(self):
        return {
            'dhcp_name': 'Device-Alpha-Pro',
            'dhcp_address': '10.0.0.15',
            'mac_address': 'AA:BB:CC:11:22:33',
            'rx_signal': '-65',
            'interface': 'wlan-5G-1',
            'ssid': 'Corporate-5G',
            'tx_rate': '866 Mbps',
            'rx_rate': '702 Mbps',
            'uptime': '11 days'
        }

    def test_match_record_no_filters(self, sample_record):
        assert BaseOutputProcessor.match_record(sample_record) is True
        assert BaseOutputProcessor.match_record(sample_record, include_patterns=None, exclude_patterns=None) is True

    def test_match_record_include_substring(self, sample_record):
        assert BaseOutputProcessor.match_record(sample_record, include_patterns="Pro") is True
        assert BaseOutputProcessor.match_record(sample_record, include_patterns="wlan-5G") is True
        assert BaseOutputProcessor.match_record(sample_record, include_patterns="10.0.0") is True
        assert BaseOutputProcessor.match_record(sample_record, include_patterns="Corporate-5G") is True
        assert BaseOutputProcessor.match_record(sample_record, include_patterns="NonExistent") is False

    def test_match_record_include_semicolon_or_logic(self, sample_record):
        assert BaseOutputProcessor.match_record(sample_record, include_patterns="NonExistent;Pro") is True
        assert BaseOutputProcessor.match_record(sample_record, include_patterns="wlan-5G;Beta") is True
        assert BaseOutputProcessor.match_record(sample_record, include_patterns="Foo;Bar;Baz") is False

    def test_match_record_exclude_logic(self, sample_record):
        assert BaseOutputProcessor.match_record(sample_record, exclude_patterns="2.4GHz") is True
        assert BaseOutputProcessor.match_record(sample_record, exclude_patterns="wlan-5G") is False
        assert BaseOutputProcessor.match_record(sample_record, exclude_patterns="Guest;Pro") is False

    def test_match_record_include_and_exclude_combined(self, sample_record):
        assert BaseOutputProcessor.match_record(sample_record, include_patterns="wlan-5G;Pro", exclude_patterns="2.4GHz") is True
        assert BaseOutputProcessor.match_record(sample_record, include_patterns="wlan-5G;Pro", exclude_patterns="Alpha") is False

    def test_match_record_wildcard_globs(self, sample_record):
        assert BaseOutputProcessor.match_record(sample_record, include_patterns="*5G*") is True
        assert BaseOutputProcessor.match_record(sample_record, include_patterns="10.0.*") is True
        assert BaseOutputProcessor.match_record(sample_record, include_patterns="AA:BB:*") is True
        assert BaseOutputProcessor.match_record(sample_record, exclude_patterns="*2.4*") is True
        assert BaseOutputProcessor.match_record(sample_record, exclude_patterns="*5G*") is False


class TestOutputTableTerminalFallback:
    def test_output_table_tty(self):
        with patch('os.get_terminal_size') as mock_term:
            mock_term.return_value.columns = 120
            table = BaseOutputProcessor.output_table(BaseOutputProcessor.OutputCapsmanEntry)
            assert table._max_width == 120

    def test_output_table_non_tty_pipe(self):
        with patch('os.get_terminal_size', side_effect=OSError("Inappropriate ioctl for device")):
            table = BaseOutputProcessor.output_table(BaseOutputProcessor.OutputCapsmanEntry)
            assert table._max_width == 0


class TestOutputIntegration:
    @patch('mktxp.cli.output.capsman_out.CapsmanRegistrationsMetricsDataSource.metric_records')
    @patch('mktxp.flow.processor.output.BaseOutputProcessor.resolve_dhcp')
    def test_capsman_output_filtering(self, mock_resolve, mock_metric_records, mock_router_entry, capsys):
        mock_metric_records.return_value = [
            {'interface': 'wlan-5G-1', 'ssid': 'Corporate-5G', 'mac_address': 'AA:BB:CC:11:22:33', 'rx_signal': '-65dBm', 'uptime': '11d', 'tx_rate': '866000000', 'rx_rate': '702000000', 'dhcp_name': 'Device-Alpha-Pro', 'dhcp_address': '10.0.0.15'},
            {'interface': 'wlan-2.4G-1', 'ssid': 'Corporate-2G', 'mac_address': 'AA:BB:CC:44:55:66', 'rx_signal': '-72dBm', 'uptime': '10h', 'tx_rate': '72000000', 'rx_rate': '72000000', 'dhcp_name': 'Device-Beta-IoT', 'dhcp_address': '10.0.0.100'},
        ]
        CapsmanOutput.clients_summary(mock_router_entry, include="wlan-5G;Pro", exclude="2.4G")
        captured = capsys.readouterr().out
        assert "Device-Alpha-Pro" in captured
        assert "Device-Beta-IoT" not in captured
        assert "Matching CAPsMAN clients: 1 (Total connected: 2)" in captured

    @patch('mktxp.cli.output.dhcp_out.DHCPMetricsDataSource.metric_records')
    def test_dhcp_output_filtering(self, mock_metric_records, mock_router_entry, capsys):
        mock_metric_records.return_value = [
            {'host_name': 'Office-Workstation', 'comment': '', 'active_address': '192.168.1.50', 'address': '192.168.1.50', 'mac_address': '11:22:33:44:55:66', 'server': 'lan', 'expires_after': '1d'},
            {'host_name': 'Guest-Tablet', 'comment': '', 'active_address': '10.0.0.20', 'address': '10.0.0.20', 'mac_address': 'AA:BB:CC:DD:EE:FF', 'server': 'guest', 'expires_after': '2h'},
        ]
        DHCPOutput.clients_summary(mock_router_entry, include="192.168.1")
        captured = capsys.readouterr().out
        assert "Office-Workstation" in captured
        assert "Guest-Tablet" not in captured
        assert "Matching DHCP clients: 1 (Total: 2)" in captured
