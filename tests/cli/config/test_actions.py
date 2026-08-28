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

import argparse
from mktxp.cli.config import config_handler
from mktxp.cli.config.actions import ConfigCLI


def test_config_cli_register_show_options():
    """Verify ConfigCLI attaches show subcommands."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')
    ConfigCLI.register_show_options(
        subparsers,
        lambda p, **kwargs: p.add_argument('-en', '--entry-name', dest='entry_name'),
        argparse.HelpFormatter
    )

    args = parser.parse_args(['show', '-cfg'])
    assert args.command == 'show'
    assert args.config is True


def test_config_cli_register_edit_options():
    """Verify ConfigCLI attaches edit subcommands."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')
    ConfigCLI.register_edit_options(subparsers, argparse.HelpFormatter)

    args_edit_internal = parser.parse_args(['edit', '-i', '-ed', 'vim'])
    assert args_edit_internal.command == 'edit'
    assert args_edit_internal.internal is True
    assert args_edit_internal.editor == 'vim'


def test_config_cli_show_paths(capsys):
    """Verify ConfigCLI.show() prints config file paths."""
    config_handler()
    ConfigCLI.show({'config': True})
    captured = capsys.readouterr()
    assert 'MKTXP data config:' in captured.out
    assert 'MKTXP internal config:' in captured.out
