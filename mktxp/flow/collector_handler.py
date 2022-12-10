# coding=utf8
## Copyright (c) 2020 Arseniy Kuznenowov
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


from timeit import default_timer
from datetime import datetime
from mktxp.cli.config.config import config_handler

class CollectorHandler:
    ''' MKTXP Collectors Handler
    '''
    def __init__(self, entries_handler, collector_registry):
        self.entries_handler = entries_handler
        self.collector_registry = collector_registry
        self.last_collect_timestamp = 0       

    def collect(self):
        now =  datetime.now().timestamp()  
        diff = now - self.last_collect_timestamp    
        if diff < config_handler.system_entry().minimal_collect_interval:
            if config_handler.system_entry().verbose_mode:
                print(f'An attemp to collect metrics within minimal collection interval: {diff} < {config_handler.system_entry().minimal_collect_interval}')
                print('deferring..')
            return
        self.last_collect_timestamp = now

        yield from self.collector_registry.bandwidthCollector.collect()

        for router_entry in self.entries_handler.router_entries:
            if not router_entry.api_connection.is_connected():
                # let's pick up on things in the next run
                router_entry.api_connection.connect()
                continue

            for collector_ID, collect_func in self.collector_registry.registered_collectors.items():                
                start = default_timer()
                yield from collect_func(router_entry)
                router_entry.time_spent[collector_ID] += default_timer() - start




