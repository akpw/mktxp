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

from unittest.mock import patch
from mktxp.utils.tables import (
    OutputCapsmanEntry,
    OutputWirelessEntry,
    OutputWiFiEntry,
    OutputDHCPEntry,
    OutputConnStatsEntry,
    OutputKidControlEntry,
    OutputAddressListEntry,
    OutputNetwatchEntry,
    output_table,
)


def test_table_entry_defaults():
    # Verify all schemas instantiate with empty defaults
    capsman = OutputCapsmanEntry()
    assert capsman.dhcp_name == ''
    assert len(capsman._fields) == 9

    dhcp = OutputDHCPEntry(host_name='MyHost')
    assert dhcp.host_name == 'MyHost'
    assert dhcp.server == ''

    kid = OutputKidControlEntry()
    assert kid.name == ''
    assert len(kid._fields) == 9

    netwatch = OutputNetwatchEntry()
    assert netwatch.host == ''

    addr = OutputAddressListEntry()
    assert addr.list == ''

    wifi = OutputWiFiEntry()
    assert wifi.signal_strength == ''

    conn = OutputConnStatsEntry()
    assert conn.src_address == ''


def test_output_table_creation():
    tbl = output_table(OutputDHCPEntry)
    assert tbl is not None

    tbl.add_row(OutputDHCPEntry(host_name='Host1', mac_address='11:22:33:44:55:66'))
    rendered = tbl.draw()
    assert 'Host1' in rendered
    assert '11:22:33:44:55:66' in rendered


def test_output_table_without_entry():
    tbl = output_table()
    assert tbl is not None
