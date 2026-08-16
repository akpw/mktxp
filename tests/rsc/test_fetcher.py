# coding=utf8
import os
import subprocess
import pytest
from unittest.mock import MagicMock, patch
from mktxp.rsc.fetcher import SSHExportFetcher


class MockConfigEntry:
    def __init__(self, hostname="192.168.1.1", username="admin", password="password123", credentials_file=None):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.credentials_file = credentials_file


def test_fetcher_init():
    fetcher = SSHExportFetcher(
        hostname="192.168.88.1",
        username="mktxp_user",
        ssh_key_file="~/.ssh/id_ed25519",
        port=2222,
        timeout=20,
        show_sensitive=True
    )
    assert fetcher.hostname == "192.168.88.1"
    assert fetcher.username == "mktxp_user"
    assert fetcher.port == 2222
    assert fetcher.timeout == 20
    assert fetcher.show_sensitive is True


def test_fetcher_from_config_entry(tmp_path):
    creds_file = tmp_path / "creds.yaml"
    creds_file.write_text("username: custom_user\nssh_key_file: /path/to/key\n")

    entry = MockConfigEntry(credentials_file=str(creds_file))
    rsc_conf = {"ssh_port": 2200, "ssh_timeout": 30, "show_sensitive": False}
    cli_overrides = {"user": "cli_user", "show_sensitive": True}

    fetcher = SSHExportFetcher.from_config_entry(
        entry_name="TestRouter",
        config_entry=entry,
        rsc_conf=rsc_conf,
        cli_overrides=cli_overrides
    )

    assert fetcher.hostname == "192.168.1.1"
    assert fetcher.username == "cli_user"  # CLI override precedence
    assert fetcher.ssh_key_file == "/path/to/key"
    assert fetcher.port == 2200
    assert fetcher.timeout == 30
    assert fetcher.show_sensitive is True


def test_fetcher_build_ssh_command():
    fetcher = SSHExportFetcher(
        hostname="192.168.88.1",
        username="admin",
        ssh_key_file="/path/to/key",
        port=2222,
        timeout=10,
        show_sensitive=False
    )
    cmd = fetcher._build_ssh_command()
    assert cmd[0] == 'ssh'
    assert '-p' in cmd and '2222' in cmd
    assert '-i' in cmd and '/path/to/key' in cmd
    assert 'admin@192.168.88.1' in cmd
    assert cmd[-1] == '/export'


@patch('shutil.which', return_value='/usr/bin/ssh')
@patch('subprocess.run')
def test_fetcher_fetch_export_default(mock_run, mock_which):
    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "# RouterOS Export\n/interface bridge add name=br0\n"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    fetcher = SSHExportFetcher(hostname="192.168.88.1", username="admin", show_sensitive=False)
    result = fetcher.fetch_export()

    mock_run.assert_called_once()
    called_cmd = mock_run.call_args[0][0]
    assert called_cmd[-1] == '/export'
    assert "/interface bridge add name=br0" in result


@patch('shutil.which', return_value='/usr/bin/ssh')
@patch('subprocess.run')
def test_fetcher_fetch_export_show_sensitive(mock_run, mock_which):
    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "# Sensitive Export\n/user add password=secret\n"
    mock_res.stderr = ""
    mock_run.return_value = mock_res

    fetcher = SSHExportFetcher(hostname="192.168.88.1", username="admin", show_sensitive=True)
    result = fetcher.fetch_export()

    called_cmd = mock_run.call_args[0][0]
    assert called_cmd[-1] == '/export show-sensitive'
    assert "/user add password=secret" in result


@patch('shutil.which', return_value='/usr/bin/ssh')
@patch('subprocess.run')
def test_fetcher_fetch_export_error(mock_run, mock_which):
    mock_res = MagicMock()
    mock_res.returncode = 255
    mock_res.stderr = "Permission denied (publickey)."
    mock_run.return_value = mock_res

    fetcher = SSHExportFetcher(hostname="192.168.88.1")
    with pytest.raises(RuntimeError) as exc_info:
        fetcher.fetch_export()

    assert "Permission denied" in str(exc_info.value)
    assert "SSH key authentication" in str(exc_info.value)
