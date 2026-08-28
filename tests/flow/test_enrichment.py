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

from unittest.mock import MagicMock
from mktxp.flow.processor.enrichment import (
    format_interface_name,
    dhcp_name,
    resolve_dhcp,
    augment_record,
)


def test_format_interface_name():
    assert format_interface_name('ether1', 'WAN uplink', 'name') == 'ether1'
    assert format_interface_name('ether1', 'WAN uplink', 'comment') == 'WAN uplink'
    assert format_interface_name('ether1', 'WAN uplink', 'combined') == 'ether1 (WAN uplink)'
    assert format_interface_name('ether1', '', 'combined') == 'ether1'


def test_dhcp_name():
    mock_router_entry = MagicMock()
    mock_router_entry.config_entry.interface_name_format = 'combined'

    lease_with_host = {'host_name': 'MyLaptop', 'comment': 'Work laptop', 'mac_address': 'AA:BB:CC:DD:EE:FF'}
    assert dhcp_name(mock_router_entry, lease_with_host) == 'MyLaptop (Work laptop)'

    lease_mac_only = {'mac_address': 'AA:BB:CC:DD:EE:FF'}
    assert dhcp_name(mock_router_entry, lease_mac_only) == 'AA:BB:CC:DD:EE:FF'


def test_augment_record():
    mock_router_entry = MagicMock()
    mock_router_entry.dhcp_records = {'AA:BB:CC:DD:EE:FF': {'host_name': 'Device1', 'address': '10.0.0.5'}}
    mock_router_entry.dhcp_record.return_value = {'host_name': 'Device1', 'address': '10.0.0.5'}
    mock_router_entry.config_entry.interface_name_format = 'name'

    rec = {
        'mac_address': 'AA:BB:CC:DD:EE:FF',
        'bytes': '1000,2000',
        'tx_rate': '866000000',
        'rx_rate': '866000000',
        'uptime': '1m30s',
        'signal_strength': '-65dBm',
    }

    augment_record(mock_router_entry, rec)

    assert rec['dhcp_name'] == 'Device1'
    assert rec['dhcp_address'] == '10.0.0.5'
    assert rec['tx_bytes'] == '1000'
    assert rec['rx_bytes'] == '2000'
    assert rec['tx_rate'] == '866 Mbps'
    assert rec['signal_strength'] == '-65'
