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


from mktxp.datasource.base_ds import BaseDSProcessor


class MKTXPMetricsDataSource:
    ''' MKTXP Metrics data provider
    '''             
    @staticmethod
    def metric_records(router_entry):
        mktxp_records = []
        for key in router_entry.time_spent.keys():
            mktxp_records.append({'name': key, 'duration': router_entry.time_spent[key]})           

        # translation rules            
        translation_table = {'duration': lambda d: d*1000}
        return BaseDSProcessor.trimmed_records(router_entry, router_records = mktxp_records, translation_table = translation_table)
