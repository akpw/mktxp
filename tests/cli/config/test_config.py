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
from configobj import ConfigObj
from routeros_exporter.cli.config.config import RouterOSExporterConfigHandler, RouterOSExporterConfigKeys, CustomConfig
from routeros_exporter.datasource.base_ds import BaseDSProcessor

def test_default_config_no_new_keys(tmpdir):
    routeros_exporter_conf_path = tmpdir.join("routeros_exporter.conf")
    _routeros_exporter_conf_path = tmpdir.join("exporter.conf")

    config = ConfigObj(str(routeros_exporter_conf_path))
    config['default'] = {}
    for key in RouterOSExporterConfigKeys.BOOLEAN_KEYS_YES.union(RouterOSExporterConfigKeys.BOOLEAN_KEYS_NO):
        config['default'][key] = 'False'
    for key in RouterOSExporterConfigKeys.STR_KEYS:
        config['default'][key] = "some_value"
    config['default'][RouterOSExporterConfigKeys.PORT_KEY] = '1234'
    config.write()

    _routeros_exporter_conf_path.write("""
[RouterOS_Exporter]
verbose_mode = False
""")

    handler = RouterOSExporterConfigHandler()
    handler(os_config=CustomConfig(str(tmpdir)))

    final_config = ConfigObj(str(routeros_exporter_conf_path))
    assert RouterOSExporterConfigKeys.RouterOS_Exporter_LATEST_DEFAULT_ENTRY_KEY not in final_config

def test_default_config_with_new_key(tmpdir):
    routeros_exporter_conf_path = tmpdir.join("routeros_exporter.conf")
    _routeros_exporter_conf_path = tmpdir.join("exporter.conf")
    routeros_exporter_conf_path.write("""
[default]
# health key is missing
""")
    _routeros_exporter_conf_path.write("""
[RouterOS_Exporter]
verbose_mode = False
""")

    handler = RouterOSExporterConfigHandler()
    handler(os_config=CustomConfig(str(tmpdir)))

    final_config = ConfigObj(str(routeros_exporter_conf_path))
    assert RouterOSExporterConfigKeys.RouterOS_Exporter_LATEST_DEFAULT_ENTRY_KEY in final_config
    assert 'health' in final_config[RouterOSExporterConfigKeys.RouterOS_Exporter_LATEST_DEFAULT_ENTRY_KEY]
    assert final_config[RouterOSExporterConfigKeys.RouterOS_Exporter_LATEST_DEFAULT_ENTRY_KEY].as_bool('health') is True
    assert 'health' not in final_config['default']

def test_default_config_key_in_new_section(tmpdir):
    routeros_exporter_conf_path = tmpdir.join("routeros_exporter.conf")
    _routeros_exporter_conf_path = tmpdir.join("exporter.conf")

    config = ConfigObj()
    config.filename = str(routeros_exporter_conf_path)
    config['default'] = {}
    for key in RouterOSExporterConfigKeys.BOOLEAN_KEYS_YES.union(RouterOSExporterConfigKeys.BOOLEAN_KEYS_NO):
        if key != 'health':
            config['default'][key] = 'False'
    for key in RouterOSExporterConfigKeys.STR_KEYS:
        config['default'][key] = "some_value"
    config['default'][RouterOSExporterConfigKeys.PORT_KEY] = '1234'
    
    config[RouterOSExporterConfigKeys.RouterOS_Exporter_LATEST_DEFAULT_ENTRY_KEY] = {
        'health': 'True'
    }
    config.write()

    _routeros_exporter_conf_path.write("""
[RouterOS_Exporter]
verbose_mode = False
""")

    handler = RouterOSExporterConfigHandler()
    handler(os_config=CustomConfig(str(tmpdir)))

    final_config = ConfigObj(str(routeros_exporter_conf_path))
    assert 'health' in final_config[RouterOSExporterConfigKeys.RouterOS_Exporter_LATEST_DEFAULT_ENTRY_KEY]
    assert final_config[RouterOSExporterConfigKeys.RouterOS_Exporter_LATEST_DEFAULT_ENTRY_KEY].as_bool('health') is True

