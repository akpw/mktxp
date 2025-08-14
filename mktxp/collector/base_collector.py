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
from mktxp.cli.config.config import MKTXPConfigKeys, config_handler

class BaseCollector:
    """ Base Collector methods
        For use by custom collector
    """
    @staticmethod
    def _de_duplicate_records(router_records, metric_labels, verbose_reporting = None):
        unique_records = {}
        if verbose_reporting is None:
            verbose_reporting = config_handler.system_entry.verbose_mode

        for record in router_records:
            label_values = tuple(record.get(label, '') for label in metric_labels)
            if label_values in unique_records:
                if verbose_reporting: 
                    print(f"Warning: Duplicate metric record found for labels {dict(zip(metric_labels, label_values))}. Keeping last.")
            unique_records[label_values] = record
        return unique_records.values()

    @staticmethod
    def info_collector(name: str, documentation: str, router_records, metric_labels=None, verbose_reporting=None):
        metric_labels = metric_labels or []
        router_records = router_records or []

        BaseCollector._add_id_labels(metric_labels)
        collector = InfoMetricFamily(f'mktxp_{name}', documentation=documentation)

        deduplicated_records = BaseCollector._de_duplicate_records(router_records, metric_labels, verbose_reporting)
        for router_record in deduplicated_records:
            label_values = {label: router_record.get(label) if router_record.get(label) else '' for label in metric_labels}
            collector.add_metric(metric_labels, label_values)
        return collector

    @staticmethod
    def counter_collector(name: str, documentation: str, router_records, metric_key, metric_labels=None, verbose_reporting=None):
        metric_labels = metric_labels or []
        router_records = router_records or []            

        BaseCollector._add_id_labels(metric_labels)
        collector = CounterMetricFamily(f'mktxp_{name}', documentation=documentation, labels=metric_labels)

        deduplicated_records = BaseCollector._de_duplicate_records(router_records, metric_labels, verbose_reporting)
        for router_record in deduplicated_records:
            label_values = [router_record.get(label) if router_record.get(label) else '' for label in metric_labels]
            collector.add_metric(label_values, router_record.get(metric_key, 0))
        return collector

    @staticmethod
    def gauge_collector(name: str, documentation: str, router_records, metric_key, metric_labels = None, add_id_labels = True, verbose_reporting=None):
        metric_labels = metric_labels or []
        router_records = router_records or []            

        if add_id_labels:
            BaseCollector._add_id_labels(metric_labels)
        collector = GaugeMetricFamily(f'mktxp_{name}', documentation=documentation, labels=metric_labels)

        deduplicated_records = BaseCollector._de_duplicate_records(router_records, metric_labels, verbose_reporting)
        for router_record in deduplicated_records:       
            label_values = [router_record.get(label) if router_record.get(label) else '' for label in metric_labels]        
            collector.add_metric(label_values, router_record.get(metric_key, 0))
        return collector

    # Helpers
    @staticmethod
    def _add_id_labels(metric_labels):
        if MKTXPConfigKeys.ROUTERBOARD_NAME not in metric_labels:
            metric_labels.append(MKTXPConfigKeys.ROUTERBOARD_NAME)
        if MKTXPConfigKeys.ROUTERBOARD_ADDRESS not in metric_labels:
            metric_labels.append(MKTXPConfigKeys.ROUTERBOARD_ADDRESS)
