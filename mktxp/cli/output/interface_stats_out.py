# coding=utf8
## Copyright (c) 2024 Arseniy Kuznetsov
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


from mktxp.flow.processor.output import BaseOutputProcessor
from mktxp.datasource.interface_ds import InterfaceMonitorMetricsDataSource


class InterfaceStatsOutput:
    ''' Interface Stats Output
    '''
    @staticmethod
    def clients_summary(router_entry):
        monitor_labels = ['status', 'rate', 'full_duplex', 'name', 'sfp_temperature', 'sfp_module_present', 'sfp_wavelength', 'sfp_tx_power', 'sfp_rx_power', 'sfp_supply_voltage', 'sfp_tx_bias_current', 'sfp_rx_loss', 'sfp_tx_fault']
        monitor_records = InterfaceMonitorMetricsDataSource.metric_records(router_entry, metric_labels = monitor_labels, add_router_id = False, running_only = not router_entry.config_entry.monitor_sfp_unplugged)
        if not monitor_records:
            print('No monitor stats records')
            return

        output_records_cnt = 0
        output_entry = BaseOutputProcessor.OutputInterfaceStatsEntry
        output_table = BaseOutputProcessor.output_table(output_entry)

        for record in monitor_records:
            output_table.add_row(output_entry(**record))
            output_table.add_row(output_entry())
            output_records_cnt += 1

        print (output_table.draw())

        print(f'Total interfaces: {output_records_cnt}')

