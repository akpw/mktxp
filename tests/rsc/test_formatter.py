# coding=utf8
import pytest
from mktxp.rsc.parser import RSCParser
from mktxp.rsc.formatter import RSCFormatter


def test_formatter_unwrapped():
    raw = """
/interface bridge
add admin-mac=DC:2C:6E:13:58:2E auto-mac=no comment="LAN Bridge" frame-types=admit-only-vlan-tagged name=bridge_main port-cost-mode=short vlan-filtering=yes
"""
    parser = RSCParser()
    config = parser.parse(raw)

    formatter = RSCFormatter(wrap_lines=False, add_section_headers=True)
    out = formatter.format_config(config)

    expected = """# Section: /interface bridge
/interface bridge
add admin-mac=DC:2C:6E:13:58:2E auto-mac=no comment="LAN Bridge" frame-types=admit-only-vlan-tagged name=bridge_main port-cost-mode=short vlan-filtering=yes
"""
    assert out.strip() == expected.strip()


def test_formatter_wrapped():
    raw = """
/interface bridge
add admin-mac=DC:2C:6E:13:58:2E auto-mac=no comment="LAN Bridge" frame-types=admit-only-vlan-tagged name=bridge_main port-cost-mode=short vlan-filtering=yes
"""
    parser = RSCParser()
    config = parser.parse(raw)

    formatter = RSCFormatter(wrap_lines=True, wrap_col=80, add_section_headers=True)
    out = formatter.format_config(config)

    assert "\\" in out
    lines = out.splitlines()
    assert lines[0] == "# Section: /interface bridge"
    assert lines[1] == "/interface bridge"
    assert lines[2].startswith("add admin-mac=")
    assert lines[2].endswith("\\")
    assert lines[3].startswith("    ")
