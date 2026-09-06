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
from mktxp.cli.output.tables import output_table, OutputCapsmanEntry
from mktxp.utils.filtering import parse_patterns, match_record, match_wireless_record, match_dhcp_record
from mktxp.cli.output.capsman_out import CapsmanOutput
from mktxp.cli.output.dhcp_out import DHCPOutput
from mktxp.cli.output.conn_stats_out import ConnectionsStatsOutput
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
        assert parse_patterns(None) == []
        assert parse_patterns("") == []
        assert parse_patterns("   ") == []
        assert parse_patterns(";;;") == []

    def test_parse_patterns_single(self):
        assert parse_patterns("wlan-5G") == ["wlan-5G"]
        assert parse_patterns("  Pro  ") == ["Pro"]

    def test_parse_patterns_semicolon_delimited(self):
        assert parse_patterns("wlan-5G;Pro") == ["wlan-5G", "Pro"]
        assert parse_patterns("wlan-5G; Pro; 10.0.0") == ["wlan-5G", "Pro", "10.0.0"]

    def test_parse_patterns_list_input(self):
        assert parse_patterns(["wlan-5G;Pro", "10.0.0"]) == ["wlan-5G", "Pro", "10.0.0"]


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
        assert match_record(sample_record) is True
        assert match_record(sample_record, include_patterns=None, exclude_patterns=None) is True

    def test_match_record_include_substring(self, sample_record):
        assert match_record(sample_record, include_patterns="Pro") is True
        assert match_record(sample_record, include_patterns="wlan-5G") is True
        assert match_record(sample_record, include_patterns="10.0.0") is True
        assert match_record(sample_record, include_patterns="Corporate-5G") is True
        assert match_record(sample_record, include_patterns="NonExistent") is False

    def test_match_record_include_semicolon_or_logic(self, sample_record):
        assert match_record(sample_record, include_patterns="NonExistent;Pro") is True
        assert match_record(sample_record, include_patterns="wlan-5G;Beta") is True
        assert match_record(sample_record, include_patterns="Foo;Bar;Baz") is False

    def test_match_record_exclude_logic(self, sample_record):
        assert match_record(sample_record, exclude_patterns="2.4GHz") is True
        assert match_record(sample_record, exclude_patterns="wlan-5G") is False
        assert match_record(sample_record, exclude_patterns="Guest;Pro") is False

    def test_match_record_include_and_exclude_combined(self, sample_record):
        assert match_record(sample_record, include_patterns="wlan-5G;Pro", exclude_patterns="2.4GHz") is True
        assert match_record(sample_record, include_patterns="wlan-5G;Pro", exclude_patterns="Alpha") is False

    def test_match_record_wildcard_globs(self, sample_record):
        assert match_record(sample_record, include_patterns="*5G*") is True
        assert match_record(sample_record, include_patterns="10.0.*") is True
        assert match_record(sample_record, include_patterns="AA:BB:*") is True
        assert match_record(sample_record, exclude_patterns="*2.4*") is True
        assert match_record(sample_record, exclude_patterns="*5G*") is False


class TestOutputTableTerminalFallback:
    def test_output_table_tty(self):
        with patch('os.get_terminal_size') as mock_term:
            mock_term.return_value.columns = 120
            table = output_table(OutputCapsmanEntry)
            assert table._max_width == 120

    def test_output_table_non_tty_pipe(self):
        with patch('os.get_terminal_size', side_effect=OSError("Inappropriate ioctl for device")):
            table = output_table(OutputCapsmanEntry)
            assert table._max_width == 0


class TestOutputIntegration:
    @patch('mktxp.cli.output.capsman_out.CapsmanRegistrationsMetricsDataSource.metric_records')
    @patch('mktxp.flow.processor.enrichment.resolve_dhcp')
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


