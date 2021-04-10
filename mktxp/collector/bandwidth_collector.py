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


import socket
import speedtest
from datetime import datetime
from multiprocessing import Pool
from mktxp.cli.config.config import config_handler
from mktxp.collector.base_collector import BaseCollector


result_list = [{'download': 0, 'upload': 0, 'ping': 0}]
def get_result(bandwidth_dict):
    result_list[0] = bandwidth_dict


class BandwidthCollector(BaseCollector):
    ''' MKTXP collector
    '''    
    def __init__(self):
        self.pool = Pool()
        self.last_call_timestamp = 0        
    
    def collect(self):
        if not config_handler.system_entry().bandwidth:
            return

        if result_list:      
            result_dict = result_list[0]
            bandwidth_records = [{'direction': key, 'bandwidth': str(result_dict[key])} for key in ('download', 'upload')]     
            bandwidth_metrics = BaseCollector.gauge_collector('internet_bandwidth', 'Internet bandwidth in bits per second', 
                                                                            bandwidth_records, 'bandwidth', ['direction'], add_id_labels = False)
            yield bandwidth_metrics

            latency_records = [{'latency': str(result_dict['ping'])}]
            latency_metrics = BaseCollector.gauge_collector('internet_latency', 'Internet latency in milliseconds', 
                                                                            latency_records, 'latency', [], add_id_labels = False)
            yield latency_metrics

        ts =  datetime.now().timestamp()       
        if (ts - self.last_call_timestamp) > config_handler.system_entry().bandwidth_test_interval:
            self.pool.apply_async(BandwidthCollector.bandwidth_worker, callback=get_result)            
            self.last_call_timestamp = ts

    def __del__(self):
        self.pool.close()
        self.pool.join()        

    @staticmethod
    def bandwidth_worker():
        if BandwidthCollector.inet_connected():
            bandwidth_test = speedtest.Speedtest()
            bandwidth_test.get_best_server()
            bandwidth_test.download()
            bandwidth_test.upload()
            return bandwidth_test.results.dict()
        else:
            return {'download': 0, 'upload': 0, 'ping': 0}

    @staticmethod
    def inet_connected(host="8.8.8.8", port=53, timeout=3):
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except socket.error as exc:
            return False

