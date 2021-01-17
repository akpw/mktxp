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
from prometheus_client import MetricsHandler, start_http_server
from mktxp.cli.config.config import config_handler
from mktxp.collectors_handler import CollectorsHandler
from mktxp.metrics_handler import RouterMetricsHandler

from mktxp.cli.output.capsman_out import CapsmanOutput
from mktxp.cli.output.wifi_out import WirelessOutput

class MKTXPProcessor:
    ''' Base Export Processing
    '''    
    @staticmethod
    def start():
        router_metrics_handler = RouterMetricsHandler()
        REGISTRY.register(CollectorsHandler(router_metrics_handler))
        MKTXPProcessor.run(port=config_handler._entry().port)

    @staticmethod
    def run(server_class=HTTPServer, handler_class=MetricsHandler, port = None):
        server_address = ('', port)
        httpd = server_class(server_address, handler_class)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f'{current_time} Running HTTP metrics server on port {port}')
        httpd.serve_forever()


class MKTXPCLIProcessor:
    ''' Base CLI Processing
    '''    
    @staticmethod
    def capsman_clients(entry_name):
        router_metric = RouterMetricsHandler.router_metric(entry_name)
        if router_metric:
            CapsmanOutput.clients_summary(router_metric)
        
    @staticmethod
    def wifi_clients(entry_name):
        router_metric = RouterMetricsHandler.router_metric(entry_name)
        if router_metric:
            WirelessOutput.clients_summary(router_metric)
        
