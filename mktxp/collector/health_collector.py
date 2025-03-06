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
from mktxp.datasource.health_ds import HealthMetricsDataSource
from mktxp.utils.utils import str2bool

class HealthCollector(BaseCollector):
    ''' System Health Metrics collector
    '''    
    @staticmethod
    def collect(router_entry):
        if not router_entry.config_entry.health:
            return

        health_labels = ['voltage', 'temperature', 'phy_temperature', 'cpu_temperature', 'switch_temperature', 
                        'fan1_speed', 'fan2_speed', 'fan3_speed', 'fan4_speed', 'power_consumption', ' board_temperature1', 'board_temperature2',
                        'psu1_voltage', 'psu2_voltage', 'psu1_current', 'psu2_current', 'psu1_state', 'psu2_state', 
                        'poe_out_consumption', 'jack_voltage', '2pin_voltage', 'poe_in_voltage']
        translation_table = {
                'psu1_state': lambda value: '1' if str2bool(value, default = False) else '0',
                'psu2_state': lambda value: '1' if str2bool(value, default = False) else '0'}
        health_records = HealthMetricsDataSource.metric_records(router_entry, metric_labels = health_labels, translation_table = translation_table)   
        if health_records:
            for record in health_records:

                if 'voltage' in record:
                    voltage_metrics = BaseCollector.gauge_collector('system_routerboard_voltage', 'Supplied routerboard voltage', [record, ], 'voltage')
                    yield voltage_metrics

                if 'temperature' in record:
                    temperature_metrics = BaseCollector.gauge_collector('system_routerboard_temperature', 'Routerboard current temperature', [record, ], 'temperature')
                    yield temperature_metrics

                if 'phy_temperature' in record:
                    phy_temperature_metrics = BaseCollector.gauge_collector('system_phy_temperature', 'Current PHY temperature', [record, ], 'phy_temperature')
                    yield phy_temperature_metrics

                if 'cpu_temperature' in record:
                    cpu_temperature_metrics = BaseCollector.gauge_collector('system_cpu_temperature', 'Current CPU temperature', [record, ], 'cpu_temperature')
                    yield cpu_temperature_metrics
                
                if 'switch_temperature' in record:
                    switch_temperature_metrics = BaseCollector.gauge_collector('system_switch_temperature', 'Current switch temperature', [record, ], 'switch_temperature')
                    yield switch_temperature_metrics

                if 'fan1_speed' in record:
                    fan_one_speed_metrics = BaseCollector.gauge_collector('system_fan_one_speed', 'System fan 1 current speed', [record, ], 'fan1_speed')
                    yield fan_one_speed_metrics

                if 'fan2_speed' in record:
                    fan_two_speed_metrics = BaseCollector.gauge_collector('system_fan_two_speed', 'System fan 2 current speed', [record, ], 'fan2_speed')
                    yield fan_two_speed_metrics

                if 'fan3_speed' in record:
                    fan_three_speed_metrics = BaseCollector.gauge_collector('system_fan_three_speed', 'System fan 3 current speed', [record, ], 'fan3_speed')
                    yield fan_three_speed_metrics

                if 'fan4_speed' in record:
                    fan_four_speed_metrics = BaseCollector.gauge_collector('system_fan_four_speed', 'System fan 4 current speed', [record, ], 'fan4_speed')
                    yield fan_four_speed_metrics

                if 'power_consumption' in record:
                    power_consumption_metrics = BaseCollector.gauge_collector('system_power_consumption', 'System Power Consumption', [record, ], 'power_consumption')
                    yield power_consumption_metrics

                if 'board_temperature1' in record:
                    board_temperature1_metrics = BaseCollector.gauge_collector('system_board_temperature1', 'System board temperature 1', [record, ], 'board_temperature1')
                    yield board_temperature1_metrics

                if 'board_temperature2' in record:
                    board_temperature2_metrics = BaseCollector.gauge_collector('system_board_temperature2', 'System board temperature 2', [record, ], 'board_temperature2')
                    yield board_temperature2_metrics

                if 'psu1_voltage' in record:
                    psu1_voltage_metrics = BaseCollector.gauge_collector('system_psu1_voltage', 'System PSU1 voltage', [record, ], 'psu1_voltage')
                    yield psu1_voltage_metrics

                if 'psu2_voltage' in record:
                    psu2_voltage_metrics = BaseCollector.gauge_collector('system_psu2_voltage', 'System PSU2 voltage', [record, ], 'psu2_voltage')
                    yield psu2_voltage_metrics

                if 'psu1_current' in record:
                    psu1_current_metrics = BaseCollector.gauge_collector('system_psu1_current', 'System PSU1 current', [record, ], 'psu1_current')
                    yield psu1_current_metrics

                if 'psu2_current' in record:
                    psu2_current_metrics = BaseCollector.gauge_collector('system_psu2_current', 'System PSU2 current', [record, ], 'psu2_current')
                    yield psu2_current_metrics

                if 'psu1_state' in record:
                    yield BaseCollector.gauge_collector('system_psu1_state', 'System PSU1 state', [record, ], 'psu1_state')

                if 'psu2_state' in record:
                    yield BaseCollector.gauge_collector('system_psu2_state', 'System PSU2 state', [record, ], 'psu2_state')

                if 'poe_out_consumption' in record:
                    poe_out_consumption_metrics = BaseCollector.gauge_collector('system_poe_out_consumption', 'System POE-out consumption', [record, ], 'poe_out_consumption')
                    yield poe_out_consumption_metrics

                if 'jack_voltage' in record:
                    jack_voltage_metrics = BaseCollector.gauge_collector('system_jack_voltage', 'System Jack Voltage', [record, ], 'jack_voltage')
                    yield jack_voltage_metrics

                if '2pin_voltage' in record:
                    pin_voltage_metrics = BaseCollector.gauge_collector('system_2pin_voltage', 'System 2pin Voltage', [record, ], '2pin_voltage')
                    yield pin_voltage_metrics

                if 'poe_in_voltage' in record:
                    poe_in_voltage_metrics = BaseCollector.gauge_collector('system_poe_in_voltage', 'System POE-in Voltage', [record, ], 'poe_in_voltage')
                    yield poe_in_voltage_metrics

