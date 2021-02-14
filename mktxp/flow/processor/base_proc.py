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


from http.server import HTTPServer
from datetime import datetime
from prometheus_client.core import REGISTRY
from prometheus_client import MetricsHandler

from mktxp.cli.config.config import config_handler
from mktxp.flow.collector_handler import CollectorHandler
from mktxp.flow.collector_registry import CollectorRegistry
from mktxp.flow.router_entries_handler import RouterEntriesHandler

from mktxp.cli.output.capsman_out import CapsmanOutput
from mktxp.cli.output.wifi_out import WirelessOutput
from mktxp.cli.output.dhcp_out import DHCPOutput


class ExportProcessor:
    ''' Base Export Processing
    '''    
    @staticmethod
    def start():
        REGISTRY.register(CollectorHandler(RouterEntriesHandler(), CollectorRegistry()))
        ExportProcessor.run(port=config_handler.system_entry().port)

    @staticmethod
    def run(server_class=HTTPServer, handler_class=MetricsHandler, port=None):
        server_address = ('', port)
        httpd = server_class(server_address, handler_class)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f'{current_time} Running HTTP metrics server on port {port}')
        httpd.serve_forever()


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