class TestDHCPDiagnostics:
    @pytest.fixture
    def sample_leases(self):
        return [
            {
                'host_name': 'Server-Main',
                'comment': 'Core Infrastructure',
                'mac_address': 'AA:00:00:00:00:01',
                'address': '192.168.1.10',
                'active_address': '192.168.1.10',
                'server': 'lan',
                'expires_after': '1d',
                'dynamic': 'false',
                'status': 'bound',
            },
            {
                'host_name': 'Guest-Phone',
                'comment': '',
                'mac_address': 'AA:00:00:00:00:02',
                'address': '192.168.1.50',
                'active_address': '192.168.1.50',
                'server': 'lan',
                'expires_after': '6h',
                'dynamic': 'true',
                'status': 'bound',
            },
            {
                'host_name': '',
                'comment': 'AP Backyard',
                'mac_address': 'AA:00:00:00:00:03',
                'address': '192.168.1.20',
                'active_address': '',
                'server': 'lan',
                'expires_after': '',
                'dynamic': 'false',
                'status': 'waiting',
            },
            {
                'host_name': '',
                'comment': '',
                'mac_address': 'AA:00:00:00:00:99',
                'address': '192.168.1.99',
                'active_address': '192.168.1.99',
                'server': 'lan',
                'expires_after': '12h',
                'dynamic': 'true',
                'status': 'bound',
            },
            {
                'host_name': '',
                'comment': '',
                'mac_address': 'AA:00:00:00:00:98',
                'address': '192.168.1.98',
                'active_address': '',
                'server': 'lan',
                'expires_after': '',
                'dynamic': 'false',
                'status': 'waiting',
            },
        ]

    def test_match_dhcp_record_unidentified(self, sample_leases):
        # Only leases with neither host_name nor comment should match
        matched = [l['mac_address'] for l in sample_leases if match_dhcp_record(l, unidentified=True)]
        assert matched == ['AA:00:00:00:00:99', 'AA:00:00:00:00:98']

    def test_match_dhcp_record_static(self, sample_leases):
        matched = [l['mac_address'] for l in sample_leases if match_dhcp_record(l, static_only=True)]
        assert matched == ['AA:00:00:00:00:01', 'AA:00:00:00:00:03', 'AA:00:00:00:00:98']

    def test_match_dhcp_record_dynamic(self, sample_leases):
        matched = [l['mac_address'] for l in sample_leases if match_dhcp_record(l, dynamic_only=True)]
        assert matched == ['AA:00:00:00:00:02', 'AA:00:00:00:00:99']

    def test_match_dhcp_record_active_only(self, sample_leases):
        matched = [l['mac_address'] for l in sample_leases if match_dhcp_record(l, active_only=True)]
        assert matched == ['AA:00:00:00:00:01', 'AA:00:00:00:00:02', 'AA:00:00:00:00:99']

    def test_match_dhcp_record_combined(self, sample_leases):
        # Unidentified + active only
        matched = [
            l['mac_address']
            for l in sample_leases
            if match_dhcp_record(l, unidentified=True, active_only=True)
        ]
        assert matched == ['AA:00:00:00:00:99']

        # Static + active only
        static_active = [
            l['mac_address']
            for l in sample_leases
            if match_dhcp_record(l, static_only=True, active_only=True)
        ]
        assert static_active == ['AA:00:00:00:00:01']

    @patch('mktxp.cli.output.dhcp_out.DHCPMetricsDataSource.metric_records')
    def test_dhcp_output_unidentified(self, mock_metric_records, mock_router_entry, sample_leases, capsys):
        mock_metric_records.return_value = sample_leases
        DHCPOutput.clients_summary(mock_router_entry, unidentified=True)
        captured = capsys.readouterr().out
        assert "AA:00:00:00:00:99" in captured
        assert "AA:00:00:00:00:98" in captured
        assert "Server-Main" not in captured
        assert "Guest-Phone" not in captured
        assert "Matching DHCP clients: 2 (Total: 5)" in captured

    @patch('mktxp.cli.output.dhcp_out.DHCPMetricsDataSource.metric_records')
    def test_dhcp_output_static_and_dynamic(self, mock_metric_records, mock_router_entry, sample_leases, capsys):
        mock_metric_records.return_value = sample_leases
        # Static
        DHCPOutput.clients_summary(mock_router_entry, static_only=True)
        captured = capsys.readouterr().out
        assert "Server-Main" in captured
        assert "Guest-Phone" not in captured
        assert "Matching DHCP clients: 3 (Total: 5)" in captured

        # Dynamic
        DHCPOutput.clients_summary(mock_router_entry, dynamic_only=True)
        captured = capsys.readouterr().out
        assert "Guest-Phone" in captured
        assert "Server-Main" not in captured
        assert "Matching DHCP clients: 2 (Total: 5)" in captured

    @patch('mktxp.cli.output.dhcp_out.DHCPMetricsDataSource.metric_records')
    def test_dhcp_output_active_only(self, mock_metric_records, mock_router_entry, sample_leases, capsys):
        mock_metric_records.return_value = sample_leases
        DHCPOutput.clients_summary(mock_router_entry, active_only=True)
        captured = capsys.readouterr().out
        assert "Server-Main" in captured
        assert "Guest-Phone" in captured
        assert "AA:00:00:00:00:99" in captured
        assert "AA:00:00:00:00:98" not in captured
        assert "Matching DHCP clients: 3 (Total: 5)" in captured

    def test_match_dhcp_record_inactive_only(self, sample_leases):
        matched = [l['mac_address'] for l in sample_leases if match_dhcp_record(l, inactive_only=True)]
        assert matched == ['AA:00:00:00:00:03', 'AA:00:00:00:00:98']

    @patch('mktxp.cli.output.dhcp_out.DHCPMetricsDataSource.metric_records')
    def test_dhcp_output_inactive_only(self, mock_metric_records, mock_router_entry, sample_leases, capsys):
        mock_metric_records.return_value = sample_leases
        DHCPOutput.clients_summary(mock_router_entry, inactive_only=True)
        captured = capsys.readouterr().out
        assert "AA:00:00:00:00:03" in captured or "AP Backyard" in captured
        assert "AA:00:00:00:00:98" in captured
        assert "Server-Main" not in captured
        assert "Guest-Phone" not in captured
        assert "Matching DHCP clients: 2 (Total: 5)" in captured

    @patch('mktxp.cli.output.dhcp_out.DHCPMetricsDataSource.metric_records')
    def test_dhcp_output_static_inactive_combined(self, mock_metric_records, mock_router_entry, sample_leases, capsys):
        mock_metric_records.return_value = sample_leases
        DHCPOutput.clients_summary(mock_router_entry, static_only=True, inactive_only=True)
        captured = capsys.readouterr().out
        assert "AA:00:00:00:00:03" in captured or "AP Backyard" in captured
        assert "AA:00:00:00:00:98" in captured
        assert "Server-Main" not in captured
        assert "Matching DHCP clients: 2 (Total: 5)" in captured


