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
from mktxp.flow.processor.output import BaseOutputProcessor
from mktxp.datasource.interface_ds import InterfaceMonitorMetricsDataSource


class MonitorCollector(BaseCollector):
    ''' Ethernet Interface Monitor Metrics collector
    '''    
    @staticmethod
    def collect(router_entry):
        if not router_entry.config_entry.monitor:
            return

        monitor_labels = ['status', 'rate', 'full_duplex', 'name', 'sfp_module_present', 'sfp_temperature', 'sfp_wavelength', 'sfp_tx_power', 'sfp_rx_power']
        monitor_records = InterfaceMonitorMetricsDataSource.metric_records(router_entry, metric_labels = monitor_labels, include_comments = True)   
        if monitor_records:
            # translate records to appropriate values
            for monitor_record in monitor_records:
                for monitor_label in monitor_labels:
                    value = monitor_record.get(monitor_label, None)    
                    if value:            
                        monitor_record[monitor_label] = MonitorCollector._translated_values(monitor_label, value)

            yield BaseCollector.gauge_collector('interface_status', 'Current interface link status', monitor_records, 'status', ['name'])

            # limit records according to the relevant metrics
            rate_records = [monitor_record for monitor_record in monitor_records if monitor_record.get('rate', None)]
            yield BaseCollector.gauge_collector('interface_rate', 'Actual interface connection data rate', rate_records, 'rate', ['name'])

            full_duplex_records = [monitor_record for monitor_record in monitor_records if monitor_record.get('full_duplex', None)]
            yield BaseCollector.gauge_collector('interface_full_duplex', 'Full duplex data transmission', full_duplex_records, 'full_duplex', ['name'])

            sfp_metrics = [record for record in monitor_records if record.get("sfp_module_present", False) == "1"]
            yield BaseCollector.gauge_collector('interface_sfp_temperature', 'Current SFP temperature', sfp_metrics, 'sfp_temperature', ['name'])
            yield BaseCollector.gauge_collector('interface_sfp_wavelength', 'Current SFP wavelength',sfp_metrics, 'sfp_wavelength', ['name'])
            yield BaseCollector.gauge_collector('interface_sfp_tx_power', 'Current TX power', sfp_metrics, 'sfp_tx_power', ['name'])
            yield BaseCollector.gauge_collector('interface_sfp_rx_power', 'Current TX power', sfp_metrics, 'sfp_rx_power', ['name'])

    # Helpers
    @staticmethod
    def _translated_values(monitor_label, value):
        try:
            return {
                    'status': lambda value: '1' if value=='link-ok' else '0',
                    'rate': lambda value: MonitorCollector._rates(value),
                    'full_duplex': lambda value: '1' if value=='true' else '0',
                    'sfp_module_present': lambda value: '1' if value=='true' else '0',
                    }[monitor_label](value)
        except KeyError:
            # default to just returning the value
            return value

    @staticmethod
    def _rates(rate_option):
        # according mikrotik docs, an interface rate should be one of these
        rate_value =  {
                '10Mbps': '10',
                '100Mbps': '100',
                '1Gbps': '1000',
                '2.5Gbps': '2500',
                '5Gbps': '5000',
                '10Gbps': '10000',
                '40Gbps': '40000'
                }.get(rate_option, None)
        if rate_value:
            return rate_value
        
        # ...or just calculate in case it's not
        return BaseOutputProcessor.parse_interface_rate(rate_option)




