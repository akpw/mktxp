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

from humanize import naturaldelta
from mktxp.datasource.dhcp_ds import DHCPMetricsDataSource
from mktxp.utils.units import (
    parse_bitrates,
    parse_timedelta_seconds,
    parse_signal_strength,
    parse_uptime_seconds,
    parse_rate_bps,
)


def format_interface_name(name, comment, interface_name_format, max_length=20):
    """Formats interface/resource name based on interface_name_format configuration.

    Args:
        name: The base name (e.g., 'ether1', '10.0.0.1', MAC address)
        comment: Optional comment/description
        interface_name_format: One of 'name', 'comment', 'combined'
        max_length: Maximum length for truncation

    Returns:
        Formatted name string
    """
    if not name:
        name = ''
    if not comment:
        comment = ''

    if max_length and comment and isinstance(comment, (str, list, tuple, bytes)):
        comment = comment[0:max_length]

    if interface_name_format == 'name':
        return name
    elif interface_name_format == 'comment':
        return comment if comment else name
    elif interface_name_format == 'combined':
        return f'{name} ({comment})' if comment else name
    else:
        print(
            f'Warning: Invalid interface_name_format "{interface_name_format}". Using "name" format.'
        )
        return name


def dhcp_name(router_entry, dhcp_lease_record, drop_comment=False):
    """Derives a human-friendly DHCP name from hostname, comment, or MAC address."""
    name = dhcp_lease_record.get('host_name')
    comment = dhcp_lease_record.get('comment')

    if not name:
        name = dhcp_lease_record.get('mac_address', '')

    formatted_name = format_interface_name(
        name, comment, router_entry.config_entry.interface_name_format
    )

    if drop_comment and 'comment' in dhcp_lease_record:
        del dhcp_lease_record['comment']

    return formatted_name if formatted_name else ''


def resolve_dhcp(
    router_entry,
    registration_record,
    id_key='mac_address',
    resolve_address=True,
):
    """Enriches a registration record with DHCP hostname and leased IP address."""
    if not router_entry.dhcp_records:
        DHCPMetricsDataSource.metric_records(router_entry)
    name = registration_record.get(id_key)
    dhcp_address = 'No DHCP Record'

    dhcp_lease_record = router_entry.dhcp_record(name)
    if dhcp_lease_record:
        name = dhcp_name(router_entry, dhcp_lease_record)
        dhcp_address = dhcp_lease_record.get('address', '')

    registration_record['dhcp_name'] = name
    if resolve_address:
        registration_record['dhcp_address'] = dhcp_address


def add_registration_gauges(registration_record):
    """Adds numeric uptime_seconds / tx_rate_bps / rx_rate_bps keys parsed from the raw RouterOS
    registration values. Must run before augment_record, which reformats those values for display.
    Unparseable values are reported and skipped, so the record simply lacks that gauge."""
    for source_key, target_key, parse in (
        ('uptime', 'uptime_seconds', parse_uptime_seconds),
        ('tx_rate', 'tx_rate_bps', parse_rate_bps),
        ('rx_rate', 'rx_rate_bps', parse_rate_bps),
    ):
        raw_value = registration_record.get(source_key)
        if not raw_value:
            continue
        value = parse(raw_value)
        if value is None:
            print(
                f"Warning: could not parse {source_key} '{raw_value}' for client {registration_record.get('mac_address', '')}, skipping sample"
            )
            continue
        registration_record[target_key] = value


def augment_record(router_entry, registration_record, id_key='mac_address'):
    """Augments registration record with DHCP names, formatted bitrates, uptime, and signal."""
    resolve_dhcp(router_entry, registration_record, id_key)

    if registration_record.get('bytes'):
        registration_record['tx_bytes'] = registration_record['bytes'].split(',')[0]
        registration_record['rx_bytes'] = registration_record['bytes'].split(',')[1]
        del registration_record['bytes']

    if registration_record.get('tx_rate'):
        registration_record['tx_rate'] = parse_bitrates(
            registration_record['tx_rate']
        )
    if registration_record.get('rx_rate'):
        registration_record['rx_rate'] = parse_bitrates(
            registration_record['rx_rate']
        )
    if registration_record.get('uptime'):
        registration_record['uptime'] = naturaldelta(
            parse_timedelta_seconds(registration_record['uptime']),
            months=True,
            minimum_unit='seconds',
        )

    if registration_record.get('signal_strength'):
        registration_record['signal_strength'] = parse_signal_strength(
            registration_record['signal_strength']
        )
    if registration_record.get('rx_signal'):
        registration_record['rx_signal'] = parse_signal_strength(
            registration_record['rx_signal']
        )
