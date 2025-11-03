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
from mktxp.cli.config.config import MKTXPConfigHandler, MKTXPConfigKeys, CustomConfig
from mktxp.datasource.base_ds import BaseDSProcessor

def test_default_config_no_new_keys(tmpdir):
    mktxp_conf_path = tmpdir.join("mktxp.conf")
    _mktxp_conf_path = tmpdir.join("_mktxp.conf")

    config = ConfigObj(str(mktxp_conf_path))
    config['default'] = {}
    for key in MKTXPConfigKeys.BOOLEAN_KEYS_YES.union(MKTXPConfigKeys.BOOLEAN_KEYS_NO):
        config['default'][key] = 'False'
    for key in MKTXPConfigKeys.STR_KEYS:
        config['default'][key] = "some_value"
    config['default'][MKTXPConfigKeys.PORT_KEY] = '1234'
    config.write()

    _mktxp_conf_path.write("""
[MKTXP]
verbose_mode = False
""")

    handler = MKTXPConfigHandler()
    handler(os_config=CustomConfig(str(tmpdir)))

    final_config = ConfigObj(str(mktxp_conf_path))
    assert MKTXPConfigKeys.MKTXP_LATEST_DEFAULT_ENTRY_KEY not in final_config

def test_default_config_with_new_key(tmpdir):
    mktxp_conf_path = tmpdir.join("mktxp.conf")
    _mktxp_conf_path = tmpdir.join("_mktxp.conf")
    mktxp_conf_path.write("""
[default]
# health key is missing
""")
    _mktxp_conf_path.write("""
[MKTXP]
verbose_mode = False
""")

    handler = MKTXPConfigHandler()
    handler(os_config=CustomConfig(str(tmpdir)))

    final_config = ConfigObj(str(mktxp_conf_path))
    assert MKTXPConfigKeys.MKTXP_LATEST_DEFAULT_ENTRY_KEY in final_config
    assert 'health' in final_config[MKTXPConfigKeys.MKTXP_LATEST_DEFAULT_ENTRY_KEY]
    assert final_config[MKTXPConfigKeys.MKTXP_LATEST_DEFAULT_ENTRY_KEY].as_bool('health') is True
    assert 'health' not in final_config['default']

def test_default_config_key_in_new_section(tmpdir):
    mktxp_conf_path = tmpdir.join("mktxp.conf")
    _mktxp_conf_path = tmpdir.join("_mktxp.conf")

    config = ConfigObj()
    config.filename = str(mktxp_conf_path)
    config['default'] = {}
    for key in MKTXPConfigKeys.BOOLEAN_KEYS_YES.union(MKTXPConfigKeys.BOOLEAN_KEYS_NO):
        if key != 'health':
            config['default'][key] = 'False'
    for key in MKTXPConfigKeys.STR_KEYS:
        config['default'][key] = "some_value"
    config['default'][MKTXPConfigKeys.PORT_KEY] = '1234'
    
    config[MKTXPConfigKeys.MKTXP_LATEST_DEFAULT_ENTRY_KEY] = {
        'health': 'True'
    }
    config.write()

    _mktxp_conf_path.write("""
[MKTXP]
verbose_mode = False
""")

    handler = MKTXPConfigHandler()
    handler(os_config=CustomConfig(str(tmpdir)))

    final_config = ConfigObj(str(mktxp_conf_path))
    assert 'health' in final_config[MKTXPConfigKeys.MKTXP_LATEST_DEFAULT_ENTRY_KEY]
    assert final_config[MKTXPConfigKeys.MKTXP_LATEST_DEFAULT_ENTRY_KEY].as_bool('health') is True

def test_system_config_no_new_keys(tmpdir):
    mktxp_conf_path = tmpdir.join("mktxp.conf")
    _mktxp_conf_path = tmpdir.join("_mktxp.conf")
    mktxp_conf_path.write("[default]")

    config = ConfigObj(str(_mktxp_conf_path))
    config['MKTXP'] = {}
    for key in MKTXPConfigKeys.MKTXP_INT_KEYS:
        config['MKTXP'][key] = '123'
    for key in MKTXPConfigKeys.MKTXP_STR_KEYS:
        config['MKTXP'][key] = '1.1.1.1'
    for key in MKTXPConfigKeys.SYSTEM_BOOLEAN_KEYS_YES.union(MKTXPConfigKeys.SYSTEM_BOOLEAN_KEYS_NO):
        config['MKTXP'][key] = 'False'
    config['MKTXP'][MKTXPConfigKeys.LISTEN_KEY] = "0.0.0.0:1234"
    config.write()

    handler = MKTXPConfigHandler()
    handler(os_config=CustomConfig(str(tmpdir)))

    final_config = ConfigObj(str(_mktxp_conf_path))
    assert MKTXPConfigKeys.MKTXP_LATEST_SYSTEM_ENTRY_KEY not in final_config

def test_system_config_with_new_key(tmpdir):
    mktxp_conf_path = tmpdir.join("mktxp.conf")
    _mktxp_conf_path = tmpdir.join("_mktxp.conf")
    mktxp_conf_path.write("[default]")
    _mktxp_conf_path.write("""
[MKTXP]
# verbose_mode is missing
""")

    handler = MKTXPConfigHandler()
    handler(os_config=CustomConfig(str(tmpdir)))

    final_config = ConfigObj(str(_mktxp_conf_path))
    assert MKTXPConfigKeys.MKTXP_LATEST_SYSTEM_ENTRY_KEY in final_config
    assert 'verbose_mode' in final_config[MKTXPConfigKeys.MKTXP_LATEST_SYSTEM_ENTRY_KEY]
    assert final_config[MKTXPConfigKeys.MKTXP_LATEST_SYSTEM_ENTRY_KEY].as_bool('verbose_mode') is False
    assert 'verbose_mode' not in final_config['MKTXP']

def test_system_config_key_in_new_section(tmpdir):
    mktxp_conf_path = tmpdir.join("mktxp.conf")
    _mktxp_conf_path = tmpdir.join("_mktxp.conf")
    mktxp_conf_path.write("[default]")

    config = ConfigObj(str(_mktxp_conf_path))
    config['MKTXP'] = {}
    for key in MKTXPConfigKeys.MKTXP_INT_KEYS:
        config['MKTXP'][key] = '123'
    for key in MKTXPConfigKeys.SYSTEM_BOOLEAN_KEYS_YES.union(MKTXPConfigKeys.SYSTEM_BOOLEAN_KEYS_NO):
        if key != 'verbose_mode':
            config['MKTXP'][key] = 'False'
    config['MKTXP'][MKTXPConfigKeys.LISTEN_KEY] = "0.0.0.0:1234"

    config[MKTXPConfigKeys.MKTXP_LATEST_SYSTEM_ENTRY_KEY] = {
        'verbose_mode': 'False'
    }
    config.write()

    handler = MKTXPConfigHandler()
    handler(os_config=CustomConfig(str(tmpdir)))

    final_config = ConfigObj(str(_mktxp_conf_path))
    assert 'verbose_mode' in final_config[MKTXPConfigKeys.MKTXP_LATEST_SYSTEM_ENTRY_KEY]
    assert final_config[MKTXPConfigKeys.MKTXP_LATEST_SYSTEM_ENTRY_KEY].as_bool('verbose_mode') is False

