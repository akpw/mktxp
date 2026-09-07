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
from mktxp.cli.output.interface_out import InterfaceOutput


@pytest.fixture
def mock_router_entry():
    """Create a mock router entry with necessary attributes."""
    router_entry = Mock()
    router_entry.router_name = "CoreRouter"
    router_entry.config_entry.hostname = "192.168.88.1"
    return router_entry


@pytest.fixture
def sample_interface_records():
    """Sample records reflecting real-world RouterOS ethernet & SFP monitor outputs."""
    return [
        {
            'name': 'INet Provider',
            'status': 'link-ok',
            'rate': '100Mbps',
            'full_duplex': 'true',
            'auto_negotiation': 'done',
            'sfp_module_present': 'false',
        },
        {
            'name': 'ether2',
            'status': 'link-ok',
            'rate': '1Gbps',
            'full_duplex': 'true',
            'auto_negotiation': 'done',
            'sfp_module_present': 'false',
        },
        {
            'name': 'SMLIGHT SLZB-06',
            'status': 'link-ok',
            'rate': '100Mbps',
            'full_duplex': 'true',
            'auto_negotiation': 'done',
            'sfp_module_present': 'false',
        },
        {
            'name': 'QNAP',
            'status': 'link-ok',
            'rate': '1Gbps',
            'full_duplex': 'true',
            'auto_negotiation': 'done',
            'sfp_module_present': 'false',
        },
        {
            'name': 'ether5 (Shaky Link)',
            'status': 'link-ok',
            'rate': '10Mbps',
            'full_duplex': 'false',
            'auto_negotiation': 'done',
            'sfp_module_present': 'false',
        },
        {
            'name': 'sfp-sfpplus1',
            'status': 'no-link',
            'rate': '',
            'full_duplex': '',
            'auto_negotiation': '',
            'sfp_module_present': 'false',
        },
        {
            'name': 'sfp-sfpplus2',
            'status': 'link-ok',
            'rate': '10Gbps',
            'full_duplex': 'true',
            'auto_negotiation': 'done',
            'sfp_module_present': 'true',
            'sfp_type': 'SFP-or-SFP+',
            'sfp_vendor_name': 'MikroTik',
            'sfp_vendor_part_number': 'S+85DLC03D',
            'sfp_connector_type': 'LC',
            'sfp_rx_power': '-5.2',
            'sfp_tx_power': '-2.1',
            'sfp_temperature': '42C',
            'sfp_rx_loss': '0',
            'sfp_tx_fault': '0',
        },
    ]


class TestInterfaceOutputHelpers:
    """Tests for rate formatting, SFP identification, and unit helpers."""

    def test_format_rate(self):
        assert InterfaceOutput._format_rate('100Mbps') == '100 Mbps'
        assert InterfaceOutput._format_rate('1Gbps') == '1 Gbps'
        assert InterfaceOutput._format_rate('2.5Gbps') == '2.5 Gbps'
        assert InterfaceOutput._format_rate('10Gbps') == '10 Gbps'
        assert InterfaceOutput._format_rate('100 Mb/s') == '100 Mbps'
        assert InterfaceOutput._format_rate('1 Gb/s') == '1 Gbps'
        assert InterfaceOutput._format_rate('') == '-'
        assert InterfaceOutput._format_rate('0') == '-'
        assert InterfaceOutput._format_rate(None) == '-'

    def test_is_sfp_record(self):
        assert InterfaceOutput._is_sfp_record({'sfp_module_present': 'true'}) is True
        assert InterfaceOutput._is_sfp_record({'sfp_type': 'SFP+'}) is True
        assert InterfaceOutput._is_sfp_record({'name': 'sfp-sfpplus1'}) is True
        assert InterfaceOutput._is_sfp_record({'name': 'qsfp28-1'}) is True
        assert InterfaceOutput._is_sfp_record({'name': 'ether1', 'sfp_module_present': 'false'}) is False


