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

import os
from collections import namedtuple
from texttable import Texttable

# CLI Diagnostic Table Schemas
OutputCapsmanEntry = namedtuple(
    'OutputCapsmanEntry',
    ['dhcp_name', 'dhcp_address', 'mac_address', 'rx_signal', 'interface', 'ssid', 'tx_rate', 'rx_rate', 'uptime']
)
OutputCapsmanEntry.__new__.__defaults__ = ('',) * len(OutputCapsmanEntry._fields)

OutputWirelessEntry = namedtuple(
    'OutputWirelessEntry',
    ['dhcp_name', 'dhcp_address', 'mac_address', 'signal_strength', 'signal_to_noise', 'interface', 'tx_rate', 'rx_rate', 'uptime']
)
OutputWirelessEntry.__new__.__defaults__ = ('',) * len(OutputWirelessEntry._fields)

OutputWiFiEntry = namedtuple(
    'OutputWiFiEntry',
    ['dhcp_name', 'dhcp_address', 'mac_address', 'signal_strength', 'interface', 'tx_rate', 'rx_rate', 'uptime']
)
OutputWiFiEntry.__new__.__defaults__ = ('',) * len(OutputWiFiEntry._fields)

OutputDHCPEntry = namedtuple(
    'OutputDHCPEntry',
    ['host_name', 'server', 'mac_address', 'address', 'active_address', 'expires_after']
)
OutputDHCPEntry.__new__.__defaults__ = ('',) * len(OutputDHCPEntry._fields)

OutputConnStatsEntry = namedtuple(
    'OutputConnStatsEntry',
    ['dhcp_name', 'src_address', 'connection_count', 'dst_addresses']
)
OutputConnStatsEntry.__new__.__defaults__ = ('',) * len(OutputConnStatsEntry._fields)

OutputKidControlEntry = namedtuple(
    'OutputKidControlEntry',
    ['dhcp_name', 'name', 'user', 'dhcp_address', 'mac_address', 'ip_address', 'rate_up', 'rate_down', 'idle_time']
)
OutputKidControlEntry.__new__.__defaults__ = ('',) * len(OutputKidControlEntry._fields)

OutputAddressListEntry = namedtuple(
    'OutputAddressListEntry',
    ['list', 'address', 'comment', 'timeout', 'dynamic', 'disabled']
)
OutputAddressListEntry.__new__.__defaults__ = ('',) * len(OutputAddressListEntry._fields)

OutputNetwatchEntry = namedtuple(
    'OutputNetwatchEntry',
    ['name', 'host', 'comment', 'status', 'type', 'since', 'timeout', 'interval']
)
OutputNetwatchEntry.__new__.__defaults__ = ('',) * len(OutputNetwatchEntry._fields)


def output_table(output_entry=None):
    """Creates an auto-sizing Texttable configured for CLI output."""
    try:
        terminal_columns = os.get_terminal_size().columns
    except (OSError, ValueError):
        terminal_columns = 0
    table = Texttable(max_width=terminal_columns)
    table.set_deco(Texttable.HEADER | Texttable.BORDER | Texttable.VLINES)
    if output_entry:
        table.header(output_entry._fields)
        table.set_cols_align(['l'] + ['c'] * (len(output_entry._fields) - 1))
    return table
