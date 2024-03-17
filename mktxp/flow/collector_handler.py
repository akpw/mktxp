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

from concurrent.futures import ThreadPoolExecutor, as_completed
from timeit import default_timer
from datetime import datetime
from threading import Event, Timer
from mktxp.cli.config.config import config_handler
from mktxp.cli.config.config import MKTXPConfigKeys

class CollectorHandler:
    ''' MKTXP Collectors Handler
    '''

    def __init__(self, entries_handler, collector_registry):
        self.entries_handler = entries_handler
        self.collector_registry = collector_registry
        self.last_collect_timestamp = 0


    def collect_sync(self):
        """
        Collect the metrics of all router entries defined in the current users configuration synchronously.
        This function iterates over each router entry one-by-one.
        Thus, the total runtime of this function scales linearly with the number of registered routers.
        """
        for router_entry in self.entries_handler.router_entries:
            if not router_entry.is_ready():
                # let's pick up on things in the next run
                continue

            for collector_ID, collect_func in self.collector_registry.registered_collectors.items():
                start = default_timer()
                yield from collect_func(router_entry)
                router_entry.time_spent[collector_ID] += default_timer() - start
                router_entry.is_done()

    def collect_router_entry_async(self, router_entry, scrape_timeout_event, total_scrape_timeout_event):
        results = []
        for collector_ID, collect_func in self.collector_registry.registered_collectors.items():
            if scrape_timeout_event.is_set():
                print(f'Hit timeout while scraping router entry: {router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_NAME]}')
                break

            if total_scrape_timeout_event.is_set():
                print(f'Hit overall timeout while scraping router entry: {router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_NAME]}')
                break

            start = default_timer()
            result = list(collect_func(router_entry))
            results += result
            router_entry.time_spent[collector_ID] += default_timer() - start
            router_entry.is_done()

        return results


    def collect_async(self, max_worker_threads=5):
        """
        Collect the metrics of all router entries defined in the current users configuration in parallel.
        This function iterates over multiple routers in parallel (depending on the value of max_worker_threads).
        Thus, the total runtime scales sub linearly (number_of_routers / max_worker_threads).
        """

        def timeout(timeout_event):
            timeout_event.set()

        # overall scrape duration 
        total_scrape_timeout_event = Event()
        total_scrape_timer = Timer(config_handler.system_entry.total_max_scrape_duration, timeout, args=(total_scrape_timeout_event,))
        total_scrape_timer.start()

        with ThreadPoolExecutor(max_workers=max_worker_threads) as executor:
            futures = {}

            for router_entry in self.entries_handler.router_entries:
                if total_scrape_timeout_event.is_set():
                    print(f'Hit overall timeout while scraping router entry: {router_entry.router_id[MKTXPConfigKeys.ROUTERBOARD_NAME]}')
                    break

                if not router_entry.is_ready():
                    # let's pick up on things in the next run
                    continue
                
                # Duration of individual scrapes
                scrape_timeout_event = Event()
                scrape_timer = Timer(config_handler.system_entry.max_scrape_duration, timeout, args=(scrape_timeout_event,))
                scrape_timer.start()

                futures[executor.submit(self.collect_router_entry_async, router_entry, scrape_timeout_event, total_scrape_timeout_event)] = scrape_timer

            for future in as_completed(futures):
                # cancel unused timers for scrapes finished regularly (within set duration)
                futures[future].cancel()
                yield from future.result()
            
        # in case collection finished without timeouts, cancel the overall scrape duration timer
        total_scrape_timer.cancel()


    def collect(self):
        if not self._valid_collect_interval():
            return

        # bandwidth collector
        yield from self.collector_registry.bandwidthCollector.collect()

        # all other collectors
        # Check whether to run in parallel by looking at the mktxp system configuration
        parallel = config_handler.system_entry.fetch_routers_in_parallel
        max_worker_threads = config_handler.system_entry.max_worker_threads
        if parallel:
            yield from self.collect_async(max_worker_threads=max_worker_threads)
        else:
            yield from self.collect_sync()


    def _valid_collect_interval(self):
        now = datetime.now().timestamp()
        diff = now - self.last_collect_timestamp
        if diff < config_handler.system_entry.minimal_collect_interval:
            if config_handler.system_entry.verbose_mode:
                print(f'An attemp to collect metrics within minimal metrics collection interval: {diff} < {config_handler.system_entry.minimal_collect_interval}')
                print('deferring..')
            return False

        self.last_collect_timestamp = now       
        return True








