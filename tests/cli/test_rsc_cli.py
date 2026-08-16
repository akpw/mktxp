# coding=utf8
import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from mktxp.cli.dispatch import MKTXPDispatcher


MOCK_RSC_EXPORT = """# 2026-08-14 by RouterOS 7.23.3
# model = MockRouter
/interface bridge
add name=bridge_main vlan-filtering=yes
/interface vlan
add interface=bridge_main name=vlan-mgmt vlan-id=70
/interface wifi
add name=wifi1 configuration.ssid=MockWiFi
/system script
add name=MockScript source="#\\_Script: MockScript.rsc\\n:log info \\"Mock Running\\";\\n"
/ip address
add address=192.168.1.1/24 interface=bridge_main
/ip firewall filter
add action=accept chain=input comment="Accept Established"
add action=drop chain=input comment="Drop Invalid"
/interface wireguard
add name=wg0 listen-port=13231
"""


@pytest.fixture
def mock_rsc_file(tmp_path):
    input_file = os.path.join(tmp_path, "mock_export.rsc")
    with open(input_file, 'w', encoding='utf8') as f:
        f.write(MOCK_RSC_EXPORT)
    return input_file


def test_cli_rsc_format(mock_rsc_file, tmp_path, capsys):
    out_file = os.path.join(tmp_path, "clean_export.rsc")
    test_args = ["mktxp", "rsc", "format", "-i", mock_rsc_file, "-o", out_file]

    with patch.object(sys, 'argv', test_args):
        dispatcher = MKTXPDispatcher()
        res = dispatcher.dispatch()
        assert res is True

    assert os.path.isfile(out_file)
    with open(out_file, 'r', encoding='utf8') as f:
        content = f.read()
    assert "# Section: /interface bridge" in content
    assert "/interface bridge" in content


def test_cli_rsc_split(mock_rsc_file, tmp_path, capsys):
    out_dir = os.path.join(tmp_path, "split_out")
    test_args = ["mktxp", "rsc", "split", "-i", mock_rsc_file, "-d", out_dir]

    with patch.object(sys, 'argv', test_args):
        dispatcher = MKTXPDispatcher()
        res = dispatcher.dispatch()
        assert res is True

    captured = capsys.readouterr()
    assert "Successfully split RouterOS export" in captured.out

    files = os.listdir(out_dir)
    assert "01-base.rsc" in files
    assert "02-wifi.rsc" in files
    assert "03-system.rsc" in files
    assert "04-ip.rsc" in files
    assert "06-firewall.rsc" in files
    assert "08-wireguard.rsc" in files
    assert "MockScript.rsc" not in files  # Embedded by default


def test_cli_rsc_split_extract_scripts(mock_rsc_file, tmp_path, capsys):
    out_dir = os.path.join(tmp_path, "split_out_extracted")
    test_args = ["mktxp", "rsc", "split", "-i", mock_rsc_file, "-d", out_dir, "--extract-scripts"]

    with patch.object(sys, 'argv', test_args):
        dispatcher = MKTXPDispatcher()
        res = dispatcher.dispatch()
        assert res is True

    files = os.listdir(out_dir)
    assert "MockScript.rsc" in files


@patch('mktxp.cli.dispatch.config_handler')
def test_cli_rsc_split_default_dir(mock_dispatch_handler, mock_rsc_file, tmp_path, capsys):
    mock_dispatch_handler.rsc_config.return_value = {"base_dir": str(tmp_path)}
    test_args = ["mktxp", "rsc", "split", "-i", mock_rsc_file]

    with patch.object(sys, 'argv', test_args):
        dispatcher = MKTXPDispatcher()
        res = dispatcher.dispatch()
        assert res is True

    # Expect folder named after file stem: mock_export
    expected_dir = os.path.join(tmp_path, "mock_export")
    assert os.path.isdir(expected_dir)
    files = os.listdir(expected_dir)
    assert "01-base.rsc" in files
    assert "06-firewall.rsc" in files


@patch('mktxp.cli.options.config_handler')
@patch('mktxp.cli.dispatch.config_handler')
@patch('mktxp.rsc.fetcher.SSHExportFetcher.fetch_export')
def test_cli_rsc_live_format(mock_fetch_export, mock_dispatch_handler, mock_options_handler, tmp_path, capsys):
    mock_fetch_export.return_value = MOCK_RSC_EXPORT

    mock_entry = MagicMock()
    mock_entry.hostname = "192.168.1.1"
    mock_entry.username = "admin"
    mock_entry.password = "pass"
    mock_entry.credentials_file = None

    for h in (mock_options_handler, mock_dispatch_handler):
        h.registered_entries.return_value = ["MockRouter"]
        h.config_entry.return_value = mock_entry
        h.rsc_config.return_value = {"base_dir": str(tmp_path)}

    out_file = os.path.join(tmp_path, "live_clean.rsc")
    test_args = ["mktxp", "rsc", "format", "-en", "MockRouter", "-o", out_file, "--show-sensitive"]

    with patch.object(sys, 'argv', test_args):
        dispatcher = MKTXPDispatcher()
        res = dispatcher.dispatch()
        assert res is True

    assert os.path.isfile(out_file)
    with open(out_file, 'r', encoding='utf8') as f:
        content = f.read()
    assert "# Section: /interface bridge" in content


@patch('mktxp.cli.options.config_handler')
@patch('mktxp.cli.dispatch.config_handler')
@patch('mktxp.rsc.fetcher.SSHExportFetcher.fetch_export')
def test_cli_rsc_live_split(mock_fetch_export, mock_dispatch_handler, mock_options_handler, tmp_path, capsys):
    mock_fetch_export.return_value = MOCK_RSC_EXPORT

    mock_entry = MagicMock()
    mock_entry.hostname = "192.168.1.1"
    mock_entry.username = "admin"
    mock_entry.password = "pass"
    mock_entry.credentials_file = None

    for h in (mock_options_handler, mock_dispatch_handler):
        h.registered_entries.return_value = ["MockRouter"]
        h.config_entry.return_value = mock_entry
        h.rsc_config.return_value = {"base_dir": str(tmp_path)}

    # Without -d, should auto-split into <base_dir>/MockRouter/
    test_args = ["mktxp", "rsc", "split", "-en", "MockRouter"]

    with patch.object(sys, 'argv', test_args):
        dispatcher = MKTXPDispatcher()
        res = dispatcher.dispatch()
        assert res is True

    target_dir = os.path.join(tmp_path, "MockRouter")
    assert os.path.isdir(target_dir)
    files = os.listdir(target_dir)
    assert "01-base.rsc" in files
    assert "06-firewall.rsc" in files
