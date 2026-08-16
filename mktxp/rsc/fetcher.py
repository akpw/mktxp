# coding=utf8
## Copyright (c) 2026 Arseniy Kuznetsov
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

import os
import shutil
import subprocess
from typing import Any, Dict, List, Optional

import yaml


class SSHExportFetcher:
    """
    Connects to a RouterOS device over native SSH using key-based authentication
    and fetches the live configuration export into memory without extra dependencies.
    """

    def __init__(
        self,
        hostname: str,
        username: str = "admin",
        ssh_key_file: Optional[str] = None,
        port: int = 22,
        timeout: int = 15,
        show_sensitive: bool = False,
    ):
        self.hostname = hostname
        self.username = username
        self.ssh_key_file = os.path.expanduser(ssh_key_file) if ssh_key_file else None
        self.port = int(port)
        self.timeout = int(timeout)
        self.show_sensitive = show_sensitive

    @classmethod
    def from_config_entry(
        cls,
        entry_name: str,
        config_entry,
        rsc_conf: Optional[Dict[str, Any]] = None,
        cli_overrides: Optional[Dict[str, Any]] = None,
    ) -> "SSHExportFetcher":
        rsc_conf = rsc_conf or {}
        cli_overrides = cli_overrides or {}

        hostname = config_entry.hostname
        username = config_entry.username or "admin"
        ssh_key_file = None

        # Check credentials_file if specified
        if config_entry.credentials_file and os.path.exists(
            config_entry.credentials_file
        ):
            try:
                with open(config_entry.credentials_file, "r", encoding="utf8") as f:
                    creds = yaml.safe_load(f)
                    if isinstance(creds, dict):
                        username = creds.get("username", username)
                        ssh_key_file = creds.get("ssh_key_file") or creds.get(
                            "ssh_key", ssh_key_file
                        )
            except Exception as exc:
                print(
                    f"Warning: Failed reading credentials file {config_entry.credentials_file}: {exc}"
                )

        # SSH port resolution
        ssh_port = cli_overrides.get("ssh_port") or rsc_conf.get("ssh_port") or 22

        # Timeout resolution
        ssh_timeout = int(rsc_conf.get("ssh_timeout", 15))

        # Show sensitive resolution
        show_sensitive_conf = rsc_conf.get("show_sensitive", False)
        if isinstance(show_sensitive_conf, str):
            show_sensitive_conf = show_sensitive_conf.lower() in ("true", "1", "yes")
        show_sensitive = bool(
            cli_overrides.get("show_sensitive", False) or show_sensitive_conf
        )

        # CLI overrides
        if cli_overrides.get("user"):
            username = cli_overrides["user"]
        if cli_overrides.get("ssh_key"):
            ssh_key_file = cli_overrides["ssh_key"]

        return cls(
            hostname=hostname,
            username=username,
            ssh_key_file=ssh_key_file,
            port=int(ssh_port),
            timeout=ssh_timeout,
            show_sensitive=show_sensitive,
        )

    def _build_ssh_command(self) -> List[str]:
        export_cmd = "/export show-sensitive" if self.show_sensitive else "/export"

        cmd = [
            "ssh",
            "-p",
            str(self.port),
            "-o",
            "BatchMode=yes",
            "-o",
            f"ConnectTimeout={self.timeout}",
            "-o",
            "StrictHostKeyChecking=accept-new",
            "-o",
            "LogLevel=ERROR",
        ]

        if self.ssh_key_file:
            cmd.extend(["-i", self.ssh_key_file])

        target = f"{self.username}@{self.hostname}"
        cmd.extend([target, export_cmd])
        return cmd

    def fetch_export(self) -> str:
        """
        Executes '/export' (or '/export show-sensitive') on the router via native SSH
        using key-based authentication and returns the raw configuration string.
        """
        if not shutil.which("ssh"):
            raise RuntimeError("Native 'ssh' binary not found in system PATH.")

        cmd = self._build_ssh_command()

        try:
            res = subprocess.run(
                cmd, capture_output=True, text=True, timeout=self.timeout + 10
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(
                f"SSH connection to {self.username}@{self.hostname}:{self.port} timed out after {self.timeout}s."
            ) from exc
        except Exception as exc:
            raise RuntimeError(f"Failed to execute SSH command: {exc}") from exc

        if res.returncode != 0:
            err_msg = (
                res.stderr.strip()
                if res.stderr
                else f"Process exited with code {res.returncode}"
            )
            raise RuntimeError(
                f"SSH export failed for {self.username}@{self.hostname}:{self.port} ({err_msg}).\n"
                "Note: Live RouterOS export uses native SSH and requires SSH key authentication "
                "(e.g. ~/.ssh/id_ed25519, ssh-agent, or --ssh-key)."
            )

        return res.stdout
