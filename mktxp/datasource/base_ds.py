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
    def trimmed_records(router_entry, *, router_records = [], metric_labels = [], add_router_id = True, translation_table = {}):
        dash2_ = lambda x : x.replace('-', '_')
        if len(metric_labels) == 0 and len(router_records) > 0:
            metric_labels = [dash2_(key) for key in router_records[0].keys()]
        metric_labels = set(metric_labels)      

        labeled_records = []
        for router_record in router_records:
            translated_record = {dash2_(key): value for (key, value) in router_record.items() if dash2_(key) in metric_labels}

            if add_router_id:
                for key, value in router_entry.router_id.items():
                    translated_record[key] = value
            
            # translate fields if needed
            for key, func in translation_table.items():
                translated_record[key] = func(translated_record.get(key))
            labeled_records.append(translated_record)
            
        return labeled_records
