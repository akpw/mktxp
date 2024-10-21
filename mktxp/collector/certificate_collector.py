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
from mktxp.datasource.certificate_ds import CertificateMetricsDataSource
from datetime import datetime

class CertificateCollector(BaseCollector):
    '''Certificate collector'''
    @staticmethod
    def collect(router_entry):
        if not router_entry.config_entry.certificate:
            return

        certificate_labels = ['name', 'digest_algorithm', 'key_type', 'country', 'state', 'locality', 'organization', 
                                'common_name', 'key_size', 'subject_alt_name', 'days_valid', 'trusted', 'key_usage', 
                                'ca', 'serial_number', 'key_usage', 'ca', 'serial_number', 'fingerprint', 'akid', 'skid', 
                                'invalid_before', 'invalid_after', 'expires-after']

        translation_table = {
        }

        certificate_records = CertificateMetricsDataSource.metric_records(router_entry, translation_table=translation_table, metric_labels = certificate_labels)   
        if isinstance(certificate_records, list): 
            for record in certificate_records:
                # Convert invalid_after time to epoch time
                record['invalid_after_epoch'] = int(datetime.strptime(record['invalid_after'], "%Y-%m-%d %H:%M:%S").timestamp())
        if certificate_records:
            yield BaseCollector.gauge_collector('certificate_expiration_timestamp_seconds', 'The number of seconds before expiration time the certificate should renew.', certificate_records, 'invalid_after_epoch', certificate_labels)
