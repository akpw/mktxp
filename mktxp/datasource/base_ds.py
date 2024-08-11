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
                for key, value in router_entry.router_id.items():
                    translated_record[key] = value
            
            # translate fields if needed
            for key, func in translation_table.items():
                if translate_if_no_value or translated_record.get(key) is not None:
                    translated_record[key] = func(translated_record.get(key))
            labeled_records.append(translated_record)            
        return labeled_records


    @staticmethod
    def _normalise_keys(key):
        chars = ".-"
        for chr in chars:
            if chr in key:
                key = key.replace(chr, "_")     
        return key

