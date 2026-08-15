# coding=utf8
import pytest
from mktxp.rsc.parser import RSCParser
from mktxp.rsc.middleware.sorter import DeterminismSorter


def test_sorter_unordered_path():
    raw = """
/interface list member
add interface=vlan-management list=Management
add interface=bridge_main list=LAN
add interface=wlan2G list=LAN
"""
    parser = RSCParser()
    config = parser.parse(raw)

    sorter = DeterminismSorter()
    sorted_config = sorter.process(config)

    cmds = sorted_config.sections[0].commands
    # Should be sorted alphabetically by list then interface
    assert cmds[0].params["interface"] == "bridge_main"
    assert cmds[1].params["interface"] == "wlan2G"
    assert cmds[2].params["interface"] == "vlan-management"


def test_sorter_ordered_firewall_path_preserved():
    raw = """
/ip firewall filter
add action=accept chain=input comment="Accept Established"
add action=drop chain=input comment="Drop Invalid"
add action=accept chain=input comment="Accept ICMP"
add action=drop chain=input comment="Drop All Else"
"""
    parser = RSCParser()
    config = parser.parse(raw)

    sorter = DeterminismSorter()
    sorted_config = sorter.process(config)

    cmds = sorted_config.sections[0].commands
    # Must strictly preserve insertion order!
    assert "Accept Established" in cmds[0].params["comment"]
    assert "Drop Invalid" in cmds[1].params["comment"]
    assert "Accept ICMP" in cmds[2].params["comment"]
    assert "Drop All Else" in cmds[3].params["comment"]


def test_sorter_ordered_ipv6_firewall_path_preserved():
    raw = """
/ipv6 firewall filter
add action=accept chain=input comment="Accept Established"
add action=drop chain=input comment="Drop Invalid"
"""
    parser = RSCParser()
    config = parser.parse(raw)

    sorter = DeterminismSorter()
    sorted_config = sorter.process(config)

    cmds = sorted_config.sections[0].commands
    assert "Accept Established" in cmds[0].params["comment"]
    assert "Drop Invalid" in cmds[1].params["comment"]
