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
from prometheus_client.core import REGISTRY
from prometheus_client import make_wsgi_app

from mktxp.cli.config.config import config_handler
from mktxp.flow.collector_handler import CollectorHandler
from mktxp.flow.collector_registry import CollectorRegistry
from mktxp.flow.router_entries_handler import RouterEntriesHandler

from mktxp.cli.output.capsman_out import CapsmanOutput
from mktxp.cli.output.wifi_out import WirelessOutput
from mktxp.cli.output.dhcp_out import DHCPOutput
from mktxp.cli.output.conn_stats_out import ConnectionsStatsOutput
from mktxp.cli.output.kid_control_out import KidControlOutput
from mktxp.cli.output.address_list_out import AddressListOutput
from mktxp.cli.output.netwatch_out import NetwatchOutput

import gzip
from waitress import serve

class PrometheusHeadersDeduplicatingMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        captured_status = []
        captured_headers = []

        def custom_start_response(status, headers, exc_info=None):
            captured_status.append(status)
            captured_headers.append(headers)

        app_iter = self.app(environ, custom_start_response)
        body = b''.join(app_iter)

        response_headers = dict(captured_headers[0])
        is_gzipped = response_headers.get('Content-Encoding') == 'gzip'

        if is_gzipped:
            try:
                uncompressed_body = gzip.decompress(body)
            except gzip.BadGzipFile:
                uncompressed_body = body
        else:
            uncompressed_body = body

        lines = uncompressed_body.decode('utf-8').split('\n')
        seen_headers = set()
        output_lines = []
        for line in lines:
            if line.startswith('# HELP') or line.startswith('# TYPE'):
                if line in seen_headers:
                    continue
                seen_headers.add(line)
            output_lines.append(line)

        processed_text = '\n'.join(output_lines)

        if is_gzipped:
            output_body = gzip.compress(processed_text.encode('utf-8'))
        else:
            output_body = processed_text.encode('utf-8')

        status = captured_status[0]
        original_headers = captured_headers[0]

        new_headers = []
        for k, v in original_headers:
            if k.lower() == 'content-length':
                new_headers.append((k, str(len(output_body))))
            else:
                new_headers.append((k, v))

        start_response(status, new_headers)
        return [output_body]

class ExportProcessor:
    ''' Base Export Processing
    '''    
    @staticmethod
    def start():
        REGISTRY.register(CollectorHandler(RouterEntriesHandler(), CollectorRegistry()))
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f'{current_time} Running HTTP metrics server on: {config_handler.system_entry.listen}')

        app = make_wsgi_app()
        if config_handler.system_entry.prometheus_headers_deduplication:
            if config_handler.system_entry.verbose_mode:
                print(f"Prometheus HELP / TYPE headers de-deplucation is On")
            middleware = PrometheusHeadersDeduplicatingMiddleware(app)
            serve(middleware, listen = config_handler.system_entry.listen)
        else:
            serve(app, listen = config_handler.system_entry.listen)

class OutputProcessor:
    ''' Base CLI Processing
    '''    
    @staticmethod
    def capsman_clients(entry_name):
        router_entry = RouterEntriesHandler.router_entry(entry_name)
        if router_entry:
            CapsmanOutput.clients_summary(router_entry)
        
    @staticmethod
    def wifi_clients(entry_name):
        router_entry = RouterEntriesHandler.router_entry(entry_name)
        if router_entry:
            WirelessOutput.clients_summary(router_entry)
        
    @staticmethod
    def dhcp_clients(entry_name):
        router_entry = RouterEntriesHandler.router_entry(entry_name)
        if router_entry:
            DHCPOutput.clients_summary(router_entry)

    @staticmethod
    def conn_stats(entry_name):
        router_entry = RouterEntriesHandler.router_entry(entry_name)
        if router_entry:
            ConnectionsStatsOutput.clients_summary(router_entry)

    @staticmethod
    def kid_control(entry_name):
        router_entry = RouterEntriesHandler.router_entry(entry_name)
        if router_entry:
            KidControlOutput.clients_summary(router_entry)

    @staticmethod
    def address_lists(entry_name, address_lists_str):
        router_entry = RouterEntriesHandler.router_entry(entry_name)
        if router_entry:
            AddressListOutput.clients_summary(router_entry, address_lists_str)

    @staticmethod
    def netwatch(entry_name):
        router_entry = RouterEntriesHandler.router_entry(entry_name)
        if router_entry:
            NetwatchOutput.clients_summary(router_entry)

            
