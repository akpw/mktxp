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

import os
import pytest
from configobj import ConfigObj
from mktxp.cli.config import MKTXPConfigHandler, CustomConfig


def test_rsc_config_injects_when_missing(tmp_path):
    conf_dir = tmp_path / "conf"
    conf_dir.mkdir()
    mktxp_conf_path = conf_dir / "_mktxp.conf"
    usr_conf_path = conf_dir / "mktxp.conf"

    # Create dummy config files without [RSC]
    with open(mktxp_conf_path, 'w', encoding='utf-8') as f:
        f.write("[MKTXP]\nlisten = '0.0.0.0:49090'\n")
    with open(usr_conf_path, 'w', encoding='utf-8') as f:
        f.write("[default]\nhostname = 192.168.1.1\n")

    handler = MKTXPConfigHandler()
    handler(os_config=CustomConfig(str(conf_dir)))
    rsc_conf = handler.rsc_config()

    assert rsc_conf is not None
    assert rsc_conf.get('base_dir') == './exports'
    assert 'handler_base' in rsc_conf
    assert 'handler_firewall' in rsc_conf

    # Verify it was written to disk
    reloaded = ConfigObj(str(mktxp_conf_path), indent_type='    ', encoding='utf-8')
    assert 'RSC' in reloaded
    assert reloaded['RSC']['base_dir'] == './exports'


def test_rsc_config_preserves_existing_keys(tmp_path):
    conf_dir = tmp_path / "conf"
    conf_dir.mkdir()
    mktxp_conf_path = conf_dir / "_mktxp.conf"
    usr_conf_path = conf_dir / "mktxp.conf"

    with open(mktxp_conf_path, 'w', encoding='utf-8') as f:
        f.write("[MKTXP]\nlisten = '0.0.0.0:49090'\n\n[RSC]\nbase_dir = '/my/custom/exports'\n")
    with open(usr_conf_path, 'w', encoding='utf-8') as f:
        f.write("[default]\nhostname = 192.168.1.1\n")

    handler = MKTXPConfigHandler()
    handler(os_config=CustomConfig(str(conf_dir)))
    rsc_conf = handler.rsc_config()

    assert rsc_conf.get('base_dir') == '/my/custom/exports'
    # Missing keys should have been injected
    assert 'handler_base' in rsc_conf
    assert 'handler_wifi' in rsc_conf
