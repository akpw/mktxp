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

from datetime import datetime
from prometheus_client import make_wsgi_app
from prometheus_client.core import REGISTRY
from waitress import serve

from mktxp.cli.config import config_handler
from mktxp.exporter.middleware import PrometheusHeadersDeduplicatingMiddleware
from mktxp.exporter.router import MetricsRouter
from mktxp.flow.collector_handler import CollectorHandler
from mktxp.flow.collector_registry import CollectorRegistry as MKTXPCollectorRegistry
from mktxp.flow.router_entries_handler import RouterEntriesHandler


class ExportProcessor:
    """Manages the Prometheus HTTP metrics exporter daemon lifecycle."""

    @staticmethod
    def start():
        REGISTRY.register(CollectorHandler(RouterEntriesHandler(), MKTXPCollectorRegistry()))
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{current_time} Running HTTP metrics server on: {config_handler.system_entry.listen}")

        metrics_app = make_wsgi_app()
        app = MetricsRouter(metrics_app)
        if config_handler.system_entry.prometheus_headers_deduplication:
            if config_handler.system_entry.verbose_mode:
                print("Prometheus HELP / TYPE headers de-deplucation is On")
            middleware = PrometheusHeadersDeduplicatingMiddleware(app)
            serve(
                middleware,
                listen=config_handler.system_entry.listen,
                threads=config_handler.system_entry.http_server_threads,
            )
        else:
            serve(
                app,
                listen=config_handler.system_entry.listen,
                threads=config_handler.system_entry.http_server_threads,
            )
