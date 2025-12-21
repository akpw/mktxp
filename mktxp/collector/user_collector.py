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

from datetime import datetime
from mktxp.collector.base_collector import BaseCollector
from mktxp.datasource.user_ds import UserMetricsDataSource

class UserCollector(BaseCollector):
    '''Active Users collector'''
    @staticmethod
    def collect(router_entry):
        if not router_entry.config_entry.user:
            return

        user_labels = ['name', 'when', 'address', 'via', 'group']
        user_records = UserMetricsDataSource.metric_records(router_entry, metric_labels=user_labels)        
        
        if user_records:
            for record in user_records:
                if 'when' in record:
                    try:
                        dt = datetime.strptime(record['when'], "%Y-%m-%d %H:%M:%S")
                        record['when'] = int(dt.timestamp())
                    except ValueError:
                        # Use current timestamp as fallback if parsing fails
                        record['when'] = int(datetime.now().timestamp())        
            
            user_labels.remove('when')

            # Auto de-duplicate the records from the scrapes via API silently            
            user_metrics = BaseCollector.gauge_collector('active_users_info', 'Active Users', user_records, 'when', user_labels, verbose_reporting = False)
            yield user_metrics
