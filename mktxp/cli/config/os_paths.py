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
import sys
from abc import ABCMeta
from mktxp.utils.utils import FSHelper


class OSConfig(metaclass=ABCMeta):
    """OS-specific configuration directory discovery and resolution."""

    @staticmethod
    def os_config():
        """Factory method returning the OSConfig instance for the current platform."""
        if sys.platform == 'linux':
            return LinuxConfig()
        elif sys.platform == 'darwin':
            return OSXConfig()
        elif sys.platform.startswith('freebsd'):
            return FreeBSDConfig()
        else:
            print(f'Non-supported platform: {sys.platform}')
            return None

    @property
    def mktxp_user_dir_path(self):
        legacy_path = FSHelper.full_path('~/mktxp')
        if os.path.exists(legacy_path):
            return legacy_path

        xdg_config = os.environ.get('XDG_CONFIG_HOME') or FSHelper.full_path('~/.config')
        return os.path.join(xdg_config, 'mktxp')


class FreeBSDConfig(OSConfig):
    """FreeBSD-related config"""

    @property
    def mktxp_user_dir_path(self):
        return super().mktxp_user_dir_path


class OSXConfig(OSConfig):
    """OSX-related config"""

    @property
    def mktxp_user_dir_path(self):
        return super().mktxp_user_dir_path


class LinuxConfig(OSConfig):
    """Linux-related config"""

    @property
    def mktxp_user_dir_path(self):
        return super().mktxp_user_dir_path


class CustomConfig(OSConfig):
    """Custom directory config override"""

    def __init__(self, path):
        self._user_dir_path = path

    @property
    def mktxp_user_dir_path(self):
        return FSHelper.full_path(self._user_dir_path)
