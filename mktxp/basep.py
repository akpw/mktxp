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
from prometheus_client.core import REGISTRY
from prometheus_client import MetricsHandler, start_http_server
from mktxp.collectors_handler import CollectorsHandler
from mktxp.metrics_handler import RouterMetricsHandler


class MKTXPProcessor:
    ''' Base Export Processing
    '''    
    @staticmethod
    def start():
        router_metrics_handler = RouterMetricsHandler()
        REGISTRY.register(CollectorsHandler(router_metrics_handler))
        MKTXPProcessor.run()

    @staticmethod
    def run(server_class=HTTPServer, handler_class=MetricsHandler, port=8000):
        server_address = ('', port)
        httpd = server_class(server_address, handler_class)
        httpd.serve_forever()
