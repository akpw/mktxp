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


from mktxp.cli.config.config import config_handler
from mktxp.router_metric import RouterMetric


class RouterMetricsHandler:
    ''' Handles RouterOS entries defined in MKTXP config 
    '''         
    def __init__(self):
        self.router_metrics = []
        for router_name in config_handler.registered_entries():
            entry = config_handler.entry(router_name)
            if entry.enabled:
                self.router_metrics.append(RouterMetric(router_name))


