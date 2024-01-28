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


from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, InfoMetricFamily
from mktxp.cli.config.config import MKTXPConfigKeys
     

class BaseCollector:
    ''' Base Collector methods
        For use by custom collector
    '''
    @staticmethod
    def info_collector(name, decription, router_records, metric_labels=None):
        if metric_labels is None:
            metric_labels = []
        BaseCollector._add_id_labels(metric_labels)
        collector = InfoMetricFamily(f'mktxp_{name}', decription)

        for router_record in router_records:
            label_values = {label: router_record.get(label) if router_record.get(label) else '' for label in metric_labels}
            collector.add_metric(metric_labels, label_values)
        return collector

    @staticmethod
    def counter_collector(name, decription, router_records, metric_key, metric_labels=None):
        if metric_labels is None:
            metric_labels = []
        BaseCollector._add_id_labels(metric_labels)
        collector = CounterMetricFamily(f'mktxp_{name}', decription, labels=metric_labels)

        for router_record in router_records:
            label_values = [router_record.get(label) if router_record.get(label) else '' for label in metric_labels]

            val = router_record.get(metric_key)
            if val is None:
                continue

            collector.add_metric(label_values, val)
        return collector

    @staticmethod
    def gauge_collector(name, decription, router_records, metric_key, metric_labels = None, add_id_labels = True):
        if metric_labels is None:
            metric_labels = []
        if add_id_labels:
            BaseCollector._add_id_labels(metric_labels)
        collector = GaugeMetricFamily(f'mktxp_{name}', decription, labels=metric_labels)

        for router_record in router_records:
            val = router_record.get(metric_key)
            if val is None:
                continue

            label_values = [router_record.get(label) if router_record.get(label) else '' for label in metric_labels]
            collector.add_metric(label_values, val)
        return collector


    # Helpers
    @staticmethod
    def _add_id_labels(metric_labels):
        metric_labels.append(MKTXPConfigKeys.ROUTERBOARD_NAME)
        metric_labels.append(MKTXPConfigKeys.ROUTERBOARD_ADDRESS)
