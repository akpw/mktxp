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

    matching_unidentified = DiagRegistry.get_matching_help_handlers(['mktxp', 'diag', '--unidentified', '-h'])
    assert len(matching_unidentified) == 1
    assert isinstance(matching_unidentified[0], DHCPDiagHandler)

    # Command switch takes priority over shared filter flags like --top
    matching_kc_top = DiagRegistry.get_matching_help_handlers(['mktxp', 'diag', '-kc', '--top', '5', '-h'])
    assert len(matching_kc_top) == 1
    assert isinstance(matching_kc_top[0], KidControlDiagHandler)

    matching_cn_top = DiagRegistry.get_matching_help_handlers(['mktxp', 'diag', '-cn', '--top', '5', '-h'])
    assert len(matching_cn_top) == 1
    assert isinstance(matching_cn_top[0], ConnectionDiagHandler)

    # Shared filter without command flag matches all applicable handlers
    matching_top_alone = DiagRegistry.get_matching_help_handlers(['mktxp', 'diag', '--top', '5', '-h'])
    assert len(matching_top_alone) == 2
    assert any(isinstance(h, ConnectionDiagHandler) for h in matching_top_alone)
    assert any(isinstance(h, KidControlDiagHandler) for h in matching_top_alone)


def test_dhcp_diag_handler_filter_registration():
    """Verify DHCPDiagHandler registers specialized filter options."""
    import argparse
    parser = argparse.ArgumentParser()
    handler = DHCPDiagHandler()
    handler.register_filter_options(parser)

    # Test parsing valid combinations
    args = parser.parse_args(['--unidentified', '--static', '--active-only'])
    assert args.unidentified is True
    assert args.static_only is True
    assert args.dynamic_only is False
    assert args.active_only is True

    # Test dynamic flag and inactive-only
    args_dyn = parser.parse_args(['--dynamic', '--inactive-only'])
    assert args_dyn.unidentified is False
    assert args_dyn.static_only is False
    assert args_dyn.dynamic_only is True
    assert args_dyn.active_only is False
    assert args_dyn.inactive_only is True

    # Test mutual exclusion of --active-only and --inactive-only
    import pytest
    with pytest.raises(SystemExit):
        parser.parse_args(['--active-only', '--inactive-only'])


def test_dhcp_diag_handler_execute_delegation():
    """Verify DHCPDiagHandler.execute passes all filter options to DHCPOutput.clients_summary."""
    from unittest.mock import Mock, patch
    handler = DHCPDiagHandler()
    router_entry = Mock()
    args = {
        'include': '192.168.1',
        'exclude': 'guest',
        'unidentified': True,
        'static_only': True,
        'dynamic_only': False,
        'active_only': False,
        'inactive_only': True,
    }

    with patch('mktxp.diag.dhcp.DHCPOutput.clients_summary') as mock_cs:
        handler.execute(router_entry, args)
        mock_cs.assert_called_once_with(
            router_entry,
            include=['192.168.1'],
            exclude=['guest'],
            unidentified=True,
            static_only=True,
            dynamic_only=False,
            active_only=False,
            inactive_only=True,
        )


def test_connection_diag_handler_filters():
    """Verify ConnectionDiagHandler registers and delegates filter options."""
    import argparse
    from unittest.mock import Mock, patch
    parser = argparse.ArgumentParser()
    handler = ConnectionDiagHandler()
    handler.register_filter_options(parser)

    args = parser.parse_args(['--top', '5', '--min-conns', '50'])
    assert args.top == '5'
    assert args.min_conns == 50

    router_entry = Mock()
    exec_args = {'include': 'lan', 'exclude': 'vpn', 'top': 5, 'min_conns': 50}
    with patch('mktxp.diag.connections.ConnectionsStatsOutput.clients_summary') as mock_cs:
        handler.execute(router_entry, exec_args)
        mock_cs.assert_called_once_with(
            router_entry,
            include=['lan'],
            exclude=['vpn'],
            top=5,
            min_conns=50,
        )


