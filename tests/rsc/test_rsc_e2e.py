# coding=utf8
import os
import pytest
from mktxp.rsc import RSCEngine


# Completely synthetic/fictional RouterOS export data for testing
FICTIONAL_RSC_EXPORT = """# 2026-08-14 10:00:00 by RouterOS 7.23.3
# software id = TEST-0001
# model = TestRouter-5G
/interface bridge
add comment="Test Bridge" frame-types=admit-only-vlan-tagged name=bridge_main port-cost-mode=short vlan-filtering=yes
/interface ethernet
set [ find default-name=ether1 ] comment="Trunk Uplink" l2mtu=1598
set [ find default-name=ether2 ] comment="LAN Port" l2mtu=1598
/interface vlan
add interface=bridge_main name=vlan-mgmt vlan-id=70
add interface=bridge_main name=vlan-data vlan-id=10
/interface list
add name=LAN
add name=Management
/interface bridge port
add bridge=bridge_main interface=ether1
add bridge=bridge_main interface=ether2
/interface bridge vlan
add bridge=bridge_main tagged=bridge_main,ether1 vlan-ids=70
add bridge=bridge_main tagged=bridge_main,ether2 vlan-ids=10
/interface list member
add interface=bridge_main list=LAN
add interface=vlan-mgmt list=Management
/interface wifi
add name=wifi1 configuration.ssid=TestWiFi
/caps-man channel
add band=5ghz-n/ac frequency=5180 name=CH36
/system logging action
set 3 remote=192.168.1.250 remote-log-format=syslog syslog-facility=local0
/system script
add comment="Simple Backup" name="cloud backup" source="/system backup cloud print;"
add comment="Watchdog Script" name=TestWatchdog source="#\\_Script: TestWatchdog.rsc\\n# Description: Fictional Watchdog\\n:log info \\"Checking connection...\\";\\n/system package update check;\\n"
/ip address
add address=192.168.1.1/24 interface=bridge_main
add address=192.168.70.1/24 interface=vlan-mgmt
/ip dns
set allow-remote-requests=yes servers=1.1.1.1,8.8.8.8
/ip route
add distance=1 dst-address=0.0.0.0/0 gateway=192.168.1.254
/ip dhcp-server lease
add address=192.168.1.50 mac-address=AA:BB:CC:DD:EE:01 server=DHCP-Main
/ip firewall filter
add action=accept chain=input comment="Accept Established" connection-state=established,related
add action=drop chain=input comment="Drop Invalid" connection-state=invalid
/interface lte
set [ find default-name=lte1 ] allow-roaming=yes
/tool sms
set port=lte1 receive-enabled=yes
/interface wireguard
add comment="Test VPN" listen-port=51820 name=wg0
"""


def test_fictional_split_e2e_default(tmp_path):
    engine = RSCEngine()
    emitted = engine.split(
        raw_text=FICTIONAL_RSC_EXPORT,
        output_dir=str(tmp_path),
        numbered=True,
        wrap_lines=False
    )

    expected_files = [
        "01-base.rsc",
        "02-wifi.rsc",
        "03-system.rsc",
        "04-ip.rsc",
        "05-dhcp-leases.rsc",
        "06-firewall.rsc",
        "08-lte.rsc",
        "09-wireguard.rsc"
    ]

    for fname in expected_files:
        assert fname in emitted, f"Expected file {fname} not found in emitted: {list(emitted.keys())}"
        assert emitted[fname].strip() != "", f"Emitted file {fname} is empty"

    assert "TestWatchdog.rsc" not in emitted


def test_fictional_split_e2e_extract_scripts(tmp_path):
    engine = RSCEngine()
    emitted = engine.split(
        raw_text=FICTIONAL_RSC_EXPORT,
        output_dir=str(tmp_path),
        numbered=True,
        wrap_lines=False,
        extract_scripts=True
    )

    assert "TestWatchdog.rsc" in emitted
    assert emitted["TestWatchdog.rsc"].strip() != ""


def test_fictional_script_extraction():
    engine = RSCEngine()
    config = engine.parse_and_process(FICTIONAL_RSC_EXPORT, extract_scripts=True)

    script_names = [s.name for s in config.extracted_scripts]
    assert "TestWatchdog" in script_names
    assert "cloud backup" in script_names

    watchdog_script = next(s for s in config.extracted_scripts if s.name == "TestWatchdog")
    assert '# Script: TestWatchdog.rsc' in watchdog_script.source_code
    assert 'Checking connection' in watchdog_script.source_code
