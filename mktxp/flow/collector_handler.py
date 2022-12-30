# coding=utf8
# Copyright (c) 2020 Arseniy Kuznenowov
##
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
##
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

from concurrent.futures import ThreadPoolExecutor, as_completed
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

    def collect_synchronous(self):
        """
        Collect the metrics of all router entries defined in the current users configuration synchronously.
        This function iterates over each router entry one-by-one.
        Thus, the total runtime of this function scales linearly with the number of registered routers.
        """
        for router_entry in self.entries_handler.router_entries:
            if not router_entry.api_connection.is_connected():
                # let's pick up on things in the next run
                router_entry.api_connection.connect()
                continue

            for collector_ID, collect_func in self.collector_registry.registered_collectors.items():
                start = default_timer()
                yield from collect_func(router_entry)
                router_entry.time_spent[collector_ID] += default_timer() - start

    def collect_single(self, router_entry):
        results = []
        for collector_ID, collect_func in self.collector_registry.registered_collectors.items():
            start = default_timer()
            result = list(collect_func(router_entry))
            results += result
            router_entry.time_spent[collector_ID] += default_timer() - start
        return results

    def collect_parallel(self, max_worker_threads=5):
        """
        Collect the metrics of all router entries defined in the current users configuration in parallel.
        This function iterates over multiple routers in parallel (depending on the value of max_worker_threads).
        Thus, the total runtime scales sub linearly (number_of_routers / max_worker_threads).
        """
        with ThreadPoolExecutor(max_workers=max_worker_threads) as executor:
            futures = []

            for router_entry in self.entries_handler.router_entries:
                if not router_entry.api_connection.is_connected():
                    # let's pick up on things in the next run
                    router_entry.api_connection.connect()
                    continue
                
                # Publish the collection function as a future
                futures.append(executor.submit(self.collect_single, router_entry))

            for future in as_completed(futures):
                yield from future.result()


    def collect(self):
        now = datetime.now().timestamp()
        diff = now - self.last_collect_timestamp
        if diff < config_handler.system_entry().minimal_collect_interval:
            if config_handler.system_entry().verbose_mode:
                print(f'An attemp to collect metrics within minimal collection interval: {diff} < {config_handler.system_entry().minimal_collect_interval}')
                print('deferring..')
            return
        self.last_collect_timestamp = now

        yield from self.collector_registry.bandwidthCollector.collect()

        # Check whether to run in parallel by looking at the mktxp system configuration
        parallel = config_handler.system_entry().fetch_routers_in_parallel
        max_worker_threads = config_handler.system_entry().max_worker_threads
        if parallel:
            yield from self.collect_parallel(max_worker_threads=max_worker_threads)
        else:
            yield from self.collect_synchronous()