def test_kid_control_diag_handler_filters():
    """Verify KidControlDiagHandler registers and delegates filter options."""
    import argparse
    from unittest.mock import Mock, patch
    parser = argparse.ArgumentParser()
    handler = KidControlDiagHandler()
    handler.register_filter_options(parser)

    args = parser.parse_args(['--active', '--rate-above', '2M', '--unassigned', '--top', '5', '--dynamic-only'])
    assert args.active_only is True
    assert args.rate_above == '2M'
    assert args.unassigned is True
    assert args.top == '5'
    assert args.dynamic_only is True
    assert args.static_only is False

    router_entry = Mock()
    exec_args = {
        'include': None,
        'exclude': None,
        'active_only': True,
        'rate_above': '2M',
        'unassigned': True,
        'dynamic_only': True,
        'static_only': False,
        'top': 5,
    }
    with patch('mktxp.diag.kid_control.KidControlOutput.clients_summary') as mock_cs:
        handler.execute(router_entry, exec_args)
        mock_cs.assert_called_once_with(
            router_entry,
            include=[],
            exclude=[],
            active_only=True,
            rate_above='2M',
            unassigned=True,
            dynamic_only=True,
            static_only=False,
            top=5,
        )


def test_address_list_diag_handler_filters():
    """Verify AddressListDiagHandler registers and delegates filter options."""
    import argparse
    from unittest.mock import Mock, patch
    parser = argparse.ArgumentParser()
    handler = AddressListDiagHandler()
    handler.register_filter_options(parser)

    args = parser.parse_args(['--dynamic-only'])
    assert args.dynamic_only is True
    assert args.static_only is False

    router_entry = Mock()
    exec_args = {'include': None, 'exclude': None, 'address_lists': 'blacklists', 'dynamic_only': True, 'static_only': False}
    with patch('mktxp.diag.address_lists.AddressListOutput.clients_summary') as mock_cs:
        handler.execute(router_entry, exec_args)
        mock_cs.assert_called_once_with(
            router_entry,
            'blacklists',
            include=[],
            exclude=[],
            dynamic_only=True,
            static_only=False,
        )


def test_netwatch_diag_handler_filters():
    """Verify NetwatchDiagHandler registers and delegates filter options."""
    import argparse
    from unittest.mock import Mock, patch
    parser = argparse.ArgumentParser()
    handler = NetwatchDiagHandler()
    handler.register_filter_options(parser)

    args = parser.parse_args(['--down-only'])
    assert args.down_only is True
    assert args.up_only is False

    router_entry = Mock()
    exec_args = {'include': None, 'exclude': None, 'down_only': True, 'up_only': False}
    with patch('mktxp.diag.netwatch.NetwatchOutput.clients_summary') as mock_cs:
        handler.execute(router_entry, exec_args)
        mock_cs.assert_called_once_with(
            router_entry,
            include=[],
            exclude=[],
            down_only=True,
            up_only=False,
        )


def test_diag_dynamic_config_defaults_in_help():
    """Verify diagnostic filter help strings dynamically display configured defaults."""
    import argparse
    from unittest.mock import patch

    mock_conf = {
        'low_signal_threshold': -80,
        'min_signal_threshold': -55,
        'low_rate_threshold': '24M',
        'recent_duration': '20m',
        'top_connections_count': 25,
        'rate_above_threshold': '5M',
    }

    with patch('mktxp.cli.config.config_handler.diag_config', return_value=mock_conf):
        # Wireless
        parser = argparse.ArgumentParser()
        WirelessDiagHandler().register_filter_options(parser)
        help_text = parser.format_help()
        assert "(default: -80 dBm)" in help_text
        assert "(default: -55 dBm)" in help_text
        assert "(default: 24M)" in help_text
        assert "(default: 20m)" in help_text

        # Connections
        parser = argparse.ArgumentParser()
        ConnectionDiagHandler().register_filter_options(parser)
        help_text = parser.format_help()
        assert "(default: 25)" in help_text

        # Kid Control
        parser = argparse.ArgumentParser()
        KidControlDiagHandler().register_filter_options(parser)
        help_text = parser.format_help()
        assert "(default: 25)" in help_text
        assert "(default: 5M)" in help_text




