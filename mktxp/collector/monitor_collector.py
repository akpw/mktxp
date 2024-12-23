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
    """ Ethernet Interface Monitor Metrics collector
    """
    @staticmethod
    def collect(router_entry):
        if not router_entry.config_entry.monitor:
            return

        monitor_labels = [
            'full_duplex',
            'name',
            'rate',
            'sfp_connector_type',
            'sfp_manufacturing_date',
            'sfp_module_present',
            'sfp_rx_loss',
            'sfp_rx_power',
            'sfp_supply_voltage',
            'sfp_temperature',
            'sfp_tx_bias_current',
            'sfp_tx_fault',
            'sfp_tx_power',
            'sfp_type',
            'sfp_vendor_name',
            'sfp_vendor_part_number',
            'sfp_vendor_revision',
            'sfp_vendor_serial',
            'sfp_wavelength',
            'status',
        ]

        translation_table = {
            'full_duplex': lambda value: '1' if value == 'true' else '0',
            'name': lambda value: value if value else '',
            'rate': lambda value: MonitorCollector._rates(value) if value else '0',
            'sfp_module_present': lambda value: '1' if value == 'true' else '0',
            'sfp_rx_loss': lambda value: '1' if value == 'true' else '0',
            'sfp_temperature': lambda value: value if value else '0',
            'sfp_tx_bias_current': lambda value: float(value) / 1000 if value else '0',
            'sfp_tx_fault': lambda value: '1' if value == 'true' else '0',
            'status': lambda value: '1' if value == 'link-ok' else '0',
        }
        monitor_records = InterfaceMonitorMetricsDataSource.metric_records(
            router_entry,
            metric_labels=monitor_labels,
            translation_table=translation_table,
            include_comments=True
        )

        if not monitor_records:
            return

        yield BaseCollector.gauge_collector(
            'interface_status',
            'Current interface link status',
            monitor_records,
            'status',
            ['name']
        )

        # limit records according to the relevant metrics
        rate_records = [monitor_record for monitor_record in monitor_records if monitor_record.get('rate', None)]
        yield BaseCollector.gauge_collector(
            'interface_rate',
            'Actual interface connection data rate',
            rate_records,
            'rate',
            ['name']
        )

        full_duplex_records = [monitor_record for monitor_record in monitor_records if monitor_record.get('full_duplex', None)]
        yield BaseCollector.gauge_collector(
            'interface_full_duplex',
            'Full duplex data transmission',
            full_duplex_records,
            'full_duplex',
            ['name']
        )

        sfp_metrics = [record for record in monitor_records if int(record.get("sfp_module_present"))]
        if sfp_metrics:
            yield BaseCollector.info_collector(
                'interface_sfp',
                'Information about the used transceiver',
                sfp_metrics,
                metric_labels=[
                    'name',
                    'sfp_connector_type',
                    'sfp_manufacturing_date',
                    'sfp_type',
                    'sfp_vendor_name',
                    'sfp_vendor_part_number',
                    'sfp_vendor_revision',
                    'sfp_vendor_serial',
                ]
            )
            yield BaseCollector.gauge_collector(
                'interface_sfp_supply_voltage',
                'The transceivers current supply voltage',
                sfp_metrics,
                metric_key='sfp_supply_voltage',
                metric_labels=['name']
            )
            yield BaseCollector.gauge_collector(
                'interface_sfp_rx_loss',
                'The receiver signal is lost',
                sfp_metrics,
                metric_key='sfp_rx_loss',
                metric_labels=['name']
            )
            yield BaseCollector.gauge_collector(
                'interface_sfp_rx_power',
                'Current SFP RX Power',
                sfp_metrics,
                metric_key='sfp_rx_power',
                metric_labels=['name']
            )
            yield BaseCollector.gauge_collector(
                'interface_sfp_temperature',
                'Current SFP Temperature',
                sfp_metrics,
                metric_key='sfp_temperature',
                metric_labels=['name']
            )
            yield BaseCollector.gauge_collector(
                'interface_sfp_tx_bias_current',
                'The transceivers current tx bias current',
                sfp_metrics,
                metric_key='sfp_tx_bias_current',
                metric_labels=['name']
            )
            yield BaseCollector.gauge_collector(
                'interface_sfp_tx_power',
                'Current SFP TX Power',
                sfp_metrics,
                metric_key='sfp_tx_power',
                metric_labels=['name']
            )
            yield BaseCollector.gauge_collector(
                'interface_sfp_tx_fault',
                'The transceiver transmitter is in fault state',
                sfp_metrics,
                metric_key='sfp_tx_fault',
                metric_labels=['name']
            )
            yield BaseCollector.gauge_collector(
                'interface_sfp_wavelength',
                'Current SFP Wavelength',
                sfp_metrics,
                metric_key='sfp_wavelength',
                metric_labels=['name']
            )

    @staticmethod
    def _rates(rate_option):
        # according mikrotik docs, an interface rate should be one of these
        rate_value = {
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
