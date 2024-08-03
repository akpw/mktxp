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
from mktxp.datasource.ipsec_ds import IPSecMetricsDataSource


class IPSecCollector(BaseCollector):
    '''IPSec collector'''

    @staticmethod
    def collect(router_entry):
        if not router_entry.config_entry.ipsec:
            return

        ipsec_labels = ['local_address', 'remote_address', 'name', 'last_seen', 'uptime', 'ph2_total', 'responder',
                        'natt_peer', 'rx_bytes', 'rx_packets', 'tx_bytes', 'tx_packets', 'state']
        translation_table = {
            'responder': lambda value: '1' if value == 'true' else '0',
            'natt_peer': lambda value: '1' if value == 'true' else '0',
            'last_seen': lambda value: BaseOutputProcessor.parse_timedelta_milliseconds(value) if value else '0',
            'uptime': lambda value: BaseOutputProcessor.parse_timedelta_milliseconds(value) if value else '0'
        }
        ipsec_records = IPSecMetricsDataSource.metric_records(router_entry, metric_labels=ipsec_labels,
                                                              translation_table=translation_table)

        if ipsec_records:
            ipsec_info_labels = ['local_address', 'name', 'remote_address', 'state']
            yield BaseCollector.info_collector('ipsec_peer_state',
                                               'State of negotiation with the peer.',
                                               ipsec_records, ipsec_info_labels)

            ipsec_value_labels = ['local_address', 'name', 'remote_address']
            yield BaseCollector.counter_collector('ipsec_peer_rx_byte',
                                                  'The total amount of bytes received from this peer.',
                                                  ipsec_records, 'rx_bytes', ipsec_value_labels)

            yield BaseCollector.counter_collector('ipsec_peer_tx_byte',
                                                  'The total amount of bytes transmitted to this peer.',
                                                  ipsec_records, 'tx_bytes', ipsec_value_labels)

            yield BaseCollector.counter_collector('ipsec_peer_rx_packet',
                                                  'The total amount of packets received from this peer.',
                                                  ipsec_records, 'rx_packets', ipsec_value_labels)

            yield BaseCollector.counter_collector('ipsec_peer_tx_packet',
                                                  'The total amount of packets transmitted to this peer.',
                                                  ipsec_records, 'tx_packets', ipsec_value_labels)

            yield BaseCollector.gauge_collector('ipsec_peer_security_association',
                                                'The total amount of active IPsec security associations.',
                                                ipsec_records, 'ph2_total', ipsec_value_labels)

            yield BaseCollector.gauge_collector('ipsec_peer_last_seen',
                                                'Duration since the last message received by this peer.',
                                                ipsec_records, 'last_seen', ipsec_value_labels)

            yield BaseCollector.gauge_collector('ipsec_peer_uptime',
                                                'How long peer is in an established state.',
                                                ipsec_records, 'uptime', ipsec_value_labels)

            yield BaseCollector.gauge_collector('ipsec_peer_responder',
                                                'Whether the connection is initiated by a remote peer.',
                                                ipsec_records, 'responder', ipsec_value_labels)

            yield BaseCollector.gauge_collector('ipsec_peer_natt_enabled',
                                                'Whether NAT-T is used for this peer.',
                                                ipsec_records, 'natt_peer', ipsec_value_labels)