class TestConnectionStatsDiagnostics:
    @pytest.fixture
    def sample_connections(self):
        return [
            {'src_address': '10.0.0.10', 'connection_count': 100, 'dst_addresses': '1.1.1.1:443'},
            {'src_address': '10.0.0.20', 'connection_count': 60, 'dst_addresses': '8.8.8.8:53'},
            {'src_address': '10.0.0.30', 'connection_count': 25, 'dst_addresses': '9.9.9.9:53'},
            {'src_address': '10.0.0.40', 'connection_count': 5, 'dst_addresses': '1.0.0.1:53'},
        ]

    @patch('mktxp.cli.output.conn_stats_out.IPConnectionStatsDatasource.metric_records')
    def test_conn_stats_top(self, mock_metric_records, mock_router_entry, sample_connections, capsys):
        mock_metric_records.return_value = sample_connections
        # Top 2
        ConnectionsStatsOutput.clients_summary(mock_router_entry, top=2)
        out = capsys.readouterr().out
        assert '10.0.0.10' in out
        assert '10.0.0.20' in out
        assert '10.0.0.30' not in out
        assert '10.0.0.40' not in out
        assert 'Matching source addresses: 2 (Total: 4)' in out

    @patch('mktxp.cli.output.conn_stats_out.IPConnectionStatsDatasource.metric_records')
    def test_conn_stats_min_conns(self, mock_metric_records, mock_router_entry, sample_connections, capsys):
        mock_metric_records.return_value = sample_connections
        # Min conns 30
        ConnectionsStatsOutput.clients_summary(mock_router_entry, min_conns=30)
        out = capsys.readouterr().out
        assert '10.0.0.10' in out
        assert '10.0.0.20' in out
        assert '10.0.0.30' not in out
        assert '10.0.0.40' not in out
        assert 'Matching source addresses: 2 (Total: 4)' in out

    @patch('mktxp.cli.output.conn_stats_out.IPConnectionStatsDatasource.metric_records')
    def test_conn_stats_combined(self, mock_metric_records, mock_router_entry, sample_connections, capsys):
        mock_metric_records.return_value = sample_connections
        # Min conns 10 + Top 1
        ConnectionsStatsOutput.clients_summary(mock_router_entry, min_conns=10, top=1)
        out = capsys.readouterr().out
        assert '10.0.0.10' in out
        assert '10.0.0.20' not in out
        assert 'Matching source addresses: 1 (Total: 4)' in out





