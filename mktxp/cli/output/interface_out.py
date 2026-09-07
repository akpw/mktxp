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

import re
from mktxp.cli.output.tables import (
    output_table,
    OutputInterfaceEntry,
    OutputSFPDetailEntry,
)
from mktxp.utils.filtering import match_record
from mktxp.utils.units import parse_numeric_rate, parse_rate_limit, parse_bitrates
from mktxp.datasource.interface_ds import InterfaceMonitorMetricsDataSource


class InterfaceOutput:
    """Interface Monitor CLI Output."""

    DEFAULT_DEGRADED_THRESHOLD = "100M"

    @staticmethod
    def interfaces_summary(
        router_entry,
        include=None,
        exclude=None,
        diag_conf=None,
        plugged_only=False,
        unplugged_only=False,
        degraded=None,
        rate=None,
        rate_below=None,
        sfp_only=False,
    ):
        """Display Ethernet & SFP interface monitor summary."""
        print(f'{router_entry.router_name}@{router_entry.config_entry.hostname}: OK to connect')
        print(f'Connecting to router {router_entry.router_name}@{router_entry.config_entry.hostname}')

        records = InterfaceOutput._collect_records(router_entry, sfp_only=sfp_only)
        if not records:
            print("No interface monitor records found")
            return

        degraded_def = (
            diag_conf.get("degraded_threshold", InterfaceOutput.DEFAULT_DEGRADED_THRESHOLD)
            if diag_conf
            else InterfaceOutput.DEFAULT_DEGRADED_THRESHOLD
        )
        if degraded is True:
            degraded_rate_str = degraded_def
        elif isinstance(degraded, str):
            degraded_rate_str = degraded
        else:
            degraded_rate_str = None

        if sfp_only:
            InterfaceOutput._display_sfp_table(
                records,
                include=include,
                exclude=exclude,
                plugged_only=plugged_only,
                unplugged_only=unplugged_only,
                degraded=degraded,
                degraded_rate_str=degraded_rate_str,
                rate=rate,
                rate_below=rate_below,
            )
        else:
            InterfaceOutput._display_main_table(
                records,
                include=include,
                exclude=exclude,
                plugged_only=plugged_only,
                unplugged_only=unplugged_only,
                degraded=degraded,
                degraded_rate_str=degraded_rate_str,
                degraded_def=degraded_def,
                rate=rate,
                rate_below=rate_below,
            )

    @staticmethod
    def _collect_records(router_entry, sfp_only=False):
        """Collect interface monitor records from RouterOS."""
        metric_labels = [
            'name',
            'status',
            'rate',
            'full_duplex',
            'auto_negotiation',
            'sfp_module_present',
            'sfp_type',
            'sfp_vendor_name',
            'sfp_vendor_part_number',
            'sfp_vendor_serial',
            'sfp_connector_type',
            'sfp_rx_power',
            'sfp_tx_power',
            'sfp_temperature',
            'sfp_supply_voltage',
            'sfp_rx_loss',
            'sfp_tx_fault',
            'sfp_wavelength',
        ]
        try:
            records = InterfaceMonitorMetricsDataSource.metric_records(
                router_entry,
                metric_labels=metric_labels,
                kind='ethernet',
                running_only=not sfp_only,
            )
            return records if records else []
        except Exception as exc:
            print(f"Error getting interface monitor info: {exc}")
            return []

    @staticmethod
    def _format_rate(rate_val):
        """Format interface rate cleanly with space between value and unit."""
        if not rate_val or str(rate_val).strip() in ('', '0', '-'):
            return '-'
        rate_str = str(rate_val).strip()
        if rate_str.isdigit() and int(rate_str) > 100000:
            return parse_bitrates(rate_str)
        match = re.match(r'^([\d.]+)\s*([A-Za-z/]+)$', rate_str)
        if match:
            val, unit = match.group(1), match.group(2).replace('/', '').lower()
            if 'g' in unit:
                unit_norm = 'Gbps'
            elif 'm' in unit:
                unit_norm = 'Mbps'
            elif 'k' in unit:
                unit_norm = 'Kbps'
            elif 't' in unit:
                unit_norm = 'Tbps'
            else:
                unit_norm = match.group(2)
            return f"{val} {unit_norm}"
        return rate_str

    @staticmethod
    def _is_sfp_record(record):
        """Check if interface is an SFP transceiver or cage."""
        if str(record.get('sfp_module_present', '')).lower() in ('true', '1'):
            return True
        if record.get('sfp_type') or record.get('sfp_connector_type'):
            return True
        name = record.get('name', '').lower()
        return 'sfp' in name or 'qsfp' in name

    @staticmethod
    def _matches_filters(record, plugged_only, unplugged_only, degraded, degraded_rate_str, rate, rate_below):
        """Check if a record matches active interface diagnostic filters."""
        is_plugged = record.get('status') == 'link-ok'

        if plugged_only and not is_plugged:
            return False
        if unplugged_only and is_plugged:
            return False

        rec_rate_bps = parse_numeric_rate(record.get('rate')) if is_plugged else 0
        fd_val = str(record.get('full_duplex', '')).lower()
        is_half_duplex = fd_val in ('false', '0')

        if degraded is not None and degraded is not False:
            threshold_bps = parse_rate_limit(degraded_rate_str)
            is_sub_rate = 0 < rec_rate_bps < threshold_bps
            is_degraded = is_plugged and (is_sub_rate or is_half_duplex)
            if not is_degraded:
                return False

        if rate is not None:
            target_rate_bps = parse_numeric_rate(rate) or parse_rate_limit(rate)
            if target_rate_bps > 0 and rec_rate_bps != target_rate_bps:
                return False

        if rate_below is not None:
            threshold_bps = parse_rate_limit(rate_below)
            if threshold_bps > 0 and not (0 < rec_rate_bps < threshold_bps):
                return False

        return True

    @staticmethod
    def _display_main_table(
        records,
        include=None,
        exclude=None,
        plugged_only=False,
        unplugged_only=False,
        degraded=None,
        degraded_rate_str=None,
        degraded_def="100M",
        rate=None,
        rate_below=None,
    ):
        """Display main interfaces summary table."""
        total_unfiltered = len(records)
        filtered = []

        for record in records:
            if not InterfaceOutput._matches_filters(
                record, plugged_only, unplugged_only, degraded, degraded_rate_str, rate, rate_below
            ):
                continue
            if not match_record(record, include, exclude):
                continue
            filtered.append(record)

        if not filtered:
            print("Interface Monitor: No matching interfaces found")
            return

        output_entry = OutputInterfaceEntry
        tbl = output_table(output_entry)
        tbl.header(['Interface', 'Status', 'Rate', 'Duplex', 'Auto-Neg', 'SFP'])

        for r in filtered:
            is_plugged = r.get('status') == 'link-ok'
            status_disp = 'Plugged-In' if is_plugged else 'Unplugged'
            rate_disp = InterfaceOutput._format_rate(r.get('rate')) if is_plugged else '-'

            fd = str(r.get('full_duplex', '')).lower()
            if not is_plugged:
                duplex_disp = '-'
            elif fd in ('true', '1'):
                duplex_disp = 'Full'
            elif fd in ('false', '0'):
                duplex_disp = 'Half'
            else:
                duplex_disp = '-'

            an = str(r.get('auto_negotiation', '')).lower()
            if not is_plugged:
                auto_neg_disp = '-'
            elif an == 'done':
                auto_neg_disp = 'Done'
            elif an in ('disabled', 'off', 'false', '0'):
                auto_neg_disp = 'Off'
            elif an == 'in-progress':
                auto_neg_disp = 'Negotiating'
            elif an == 'failed':
                auto_neg_disp = 'Failed'
            elif an:
                auto_neg_disp = str(r.get('auto_negotiation')).capitalize()
            else:
                auto_neg_disp = '-'

            sfp_present = str(r.get('sfp_module_present', '')).lower() in ('true', '1')
            sfp_type = r.get('sfp_type', '')
            sfp_vendor = r.get('sfp_vendor_name', '')
            if sfp_present:
                if sfp_type and sfp_vendor:
                    sfp_disp = f"{sfp_type} ({sfp_vendor})"
                elif sfp_type:
                    sfp_disp = sfp_type
                elif sfp_vendor:
                    sfp_disp = sfp_vendor
                else:
                    sfp_disp = 'Yes'
            else:
                sfp_disp = '-'

            tbl.add_row(
                output_entry(
                    interface=r.get('name', ''),
                    status=status_disp,
                    rate=rate_disp,
                    duplex=duplex_disp,
                    auto_neg=auto_neg_disp,
                    sfp=sfp_disp,
                )
            )

        print("Interface Monitor:")
        print(tbl.draw())

        total_entries = len(filtered)
        plugged_count = len([r for r in filtered if r.get('status') == 'link-ok'])
        unplugged_count = total_entries - plugged_count

        active_sub_rate_str = degraded_rate_str if degraded_rate_str else degraded_def
        sub_rate_bps = parse_rate_limit(active_sub_rate_str)
        degraded_count = len([
            r for r in filtered
            if r.get('status') == 'link-ok' and (
                0 < parse_numeric_rate(r.get('rate')) < sub_rate_bps
                or str(r.get('full_duplex', '')).lower() in ('false', '0')
            )
        ])

        has_filters = (
            bool(include)
            or bool(exclude)
            or plugged_only
            or unplugged_only
            or (degraded is not None and degraded is not False)
            or rate is not None
            or rate_below is not None
        )

        if has_filters:
            print(f"Matching interfaces: {total_entries} (Total: {total_unfiltered})")
        else:
            print(f"Total interfaces: {total_entries}")
        print(f"Plugged: {plugged_count}")
        print(f"Unplugged: {unplugged_count}")
        print(f"Degraded (< {active_sub_rate_str}): {degraded_count}")

    @staticmethod
    def _display_sfp_table(
        records,
        include=None,
        exclude=None,
        plugged_only=False,
        unplugged_only=False,
        degraded=None,
        degraded_rate_str=None,
        rate=None,
        rate_below=None,
    ):
        """Display SFP transceivers table with optical DOM diagnostics."""
        sfp_records = [r for r in records if InterfaceOutput._is_sfp_record(r)]
        total_sfp_unfiltered = len(sfp_records)
        filtered = []

        for record in sfp_records:
            if not InterfaceOutput._matches_filters(
                record, plugged_only, unplugged_only, degraded, degraded_rate_str, rate, rate_below
            ):
                continue
            if not match_record(record, include, exclude):
                continue
            filtered.append(record)

        if not filtered:
            print("SFP Monitor: No matching SFP interfaces found")
            return

        output_entry = OutputSFPDetailEntry
        tbl = output_table(output_entry)
        tbl.header([
            'Interface',
            'Status',
            'Rate',
            'Type',
            'Vendor / Part',
            'Connector',
            'Rx Power',
            'Tx Power',
            'Temp',
        ])
        tbl.set_cols_align(['l', 'c', 'c', 'l', 'l', 'c', 'c', 'c', 'c'])

        for r in filtered:
            is_plugged = r.get('status') == 'link-ok'
            status_disp = 'Plugged-In' if is_plugged else 'Unplugged'
            rate_disp = InterfaceOutput._format_rate(r.get('rate')) if is_plugged else '-'
            type_disp = r.get('sfp_type', '') or '-'

            vendor = r.get('sfp_vendor_name', '')
            part = r.get('sfp_vendor_part_number', '')
            if vendor and part:
                vp_disp = f"{vendor} {part}"
            elif vendor:
                vp_disp = vendor
            elif part:
                vp_disp = part
            else:
                vp_disp = '-'

            connector_disp = r.get('sfp_connector_type', '') or '-'

            if str(r.get('sfp_rx_loss', '')).lower() in ('true', '1'):
                rx_disp = 'Loss'
            elif r.get('sfp_rx_power') is not None and str(r.get('sfp_rx_power')).strip() != '':
                rx_disp = f"{r.get('sfp_rx_power')} dBm"
            else:
                rx_disp = '-'

            if str(r.get('sfp_tx_fault', '')).lower() in ('true', '1'):
                tx_disp = 'Fault'
            elif r.get('sfp_tx_power') is not None and str(r.get('sfp_tx_power')).strip() != '':
                tx_disp = f"{r.get('sfp_tx_power')} dBm"
            else:
                tx_disp = '-'

            temp = r.get('sfp_temperature')
            if temp is not None and str(temp).strip() != '':
                clean_temp = str(temp).replace('C', '').strip()
                temp_disp = f"{clean_temp} °C"
            else:
                temp_disp = '-'

            tbl.add_row(
                output_entry(
                    interface=r.get('name', ''),
                    status=status_disp,
                    rate=rate_disp,
                    type=type_disp,
                    vendor_part=vp_disp,
                    connector=connector_disp,
                    rx_power=rx_disp,
                    tx_power=tx_disp,
                    temperature=temp_disp,
                )
            )

        print("SFP Interface Monitor:")
        print(tbl.draw())

        total_entries = len(filtered)
        plugged_count = len([r for r in filtered if r.get('status') == 'link-ok'])
        unplugged_count = total_entries - plugged_count

        has_filters = (
            bool(include)
            or bool(exclude)
            or plugged_only
            or unplugged_only
            or (degraded is not None and degraded is not False)
            or rate is not None
            or rate_below is not None
        )

        if has_filters:
            print(f"Matching SFP interfaces: {total_entries} (Total SFP: {total_sfp_unfiltered})")
        else:
            print(f"Total SFP interfaces: {total_entries}")
        print(f"Plugged: {plugged_count}")
        print(f"Unplugged: {unplugged_count}")
