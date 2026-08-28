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

from mktxp.diag.registry import DiagRegistry
from mktxp.diag.wireless import WirelessDiagHandler
from mktxp.diag.dhcp import DHCPDiagHandler
from mktxp.diag.connections import ConnectionDiagHandler
from mktxp.diag.kid_control import KidControlDiagHandler
from mktxp.diag.address_lists import AddressListDiagHandler
from mktxp.diag.netwatch import NetwatchDiagHandler


def test_diag_registry_handler_count():
    """Verify all 6 core diagnostic domain handlers are registered."""
    handlers = DiagRegistry.get_handlers()
    assert len(handlers) == 6
    handler_classes = [type(h) for h in handlers]
    assert WirelessDiagHandler in handler_classes
    assert DHCPDiagHandler in handler_classes
    assert ConnectionDiagHandler in handler_classes
    assert KidControlDiagHandler in handler_classes
    assert AddressListDiagHandler in handler_classes
    assert NetwatchDiagHandler in handler_classes


def test_diag_registry_get_active_handler():
    """Verify get_active_handler identifies the correct handler based on args."""
    # Wireless (capsman)
    handler = DiagRegistry.get_active_handler({'capsman_clients': True})
    assert isinstance(handler, WirelessDiagHandler)

    # Wireless (wifi)
    handler = DiagRegistry.get_active_handler({'wifi_clients': True})
    assert isinstance(handler, WirelessDiagHandler)

    # DHCP
    handler = DiagRegistry.get_active_handler({'dhcp_clients': True})
    assert isinstance(handler, DHCPDiagHandler)

    # Connections
    handler = DiagRegistry.get_active_handler({'conn_stats': True})
    assert isinstance(handler, ConnectionDiagHandler)

    # Kid Control
    handler = DiagRegistry.get_active_handler({'kid_control': True})
    assert isinstance(handler, KidControlDiagHandler)

    # Address List
    handler = DiagRegistry.get_active_handler({'address_lists': True})
    assert isinstance(handler, AddressListDiagHandler)

    # Netwatch
    handler = DiagRegistry.get_active_handler({'netwatch': True})
    assert isinstance(handler, NetwatchDiagHandler)

    # Unknown / None
    handler = DiagRegistry.get_active_handler({'unknown': True})
    assert handler is None


def test_diag_registry_matching_help_handlers():
    """Verify get_matching_help_handlers detects matching flags in argv."""
    matching = DiagRegistry.get_matching_help_handlers(['mktxp', 'diag', '-cc', '-h'])
    assert len(matching) == 1
    assert isinstance(matching[0], WirelessDiagHandler)

    matching_dhcp = DiagRegistry.get_matching_help_handlers(['mktxp', 'diag', '-dc', '-h'])
    assert len(matching_dhcp) == 1
    assert isinstance(matching_dhcp[0], DHCPDiagHandler)