def test_system_config_no_new_keys(tmpdir):
    routeros_exporter_conf_path = tmpdir.join("routeros_exporter.conf")
    _routeros_exporter_conf_path = tmpdir.join("exporter.conf")
    routeros_exporter_conf_path.write("[default]")

    config = ConfigObj(str(_routeros_exporter_conf_path))
    config['RouterOS_Exporter'] = {}
    for key in RouterOSExporterConfigKeys.RouterOS_Exporter_INT_KEYS:
        config['RouterOS_Exporter'][key] = '123'
    for key in RouterOSExporterConfigKeys.SYSTEM_BOOLEAN_KEYS_YES.union(RouterOSExporterConfigKeys.SYSTEM_BOOLEAN_KEYS_NO):
        config['RouterOS_Exporter'][key] = 'False'
    config['RouterOS_Exporter'][RouterOSExporterConfigKeys.LISTEN_KEY] = "0.0.0.0:1234"
    config.write()

    handler = RouterOSExporterConfigHandler()
    handler(os_config=CustomConfig(str(tmpdir)))

    final_config = ConfigObj(str(_routeros_exporter_conf_path))
    assert RouterOSExporterConfigKeys.RouterOS_Exporter_LATEST_SYSTEM_ENTRY_KEY not in final_config

def test_system_config_with_new_key(tmpdir):
    routeros_exporter_conf_path = tmpdir.join("routeros_exporter.conf")
    _routeros_exporter_conf_path = tmpdir.join("exporter.conf")
    routeros_exporter_conf_path.write("[default]")
    _routeros_exporter_conf_path.write("""
[RouterOS_Exporter]
# verbose_mode is missing
""")

    handler = RouterOSExporterConfigHandler()
    handler(os_config=CustomConfig(str(tmpdir)))

    final_config = ConfigObj(str(_routeros_exporter_conf_path))
    assert RouterOSExporterConfigKeys.RouterOS_Exporter_LATEST_SYSTEM_ENTRY_KEY in final_config
    assert 'verbose_mode' in final_config[RouterOSExporterConfigKeys.RouterOS_Exporter_LATEST_SYSTEM_ENTRY_KEY]
    assert final_config[RouterOSExporterConfigKeys.RouterOS_Exporter_LATEST_SYSTEM_ENTRY_KEY].as_bool('verbose_mode') is False
    assert 'verbose_mode' not in final_config['RouterOS_Exporter']

def test_system_config_key_in_new_section(tmpdir):
    routeros_exporter_conf_path = tmpdir.join("routeros_exporter.conf")
    _routeros_exporter_conf_path = tmpdir.join("exporter.conf")
    routeros_exporter_conf_path.write("[default]")

    config = ConfigObj(str(_routeros_exporter_conf_path))
    config['RouterOS_Exporter'] = {}
    for key in RouterOSExporterConfigKeys.RouterOS_Exporter_INT_KEYS:
        config['RouterOS_Exporter'][key] = '123'
    for key in RouterOSExporterConfigKeys.SYSTEM_BOOLEAN_KEYS_YES.union(RouterOSExporterConfigKeys.SYSTEM_BOOLEAN_KEYS_NO):
        if key != 'verbose_mode':
            config['RouterOS_Exporter'][key] = 'False'
    config['RouterOS_Exporter'][RouterOSExporterConfigKeys.LISTEN_KEY] = "0.0.0.0:1234"

    config[RouterOSExporterConfigKeys.RouterOS_Exporter_LATEST_SYSTEM_ENTRY_KEY] = {
        'verbose_mode': 'False'
    }
    config.write()

    handler = RouterOSExporterConfigHandler()
    handler(os_config=CustomConfig(str(tmpdir)))

    final_config = ConfigObj(str(_routeros_exporter_conf_path))
    assert 'verbose_mode' in final_config[RouterOSExporterConfigKeys.RouterOS_Exporter_LATEST_SYSTEM_ENTRY_KEY]
    assert final_config[RouterOSExporterConfigKeys.RouterOS_Exporter_LATEST_SYSTEM_ENTRY_KEY].as_bool('verbose_mode') is False

