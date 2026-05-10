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
from mktxp.datasource.routerboard_ds import RouterboardMetricsDataSource


class RouterboardCollector(BaseCollector):
    """RouterBOARD inventory + firmware metrics collector"""

    @staticmethod
    def collect(router_entry):
        if not router_entry.config_entry.routerboard:
            return
        
        rb_labels = [
            "routerboard",
            "model",
            "serial_number",
            "firmware_type",
            "factory_firmware",
            "current_firmware",
            "upgrade_firmware",
        ]

        rb_records = RouterboardMetricsDataSource.metric_records(router_entry, metric_labels=rb_labels)
        if not rb_records:
            return

        yield BaseCollector.info_collector(
            "routerboard",
            "RouterBOARD inventory and firmware information",
            rb_records,
            rb_labels,
        )

        for r in rb_records:
            cur = r.get("current_firmware")
            upg = r.get("upgrade_firmware")
            r["firmware_upgrade_available"] = 1 if (cur and upg and cur != upg) else 0

        yield BaseCollector.gauge_collector(
            "routerboard_firmware_upgrade_available",
            "Whether RouterBOARD firmware upgrade is available (current_firmware != upgrade_firmware)",
            rb_records,
            "firmware_upgrade_available",
            ["current_firmware", "upgrade_firmware"],
        )