class TestInterfaceOutputCollection:
    """Tests for data collection from InterfaceMonitorMetricsDataSource."""

    @patch('mktxp.cli.output.interface_out.InterfaceMonitorMetricsDataSource.metric_records')
    def test_collect_records_success(self, mock_metric_records, mock_router_entry, sample_interface_records):
        mock_metric_records.return_value = sample_interface_records
        records = InterfaceOutput._collect_records(mock_router_entry)
        assert len(records) == 7
        mock_metric_records.assert_called_once()

    @patch('mktxp.cli.output.interface_out.InterfaceMonitorMetricsDataSource.metric_records')
    def test_collect_records_exception(self, mock_metric_records, mock_router_entry, capsys):
        mock_metric_records.side_effect = Exception("API connection failed")
        records = InterfaceOutput._collect_records(mock_router_entry)
        assert records == []
        out = capsys.readouterr().out
        assert "Error getting interface monitor info" in out

    @patch('mktxp.cli.output.interface_out.InterfaceOutput._collect_records')
    def test_interfaces_summary_no_records(self, mock_collect, mock_router_entry, capsys):
        mock_collect.return_value = []
        InterfaceOutput.interfaces_summary(mock_router_entry)
        out = capsys.readouterr().out
        assert "No interface monitor records found" in out


