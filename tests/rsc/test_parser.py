# coding=utf8
import pytest
from mktxp.rsc.parser import RSCParser


def test_parser_basic_sections():
    raw = """
/interface bridge
add name=bridge_main vlan-filtering=yes
/interface vlan
add interface=bridge_main name=vlan-mgmt vlan-id=70
"""
    parser = RSCParser()
    config = parser.parse(raw)

    assert len(config.sections) == 2
    assert config.sections[0].path == "/interface bridge"
    assert len(config.sections[0].commands) == 1
    assert config.sections[0].commands[0].command == "add"
    assert config.sections[0].commands[0].params["name"] == "bridge_main"
    assert config.sections[0].commands[0].params["vlan-filtering"] == "yes"

    assert config.sections[1].path == "/interface vlan"
    assert config.sections[1].commands[0].params["vlan-id"] == "70"


def test_parser_set_with_find():
    raw = """
/interface ethernet
# same mac-address as MBR
set [ find default-name=ether1 ] comment="Trunk Link" l2mtu=1598
"""
    parser = RSCParser()
    config = parser.parse(raw)

    assert len(config.sections) == 1
    cmd = config.sections[0].commands[0]
    assert cmd.command == "set"
    assert cmd.find_expr == "[ find default-name=ether1 ]"
    assert cmd.params["comment"] == '"Trunk Link"'
    assert cmd.params["l2mtu"] == "1598"
    assert cmd.leading_comments == ["# same mac-address as MBR"]


def test_parser_inline_path_command():
    raw = """
/system clock set time-zone-name=Europe/Lisbon
/routing bgp template set default disabled=no output.network=bgp-networks
"""
    parser = RSCParser()
    config = parser.parse(raw)

    assert len(config.sections) == 2
    assert config.sections[0].path == "/system clock"
    assert config.sections[0].commands[0].command == "set"
    assert config.sections[0].commands[0].params["time-zone-name"] == "Europe/Lisbon"

    assert config.sections[1].path == "/routing bgp template"
    assert config.sections[1].commands[0].command == "set"
    assert config.sections[1].commands[0].target == "default"
    assert config.sections[1].commands[0].params["output.network"] == "bgp-networks"
