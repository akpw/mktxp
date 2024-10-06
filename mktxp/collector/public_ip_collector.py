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
from mktxp.datasource.public_ip_ds import PublicIPAddressDatasource


class PublicIPAddressCollector(BaseCollector):
    '''Public IP address collector'''
    @staticmethod
    def collect(router_entry):
        if not router_entry.config_entry.public_ip:
            return

        address_labels = ['public_address', 'public_address_ipv6', 'dns_name']
        address_records = PublicIPAddressDatasource.metric_records(router_entry, metric_labels=address_labels)

        if address_records:
            for address_record in address_records:
                if not 'dns_name' in address_record:
                    address_record['dns_name'] = 'ddns disabled'

            address_metrics = BaseCollector.info_collector('public_ip_address', 'Public IP address', address_records, address_labels)
            yield address_metrics
