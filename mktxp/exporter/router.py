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

import ipaddress
from urllib.parse import parse_qs
from prometheus_client import make_wsgi_app, CollectorRegistry as PrometheusCollectorRegistry

from mktxp.cli.config import config_handler
from mktxp.flow.collector_handler import ProbeCollectorHandler
from mktxp.flow.collector_registry import CollectorRegistry as MKTXPCollectorRegistry
from mktxp.flow.probe_connection_pool import ProbeConnectionPool
from mktxp.flow.probe_entries_provider import ProbeEntriesProvider


def parse_allowed_targets(allowed_targets):
    """Parses allowed targets configuration into a list of normalized strings."""
    if not allowed_targets or allowed_targets == 'None':
        return []
    if isinstance(allowed_targets, str):
        items = [item.strip() for item in allowed_targets.split(',')]
    elif isinstance(allowed_targets, (list, tuple)):
        items = []
        for item in allowed_targets:
            if isinstance(item, str):
                items.extend([sub.strip() for sub in item.split(',')])
            else:
                items.append(str(item).strip())
    else:
        return []
    return [item for item in items if item and item != 'None']


def is_target_allowed(target: str, allowed_targets: list) -> bool:
    """
    Checks whether a probe target is permitted by the allowed_targets list.
    Supports:
    - '*' : wildcard allowing all targets
    - IP addresses and CIDR subnets (e.g. '192.168.88.0/24', '10.0.0.1', '2001:db8::/32')
    - Domain wildcards (e.g. '*.internal', '.corp.local')
    - Exact hostnames (e.g. 'router1.lan', 'localhost')
    """
    if not target or not allowed_targets:
        return False

    target_str = target.strip()
    target_clean = target_str.strip('[]')
    target_ip = None
    try:
        target_ip = ipaddress.ip_address(target_clean)
    except ValueError:
        target_ip = None

    for rule in allowed_targets:
        rule = rule.strip()
        if not rule:
            continue
        if rule == '*':
            return True

        if target_ip is not None:
            try:
                network = ipaddress.ip_network(rule, strict=False)
                if target_ip in network:
                    return True
            except ValueError:
                pass

        target_lower = target_str.lower()
        rule_lower = rule.lower()

        if target_lower == rule_lower:
            return True

        if rule_lower.startswith('*.'):
            suffix = rule_lower[1:]  # e.g. .corp.local
            if target_lower.endswith(suffix):
                return True
        elif rule_lower.startswith('.'):
            if target_lower.endswith(rule_lower):
                return True

    return False


class MetricsRouter:
    """WSGI Router handling /metrics standard scrapes and multi-target /probe requests."""

    def __init__(self, metrics_app):
        self.metrics_app = metrics_app
        self.probe_connection_pool = None
        if config_handler.system_entry.probe_connection_pool:
            self.probe_connection_pool = ProbeConnectionPool(
                config_handler.system_entry.probe_connection_pool_max_size,
                config_handler.system_entry.probe_connection_pool_ttl,
            )

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "")
        if path == "/probe":
            if not getattr(config_handler.system_entry, "enable_probe", True):
                return self._error(
                    start_response,
                    "Probe endpoint is disabled in configuration",
                    status="403 Forbidden",
                )
            return self._handle_probe(environ, start_response)
        return self.metrics_app(environ, start_response)

    def _handle_probe(self, environ, start_response):
        query = parse_qs(environ.get("QUERY_STRING", ""), keep_blank_values=True)
        modules = query.get("module", [])
        if len(modules) != 1 or not modules[0].strip():
            return self._error(start_response, "Missing or invalid 'module' parameter")

        module = modules[0].strip()
        if not config_handler.registered_entry(module):
            return self._error(start_response, f"Unknown module '{module}'")
        config_entry = config_handler.config_entry(module)
        if not config_entry or not config_entry.enabled:
            return self._error(start_response, f"Module '{module}' is disabled")

        targets = query.get("target", [])
        if len(targets) > 1:
            return self._error(start_response, "Multiple 'target' parameters are not supported")
        if len(targets) == 1 and not targets[0].strip():
            return self._error(start_response, "Invalid 'target' parameter")

        target = targets[0].strip() if len(targets) == 1 else None

        if not config_entry.module_only and target and target != config_entry.hostname:
            return self._error(
                start_response,
                f"Target override is not allowed for static module '{module}'. Only modules configured with module_only = True accept dynamic targets.",
                status="403 Forbidden",
            )

        if config_entry.module_only:
            if not target:
                return self._error(start_response, f"Module '{module}' requires a target override")

            raw_allowed = getattr(config_entry, "probe_allowed_targets", None)
            if not raw_allowed or raw_allowed == "None":
                raw_allowed = getattr(config_handler.system_entry, "probe_allowed_targets", None)

            allowed_targets = parse_allowed_targets(raw_allowed)
            if not allowed_targets:
                return self._error(
                    start_response,
                    f"Target override rejected: module '{module}' has no probe_allowed_targets defined. Specify allowed target IPs, CIDRs, or hostnames in configuration (or '*' to permit all).",
                    status="403 Forbidden",
                )

            if not is_target_allowed(target, allowed_targets):
                return self._error(
                    start_response,
                    f"Target '{target}' is not allowed for module '{module}'",
                    status="403 Forbidden",
                )

        config_override = config_entry._replace(hostname=target) if target else None
        probe_entries = ProbeEntriesProvider(
            module,
            config_override or config_entry,
            connection_pool=self.probe_connection_pool,
        )
        registry = PrometheusCollectorRegistry()
        registry.register(
            ProbeCollectorHandler(
                probe_entries,
                MKTXPCollectorRegistry(),
            )
        )
        probe_app = make_wsgi_app(registry=registry)
        return self._safe_probe_response(probe_app, environ, start_response, module, target)

    @staticmethod
    def _error(start_response, message, status="503 Service Unavailable"):
        body = f"Error: {message}\n".encode("utf-8")
        start_response(
            status,
            [
                ("Content-Type", "text/plain; charset=utf-8"),
                ("Content-Length", str(len(body))),
            ],
        )
        return [body]

    def _safe_probe_response(self, probe_app, environ, start_response, module, target):
        captured = []

        def probe_start_response(status, headers, exc_info=None):
            captured.append((status, headers))

        try:
            body = b"".join(probe_app(environ, probe_start_response))
        except Exception as exc:
            suffix = f"@{target}" if target else ""
            return self._error(start_response, f"Probe failed for module '{module}': {exc}{suffix}")

        status, headers = captured[0]
        start_response(status, headers)
        return [body]
