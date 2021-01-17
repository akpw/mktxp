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


import speedtest
from datetime import datetime
from multiprocessing import Pool
from prometheus_client import Gauge
from mktxp.cli.config.config import config_handler

result_list = [{'download': 0, 'upload': 0, 'ping': 0}]
def get_result(bandwidth_dict):
    result_list.append(bandwidth_dict)

class MKTXPCollector:
    ''' MKTXP collector
    '''    
    def __init__(self):
        self.pool = Pool()
        self.last_call_timestamp = 0        
        self.gauge_bandwidth = Gauge('mktxp_internet_bandwidth', 'Internet bandwidth in bits per second', ['direction'])
        self.gauge_latency = Gauge('mktxp_internet_latency', 'Internet bandwidth latency in milliseconds')
    
    def collect(self):
        if result_list:                        
            bandwidth_dict = result_list.pop(0)
            self.gauge_bandwidth.labels('download').set(bandwidth_dict["download"])
            self.gauge_bandwidth.labels('upload').set(bandwidth_dict["upload"])
            self.gauge_latency.set(bandwidth_dict["ping"])

        ts =  datetime.now().timestamp()       
        if (ts - self.last_call_timestamp) > config_handler._entry().bandwidth_test_interval:            
            self.pool.apply_async(MKTXPCollector.bandwidth_worker, callback=get_result)            
            self.last_call_timestamp = ts

    def __del__(self):
        self.pool.close()
        self.pool.join()        

    @staticmethod
    def bandwidth_worker():
        bandwidth_test = speedtest.Speedtest()
        bandwidth_test.get_best_server()
        bandwidth_test.download()
        bandwidth_test.upload()
        return bandwidth_test.results.dict()

