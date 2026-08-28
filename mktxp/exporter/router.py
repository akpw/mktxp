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

from urllib.parse import parse_qs
from prometheus_client import make_wsgi_app, CollectorRegistry as PrometheusCollectorRegistry

from mktxp.cli.config import config_handler
from mktxp.flow.collector_handler import ProbeCollectorHandler
from mktxp.flow.collector_registry import CollectorRegistry as MKTXPCollectorRegistry
from mktxp.flow.probe_connection_pool import ProbeConnectionPool
from mktxp.flow.probe_entries_provider import ProbeEntriesProvider


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
        if config_entry.module_only and not target:
            return self._error(start_response, f"Module '{module}' requires a target override")

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
    def _error(start_response, message):
        body = f"Error: {message}\n".encode("utf-8")
        start_response(
            "503 Service Unavailable",
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
