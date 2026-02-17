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


from mktxp.collector.base_collector import BaseCollector
from mktxp.flow.processor.output import BaseOutputProcessor
from mktxp.datasource.bfd_ds import BFDMetricsDataSource


class BFDCollector(BaseCollector):
    """
    Bidirectional Forwarding Detection (BFD) collector
    """
    @staticmethod
    def collect(router_entry):
        if not router_entry.config_entry.bfd:
            return

        translation_table = {
            "actual_tx_interval": lambda value: BaseOutputProcessor.parse_timedelta_milliseconds(value, ms_span=True) if value else "0",
            "desired_tx_interval": lambda value: BaseOutputProcessor.parse_timedelta_milliseconds(value, ms_span=True) if value else "0",
            "hold_time": lambda value: BaseOutputProcessor.parse_timedelta_milliseconds(value, ms_span=True) if value else "0",
            "up": lambda value: "1" if value == "true" else "0",
            "uptime": lambda value: BaseOutputProcessor.parse_timedelta_milliseconds(value) if value else "0",
        }

        default_labels = ["local_address", "remote_address"]
        metric_records = BFDMetricsDataSource.metric_records(
            router_entry,
            translation_table=translation_table,
        )

        if not metric_records:
            return

        yield BaseCollector.gauge_collector(
            "bfd_multiplier",
            "The multiplier",
            metric_records,
            metric_key="multiplier",
            metric_labels=default_labels
        )
        yield BaseCollector.gauge_collector(
            "bfd_hold_time",
            "The hold time in milliseconds",
            metric_records,
            metric_key="hold_time",
            metric_labels=default_labels
        )
        yield BaseCollector.counter_collector(
            "bfd_rx_packet",
            "BFD control packets received",
            metric_records,
            metric_key="packets_rx",
            metric_labels=default_labels,
        )
        yield BaseCollector.counter_collector(
            "bfd_state_change",
            "Number of time the state changed",
            metric_records,
            metric_key="state_changes",
            metric_labels=default_labels,
        )
        yield BaseCollector.gauge_collector(
            "bfd_tx_interval",
            "The actual transmit interval",
            metric_records,
            metric_key="actual_tx_interval",
            metric_labels=default_labels
        )
        yield BaseCollector.gauge_collector(
            "bfd_tx_interval_desired",
            "Desired transmit interval is the highes value from local tx interval and remote minimum rx interval",
            metric_records,
            metric_key="desired_tx_interval",
            metric_labels=default_labels
        )
        yield BaseCollector.counter_collector(
            "bfd_tx_packet",
            "BFD control packets transmitted",
            metric_records,
            metric_key="packets_tx",
            metric_labels=default_labels,
        )
        yield BaseCollector.gauge_collector(
            "bfd_up",
            "BFD is up",
            metric_records,
            metric_key="up",
            metric_labels=default_labels
        )
        yield BaseCollector.gauge_collector(
            "bfd_uptime",
            "BFD uptime in milliseconds",
            metric_records,
            metric_key="uptime",
            metric_labels=default_labels
        )