class TestWirelessDiagnostics:
    @pytest.fixture
    def weak_client(self):
        return {
            'dhcp_name': 'Weak-IoT',
            'rx_signal': '-82',
            'tx_rate': '12 Mbps',
            'rx_rate': '6 Mbps',
            'uptime': '5m',
            'interface': 'wlan-2.4G-1',
            'ssid': 'Corporate-2G'
        }

    @pytest.fixture
    def strong_fast_client(self):
        return {
            'dhcp_name': 'Fast-Laptop',
            'rx_signal': '-52',
            'tx_rate': '866 Mbps',
            'rx_rate': '866 Mbps',
            'uptime': '2d',
            'interface': 'wlan-5G-1',
            'ssid': 'Corporate-5G'
        }

    def test_low_signal_filter(self, weak_client, strong_fast_client):
        # Default -75 dBm: -82 matches (is <= -75), -52 fails (is > -75)
        assert match_wireless_record(weak_client, low_signal=True) is True
        assert match_wireless_record(strong_fast_client, low_signal=True) is False
        # Custom -85 dBm: -82 fails
        assert match_wireless_record(weak_client, low_signal='-85') is False

    def test_min_signal_filter(self, weak_client, strong_fast_client):
        # Default -60 dBm: -52 matches (is >= -60), -82 fails (is < -60)
        assert match_wireless_record(strong_fast_client, min_signal=True) is True
        assert match_wireless_record(weak_client, min_signal=True) is False

    def test_low_rate_filter(self, weak_client, strong_fast_client):
        # Default 18M: 6 Mbps matches (is <= 18M), 866 Mbps fails
        assert match_wireless_record(weak_client, low_rate=True) is True
        assert match_wireless_record(strong_fast_client, low_rate=True) is False
        # Unitless number: 18 -> 18 Mbps
        assert match_wireless_record(weak_client, low_rate='18') is True
        assert match_wireless_record(weak_client, low_rate=18) is True
        # Custom 5 Mbps: 6 Mbps fails
        assert match_wireless_record(weak_client, low_rate='5') is False

    def test_recent_filter(self, weak_client, strong_fast_client):
        # Default 15m: 5m matches (is <= 15m), 2d fails
        assert match_wireless_record(weak_client, recent=True) is True
        assert match_wireless_record(strong_fast_client, recent=True) is False
        # Unitless number: 16 -> 16m (matches 5m)
        assert match_wireless_record(weak_client, recent='16') is True
        assert match_wireless_record(weak_client, recent=16) is True
        assert match_wireless_record(weak_client, recent='16m') is True
        # Stricter 2m: 5m fails
        assert match_wireless_record(weak_client, recent='2m') is False
        assert match_wireless_record(weak_client, recent=2) is False

    def test_band_filter(self, weak_client, strong_fast_client):
        assert match_wireless_record(weak_client, band='2g') is True
        assert match_wireless_record(weak_client, band='5g') is False
        assert match_wireless_record(strong_fast_client, band='5g') is True
        assert match_wireless_record(strong_fast_client, band='2g') is False


class TestOptionsParserWirelessFlags:
    @patch('mktxp.cli.options.config_handler')
    def test_print_options_wireless_flags(self, mock_conf):
        mock_conf.registered_entries.return_value = ['TestRouter']
        mock_conf.config_entry.return_value.enabled = True
        parser = MKTXPOptionsParser()
        args = parser.parse_options(["print", "-en", "TestRouter", "-cc", "--low-signal", "-80", "--band", "5g", "--recent", "1h"])
        assert args["capsman_clients"] is True
        assert args["low_signal"] == "-80"
        assert args["band"] == "5g"
        assert args["recent"] == "1h"
