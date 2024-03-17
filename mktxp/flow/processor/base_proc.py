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

from waitress import serve


class ExportProcessor:
    ''' Base Export Processing
    '''    
    @staticmethod
    def start():
        REGISTRY.register(CollectorHandler(RouterEntriesHandler(), CollectorRegistry()))
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f'{current_time} Running HTTP metrics server on: {config_handler.system_entry.listen}')
        serve(make_wsgi_app(), listen = config_handler.system_entry.listen)

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

            
