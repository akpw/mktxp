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

from unittest.mock import patch, MagicMock
from mktxp.cli.config import config_handler
from mktxp.cli.options import MKTXPOptionsParser, MKTXPCommands
from mktxp.cli.dispatch import MKTXPDispatcher


def test_options_parser_info():
    """Verify info subcommand parses."""
    parser = MKTXPOptionsParser()
    args = parser.parse_options(['info'])
    assert args['sub_cmd'] == MKTXPCommands.INFO


def test_options_parser_export():
    """Verify export subcommand parses."""
    parser = MKTXPOptionsParser()
    args = parser.parse_options(['export'])
    assert args['sub_cmd'] == MKTXPCommands.EXPORT


def test_options_parser_diag_alias():
    """Verify 'print' command aliases to 'diag'."""
    config_handler()
    parser = MKTXPOptionsParser()
    # Mock config_handler registered_entries and config_entry
    with patch('mktxp.cli.options.config_handler.registered_entries', return_value=['TestRouter']), \
         patch('mktxp.cli.options.config_handler.config_entry') as mock_ce:
        mock_ce.return_value = MagicMock(enabled=True)
        args = parser.parse_options(['print', '-en', 'TestRouter', '-cc'])
        assert args['sub_cmd'] == MKTXPCommands.PRINT
        assert args['capsman_clients'] is True


def test_options_parser_rsc_options(tmp_path):
    """Verify rsc command options parse correctly."""
    dummy_rsc = tmp_path / "test.rsc"
    dummy_rsc.write_text("# RouterOS export")

    parser = MKTXPOptionsParser()
    args = parser.parse_options(['rsc', 'format', '-i', str(dummy_rsc)])
    assert args['sub_cmd'] == MKTXPCommands.RSC
    assert args['rsc_cmd'] == 'format'
    assert args['input'] == str(dummy_rsc)


def test_dispatch_info(capsys):
    """Verify dispatcher print_info prints version info."""
    dispatcher = MKTXPDispatcher()
    dispatcher.print_info()
    captured = capsys.readouterr()
    assert 'MKTXP' in captured.out
    assert 'Diagnostics:' in captured.out


@patch('mktxp.cli.dispatch.ConfigCLI.show')
def test_dispatch_show(mock_show):
    """Verify dispatch show_entries delegates to ConfigCLI.show."""
    dispatcher = MKTXPDispatcher()
    args = {'sub_cmd': 'show', 'config': True}
    dispatcher.show_entries(args)
    assert mock_show.called


@patch('mktxp.cli.dispatch.DiagRegistry.get_active_handler')
@patch('mktxp.cli.dispatch.RouterEntriesHandler.router_entry')
def test_dispatch_diag(mock_router_entry, mock_get_active_handler):
    """Verify dispatch diag queries DiagRegistry and executes active handler."""
    mock_handler = MagicMock()
    mock_get_active_handler.return_value = mock_handler
    mock_router_entry.return_value = MagicMock()

    dispatcher = MKTXPDispatcher()
    args = {'sub_cmd': 'diag', 'wireless_clients': True, 'entry_name': 'TestRouter'}
    dispatcher.diag(args)

    assert mock_get_active_handler.called
    assert mock_handler.execute.called


def test_diag_help_formatter_scoping():
    """Verify MKTXPHelpFormatter scopes both Diagnostic Commands and filter groups to the target command."""
    import sys
    import argparse
    from unittest.mock import patch

    cmd_parser = argparse.ArgumentParser()
    MKTXPOptionsParser().parse_commands(cmd_parser)
    subparsers_actions = [
        action for action in cmd_parser._actions
        if isinstance(action, argparse._SubParsersAction)
    ]
    diag_parser = subparsers_actions[0].choices['diag']

    with patch.object(sys, 'argv', ['mktxp', 'diag', '-en', 'TestRouter', '-kc', '--top', '5', '-h']):
        help_text = diag_parser.format_help()
        assert "Kid Control Filters (-kc):" in help_text
        assert "-kc, --kid_control" in help_text
        assert "Wireless & CAPsMAN Filters" not in help_text
        assert "DHCP Server Filters" not in help_text
        assert "IP Connections Filters" not in help_text
        assert "Netwatch Filters" not in help_text
        assert "-cc, --capsman_clients" not in help_text
        assert "-cn, --conn_stats" not in help_text

