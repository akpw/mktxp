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
from mktxp.datasource.package_ds import PackageMetricsDataSource


class PackageCollector(BaseCollector):
    '''Installed Packages collector'''
    @staticmethod
    def collect(router_entry):
        if not router_entry.config_entry.installed_packages:
            return

        package_labels = ['name', 'version', 'build_time', 'disabled']
        package_records = PackageMetricsDataSource.metric_records(router_entry, metric_labels=package_labels)
        if package_records:
            package_metrics = BaseCollector.info_collector('installed_packages', 'Installed Packages', package_records, package_labels)
            yield package_metrics

