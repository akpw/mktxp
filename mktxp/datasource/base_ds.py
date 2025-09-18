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

from mktxp.cli.config.config import MKTXPConfigKeys
from mktxp.cli.config.config import config_handler

class BaseDSProcessor:
    ''' Base Metrics DataSource processing
    '''             

    @staticmethod
    def trimmed_records(router_entry, *, router_records = None, metric_labels = None, add_router_id = True, translation_table = None, translate_if_no_value = True):
        metric_labels = metric_labels or []
        router_records = router_records or []            
        translation_table = translation_table or {}         

        if len(metric_labels) == 0 and len(router_records) > 0:
            metric_labels = [BaseDSProcessor._normalise_keys(key) for key in router_records[0].keys()]
        metric_labels = set(metric_labels)      

        labeled_records = []
        for router_record in router_records:
            translated_record = {BaseDSProcessor._normalise_keys(key): value for (key, value) in router_record.items() if BaseDSProcessor._normalise_keys(key) in metric_labels}

            if add_router_id:
                translated_record.update(router_entry.router_id)
            
            if router_entry.config_entry.custom_labels:
                custom_labels = BaseDSProcessor._parse_custom_labels(router_entry.config_entry.custom_labels, router_entry)
                if custom_labels:
                    translated_record[MKTXPConfigKeys.CUSTOM_LABELS_METADATA_ID] = custom_labels

            # translate fields if needed
            for key, func in translation_table.items():
                if translate_if_no_value or translated_record.get(key) is not None:
                    translated_record[key] = func(translated_record.get(key))
            labeled_records.append(translated_record)            
        return labeled_records

    @staticmethod
    def count_records(router_entry, *, api_path, api_query=None):
        api_query = api_query or {}
        try:
            resource = router_entry.api_connection.router_api().get_resource(api_path)
            response = resource.call('print', {'count-only': ''}, api_query).done_message
            if response:
                return int(response.get('ret', 0))
            return 0
        except Exception as exc:
            print(f'Error getting record count for {api_path} from router {router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None

    @staticmethod
    def _normalise_keys(key):
        chars = ".-"
        for chr in chars:
            if chr in key:
                key = key.replace(chr, "_")     
        return key

    @staticmethod
    def _parse_custom_labels(custom_labels, router_entry):
        if not custom_labels or custom_labels == 'None':
            return {}

        labels_list = []
        if isinstance(custom_labels, str):
            labels_list = custom_labels.split(',')
        elif isinstance(custom_labels, (list, tuple)):
            labels_list = [str(item) for item in custom_labels]
        else:
            return {}

        labels_dict = {}
        for item in labels_list:
            try:
                if isinstance(item, str) and (':' in item or '=' in item):
                    key, value = item.split(':', 1) if ':' in item else item.split('=', 1)
                    labels_dict[key.strip()] = value.strip()
                else:
                    if config_handler.system_entry.verbose_mode:
                        print(f"Warning: Configuration for {router_entry.router_name} contains a malformed custom label '{item}'. It should be in 'key:value' or 'key=value' format. Ignoring.")
            except Exception as e:
                print(f"Warning: Could not parse custom label '{item} for {router_entry.router_name}'. Error: {e}. Ignoring.")
        return labels_dict        