class TestInterfaceOutputDisplay:
    """Tests for table rendering and diagnostic filters."""

    @patch('mktxp.cli.output.interface_out.InterfaceOutput._collect_records')
    @patch('os.get_terminal_size')
    def test_full_summary_table(self, mock_term, mock_collect, mock_router_entry, sample_interface_records, capsys):
        mock_term.return_value = Mock(columns=140)
        mock_collect.return_value = sample_interface_records

        InterfaceOutput.interfaces_summary(mock_router_entry)
        out = capsys.readouterr().out

        assert "Interface Monitor:" in out
        assert "INet Provider" in out
        assert "ether2" in out
        assert "SMLIGHT SLZB-06" in out
        assert "ether5 (Shaky Link)" in out
        assert "sfp-sfpplus1" in out
        assert "sfp-sfpplus2" in out

        # Rates
        assert "100 Mbps" in out
        assert "1 Gbps" in out
        assert "10 Mbps" in out
        assert "10 Gbps" in out

        # Statuses
        assert "Plugged-In" in out
        assert "Unplugged" in out

        # Footer statistics (default threshold: < 100M)
        assert "Total interfaces: 7" in out
        assert "Plugged: 6" in out
        assert "Unplugged: 1" in out
        assert "Degraded (< 100M): 1" in out

    @patch('mktxp.cli.output.interface_out.InterfaceOutput._collect_records')
    @patch('os.get_terminal_size')
    def test_degraded_filter_default(self, mock_term, mock_collect, mock_router_entry, sample_interface_records, capsys):
        """Verify --degraded with default threshold (< 100M or half-duplex) isolates only genuinely degraded links."""
        mock_term.return_value = Mock(columns=140)
        mock_collect.return_value = sample_interface_records

        InterfaceOutput.interfaces_summary(mock_router_entry, degraded=True)
        out = capsys.readouterr().out

        # Only 10 Mbps / half-duplex link should match; normal 100M devices are not degraded
        assert "ether5 (Shaky Link)" in out
        assert "Half" in out
        assert "INet Provider" not in out
        assert "SMLIGHT SLZB-06" not in out
        assert "ether2" not in out
        assert "QNAP" not in out
        assert "sfp-sfpplus1" not in out

        assert "Matching interfaces: 1 (Total: 7)" in out
        assert "Plugged: 1" in out
        assert "Degraded (< 100M): 1" in out

    @patch('mktxp.cli.output.interface_out.InterfaceOutput._collect_records')
    @patch('os.get_terminal_size')
    def test_degraded_filter_custom_level(self, mock_term, mock_collect, mock_router_entry, sample_interface_records, capsys):
        """Verify --degraded with custom sub-rate level (e.g. 1G) catches all sub-gigabit links."""
        mock_term.return_value = Mock(columns=140)
        mock_collect.return_value = sample_interface_records

        InterfaceOutput.interfaces_summary(mock_router_entry, degraded='1G')
        out = capsys.readouterr().out

        # All links below 1G should appear
        assert "INet Provider" in out
        assert "SMLIGHT SLZB-06" in out
        assert "ether5 (Shaky Link)" in out
        assert "ether2" not in out
        assert "QNAP" not in out
        assert "sfp-sfpplus1" not in out
        assert "sfp-sfpplus2" not in out

        assert "Matching interfaces: 3 (Total: 7)" in out
        assert "Plugged: 3" in out
        assert "Degraded (< 1G): 3" in out

    @patch('mktxp.cli.output.interface_out.InterfaceOutput._collect_records')
    @patch('os.get_terminal_size')
    def test_plugged_and_unplugged_filters(self, mock_term, mock_collect, mock_router_entry, sample_interface_records, capsys):
        mock_term.return_value = Mock(columns=140)
        mock_collect.return_value = sample_interface_records

        # 1. Plugged only
        InterfaceOutput.interfaces_summary(mock_router_entry, plugged_only=True)
        out_plugged = capsys.readouterr().out
        assert "sfp-sfpplus1" not in out_plugged
        assert "ether2" in out_plugged
        assert "Matching interfaces: 6 (Total: 7)" in out_plugged
        assert "Plugged: 6" in out_plugged
        assert "Unplugged: 0" in out_plugged

        # 2. Unplugged only
        InterfaceOutput.interfaces_summary(mock_router_entry, unplugged_only=True)
        out_unplugged = capsys.readouterr().out
        assert "sfp-sfpplus1" in out_unplugged
        assert "ether2" not in out_unplugged
        assert "Matching interfaces: 1 (Total: 7)" in out_unplugged
        assert "Plugged: 0" in out_unplugged
        assert "Unplugged: 1" in out_unplugged

    @patch('mktxp.cli.output.interface_out.InterfaceOutput._collect_records')
    @patch('os.get_terminal_size')
    def test_rate_filtering(self, mock_term, mock_collect, mock_router_entry, sample_interface_records, capsys):
        mock_term.return_value = Mock(columns=140)
        mock_collect.return_value = sample_interface_records

        # 1. Exact rate
        InterfaceOutput.interfaces_summary(mock_router_entry, rate='100M')
        out_rate = capsys.readouterr().out
        assert "INet Provider" in out_rate
        assert "SMLIGHT SLZB-06" in out_rate
        assert "ether2" not in out_rate
        assert "ether5 (Shaky Link)" not in out_rate

        # 2. Rate below threshold
        InterfaceOutput.interfaces_summary(mock_router_entry, rate_below='100M')
        out_below = capsys.readouterr().out
        assert "ether5 (Shaky Link)" in out_below
        assert "INet Provider" not in out_below
        assert "ether2" not in out_below

    @patch('mktxp.cli.output.interface_out.InterfaceOutput._collect_records')
    @patch('os.get_terminal_size')
    def test_include_and_exclude_filters(self, mock_term, mock_collect, mock_router_entry, sample_interface_records, capsys):
        mock_term.return_value = Mock(columns=140)
        mock_collect.return_value = sample_interface_records

        # Include filter
        InterfaceOutput.interfaces_summary(mock_router_entry, include=['sfp'])
        out = capsys.readouterr().out
        assert "sfp-sfpplus1" in out
        assert "sfp-sfpplus2" in out
        assert "ether2" not in out

        # Exclude filter
        InterfaceOutput.interfaces_summary(mock_router_entry, exclude=['sfp'])
        out_ex = capsys.readouterr().out
        assert "sfp-sfpplus1" not in out_ex
        assert "sfp-sfpplus2" not in out_ex
        assert "ether2" in out_ex

    @patch('mktxp.cli.output.interface_out.InterfaceOutput._collect_records')
    @patch('os.get_terminal_size')
    def test_sfp_only_table_display(self, mock_term, mock_collect, mock_router_entry, sample_interface_records, capsys):
        mock_term.return_value = Mock(columns=160)
        mock_collect.return_value = sample_interface_records

        InterfaceOutput.interfaces_summary(mock_router_entry, sfp_only=True)
        out = capsys.readouterr().out

        assert "SFP Interface Monitor:" in out
        assert "sfp-sfpplus1" in out
        assert "sfp-sfpplus2" in out
        assert "ether2" not in out
        assert "INet Provider" not in out

        # Transceiver and DOM details
        assert "MikroTik S+85DLC03D" in out
        assert "LC" in out
        assert "-5.2 dBm" in out
        assert "-2.1 dBm" in out
        assert "42 °C" in out

        assert "Total SFP interfaces: 2" in out
        assert "Plugged: 1" in out
        assert "Unplugged: 1" in out
