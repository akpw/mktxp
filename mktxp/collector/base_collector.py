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

import itertools
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, InfoMetricFamily
from mktxp.cli.config.config import MKTXPConfigKeys, config_handler

class BaseCollector:
    """ Base Collector methods
        For use by custom collector
    """
    @staticmethod
    def _smart_tee(router_records):
        # Check if it's already subscriptable (list/tuple)
        if hasattr(router_records, '__getitem__'):
            # It's subscriptable - safe to use multiple times
            return router_records, router_records
        else:
            # It's not subscriptable - need to tee it
            return itertools.tee(router_records)

    @staticmethod
    def _de_duplicate_records(router_records, metric_labels, verbose_reporting = None):
        unique_records = {}
        if verbose_reporting is None:
            verbose_reporting = config_handler.system_entry.verbose_mode

        for record in router_records:
            custom_labels_dict = record.get(MKTXPConfigKeys.CUSTOM_LABELS_METADATA_ID, {})
            label_values_tuple = tuple(record.get(label, custom_labels_dict.get(label, '')) for label in metric_labels)
            
            if label_values_tuple in unique_records:
                if verbose_reporting:
                    print(f"Warning: Duplicate metric record found for labels {dict(zip(metric_labels, label_values_tuple))}. Keeping last.")
            unique_records[label_values_tuple] = record
        return unique_records.values()

    @staticmethod
    def info_collector(name: str, documentation: str, router_records, metric_labels=None, add_id_labels = True, add_custom_labels=True, verbose_reporting=None):
        metric_labels = metric_labels or []
        router_records = router_records or []

        records_for_labels, records_for_processing = BaseCollector._smart_tee(router_records)

        if add_id_labels:
            metric_labels = BaseCollector._add_id_labels(metric_labels)
        if add_custom_labels:
            metric_labels = BaseCollector._add_custom_labels(metric_labels, records_for_labels)
        
        collector = InfoMetricFamily(f'mktxp_{name}', documentation=documentation, labels=metric_labels)

        deduplicated_records = BaseCollector._de_duplicate_records(records_for_processing, metric_labels, verbose_reporting)
        for router_record in deduplicated_records:
            label_values = {}
            custom_labels_dict = router_record.get(MKTXPConfigKeys.CUSTOM_LABELS_METADATA_ID, {})
            for label in metric_labels:
                value = router_record.get(label, custom_labels_dict.get(label, ''))
                label_values[label] = value
            collector.add_metric(metric_labels, label_values)
        return collector

    @staticmethod
    def counter_collector(name: str, documentation: str, router_records, metric_key, metric_labels=None, add_id_labels = True, add_custom_labels=True, verbose_reporting=None):
        metric_labels = metric_labels or []
        router_records = router_records or []

        records_for_labels, records_for_processing = BaseCollector._smart_tee(router_records)

        if add_id_labels:
            metric_labels = BaseCollector._add_id_labels(metric_labels)
        if add_custom_labels:
            metric_labels = BaseCollector._add_custom_labels(metric_labels, records_for_labels, metric_key)

        collector = CounterMetricFamily(f'mktxp_{name}', documentation=documentation, labels=metric_labels)

        deduplicated_records = BaseCollector._de_duplicate_records(records_for_processing, metric_labels, verbose_reporting)
        for router_record in deduplicated_records:
            label_values = []
            custom_labels_dict = router_record.get(MKTXPConfigKeys.CUSTOM_LABELS_METADATA_ID, {})
            for label in metric_labels:
                value = router_record.get(label, custom_labels_dict.get(label, ''))
                label_values.append(value)
            collector.add_metric(label_values, router_record.get(metric_key, 0))
        return collector

    @staticmethod
    def gauge_collector(name: str, documentation: str, router_records, metric_key, metric_labels = None, add_id_labels = True, add_custom_labels = True, verbose_reporting=None):
        metric_labels = metric_labels or []
        router_records = router_records or []

        records_for_labels, records_for_processing = BaseCollector._smart_tee(router_records)

        if add_id_labels:
            metric_labels = BaseCollector._add_id_labels(metric_labels)
        if add_custom_labels:
            metric_labels = BaseCollector._add_custom_labels(metric_labels, records_for_labels, metric_key)

        collector = GaugeMetricFamily(f'mktxp_{name}', documentation=documentation, labels=metric_labels)

        deduplicated_records = BaseCollector._de_duplicate_records(records_for_processing, metric_labels, verbose_reporting)
        for router_record in deduplicated_records:
            label_values = []
            custom_labels_dict = router_record.get(MKTXPConfigKeys.CUSTOM_LABELS_METADATA_ID, {})
            for label in metric_labels:
                value = router_record.get(label, custom_labels_dict.get(label, ''))
                label_values.append(value)
            collector.add_metric(label_values, router_record.get(metric_key, 0))
        return collector

    # Helpers
    @staticmethod
    def _add_custom_labels(metric_labels, router_records, metric_key = None):
        try:
            first_record = next(iter(router_records), None)
        except TypeError:
            return list(metric_labels)

        if not first_record:
            return list(metric_labels)

        extended_labels = list(metric_labels)

        if MKTXPConfigKeys.CUSTOM_LABELS_METADATA_ID in first_record and isinstance(first_record.get(MKTXPConfigKeys.CUSTOM_LABELS_METADATA_ID), dict):
            for key in first_record[MKTXPConfigKeys.CUSTOM_LABELS_METADATA_ID].keys():
                if key not in extended_labels:
                    extended_labels.append(key)

        return extended_labels

    @staticmethod
    def _add_id_labels(metric_labels):
        extended_labels = list(metric_labels)

        if MKTXPConfigKeys.ROUTERBOARD_NAME not in extended_labels:
            extended_labels.append(MKTXPConfigKeys.ROUTERBOARD_NAME)
        if MKTXPConfigKeys.ROUTERBOARD_ADDRESS not in extended_labels:
            extended_labels.append(MKTXPConfigKeys.ROUTERBOARD_ADDRESS)

        return extended_labels