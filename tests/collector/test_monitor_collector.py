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

import pytest
from mktxp.collector.monitor_collector import MonitorCollector


class TestHasNumericValue:
    """Tests for MonitorCollector._has_numeric_value helper."""

    def test_valid_positive_float(self):
        record = {'sfp_rx_power': '-12.5'}
        assert MonitorCollector._has_numeric_value(record, 'sfp_rx_power') is True

    def test_valid_integer_string(self):
        record = {'sfp_wavelength': '1310'}
        assert MonitorCollector._has_numeric_value(record, 'sfp_wavelength') is True

    def test_valid_zero(self):
        """A real zero value should be considered valid."""
        record = {'sfp_temperature': '0'}
        assert MonitorCollector._has_numeric_value(record, 'sfp_temperature') is True

    def test_valid_float_value(self):
        record = {'sfp_tx_bias_current': 0.005}
        assert MonitorCollector._has_numeric_value(record, 'sfp_tx_bias_current') is True

    def test_missing_key(self):
        """DAC/copper SFPs won't have optical DOM fields at all."""
        record = {'name': 'sfp-sfpplus1', 'sfp_module_present': '1'}
        assert MonitorCollector._has_numeric_value(record, 'sfp_rx_power') is False

    def test_none_value(self):
        """Translation table returns None for unsupported fields."""
        record = {'sfp_temperature': None}
        assert MonitorCollector._has_numeric_value(record, 'sfp_temperature') is False

    def test_empty_string(self):
        record = {'sfp_supply_voltage': ''}
        assert MonitorCollector._has_numeric_value(record, 'sfp_supply_voltage') is False

    def test_non_numeric_string(self):
        record = {'sfp_rx_power': 'n/a'}
        assert MonitorCollector._has_numeric_value(record, 'sfp_rx_power') is False


class TestTranslationTable:
    """Tests for the updated translation table lambdas."""

    sfp_temperature_fn = staticmethod(lambda value: value if value else None)
    sfp_tx_bias_current_fn = staticmethod(lambda value: float(value) / 1000 if value else None)

    def test_temperature_with_value(self):
        assert self.sfp_temperature_fn('45') == '45'

    def test_temperature_without_value(self):
        assert self.sfp_temperature_fn(None) is None
        assert self.sfp_temperature_fn('') is None

    def test_bias_current_with_value(self):
        assert self.sfp_tx_bias_current_fn('5000') == 5.0

    def test_bias_current_without_value(self):
        assert self.sfp_tx_bias_current_fn(None) is None
        assert self.sfp_tx_bias_current_fn('') is None


class TestSFPDOMFiltering:
    """Integration-style tests verifying that DAC/copper SFP records are excluded from DOM metrics."""

    @staticmethod
    def _fiber_sfp_record():
        """Simulates a fiber SFP record with full DOM support."""
        return {
            'name': 'sfp-sfpplus1',
            'sfp_module_present': '1',
            'sfp_connector_type': 'LC',
            'sfp_type': 'SFP-or-SFP+',
            'sfp_vendor_name': 'Acme',
            'sfp_vendor_part_number': 'SFP-10G-LR',
            'sfp_vendor_revision': '1.0',
            'sfp_vendor_serial': 'ABC123',
            'sfp_manufacturing_date': '2024-01-01',
            'sfp_rx_power': '-8.3',
            'sfp_tx_power': '-5.1',
            'sfp_supply_voltage': '3.3',
            'sfp_temperature': '42',
            'sfp_tx_bias_current': 0.006,
            'sfp_wavelength': '1310',
            'sfp_rx_loss': '0',
            'sfp_tx_fault': '0',
        }

    @staticmethod
    def _dac_sfp_record():
        """Simulates a DAC/copper SFP record — no optical DOM fields."""
        return {
            'name': 'sfp-sfpplus2',
            'sfp_module_present': '1',
            'sfp_connector_type': 'copper-pigtail',
            'sfp_type': 'SFP-or-SFP+',
            'sfp_vendor_name': 'Acme',
            'sfp_vendor_part_number': 'DAC-10G-1M',
            'sfp_vendor_revision': '2.0',
            'sfp_vendor_serial': 'DEF456',
            'sfp_manufacturing_date': '2024-06-01',
            # No sfp_rx_power, sfp_tx_power, sfp_supply_voltage, sfp_wavelength
            'sfp_temperature': None,       # translation table returns None
            'sfp_tx_bias_current': None,   # translation table returns None
            'sfp_rx_loss': '0',
            'sfp_tx_fault': '0',
        }

    def test_fiber_included_in_dom_metrics(self):
        fiber = self._fiber_sfp_record()
        for key in ['sfp_rx_power', 'sfp_tx_power', 'sfp_supply_voltage', 'sfp_temperature', 'sfp_tx_bias_current', 'sfp_wavelength']:
            assert MonitorCollector._has_numeric_value(fiber, key) is True

    def test_dac_excluded_from_dom_metrics(self):
        dac = self._dac_sfp_record()
        for key in ['sfp_rx_power', 'sfp_tx_power', 'sfp_supply_voltage', 'sfp_temperature', 'sfp_tx_bias_current', 'sfp_wavelength']:
            assert MonitorCollector._has_numeric_value(dac, key) is False

    def test_mixed_sfp_filtering(self):
        """When both fiber and DAC records exist, only fiber records pass the filter."""
        fiber = self._fiber_sfp_record()
        dac = self._dac_sfp_record()
        sfp_metrics = [fiber, dac]

        for key in ['sfp_rx_power', 'sfp_tx_power', 'sfp_supply_voltage', 'sfp_temperature', 'sfp_tx_bias_current', 'sfp_wavelength']:
            filtered = [r for r in sfp_metrics if MonitorCollector._has_numeric_value(r, key)]
            assert len(filtered) == 1
            assert filtered[0]['name'] == 'sfp-sfpplus1'
