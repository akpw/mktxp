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
from mktxp.cli.config import LinuxConfig
from mktxp.utils.utils import FSHelper

def test_mktxp_user_dir_path_legacy(mocker):
    """Test that legacy path ~/mktxp is used if it already exists."""
    legacy_path = FSHelper.full_path('~/mktxp')
    
    # Mock that legacy directory exists
    mocker.patch('os.path.exists', return_value=True)
    
    os_config = LinuxConfig()
    assert os_config.mktxp_user_dir_path == legacy_path


def test_mktxp_user_dir_path_xdg(mocker):
    """Test that XDG_CONFIG_HOME is respected when legacy path doesn't exist."""
    # Mock that legacy directory does NOT exist
    mocker.patch('os.path.exists', return_value=False)
    
    # Mock XDG_CONFIG_HOME
    mocker.patch.dict(os.environ, {'XDG_CONFIG_HOME': '/tmp/custom_xdg'}, clear=True)
    
    os_config = LinuxConfig()
    assert os_config.mktxp_user_dir_path == os.path.join('/tmp/custom_xdg', 'mktxp')


def test_mktxp_user_dir_path_xdg_fallback(mocker):
    """Test that ~/.config is used when legacy path and XDG_CONFIG_HOME don't exist."""
    # Mock that legacy directory does NOT exist
    mocker.patch('os.path.exists', return_value=False)
    
    # Mock missing XDG_CONFIG_HOME
    mocker.patch.dict(os.environ, {}, clear=True)
    
    os_config = LinuxConfig()
    expected_xdg = FSHelper.full_path('~/.config')
    assert os_config.mktxp_user_dir_path == os.path.join(expected_xdg, 'mktxp')
