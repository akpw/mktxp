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
import re
from importlib.metadata import version as pkg_version, PackageNotFoundError


def get_version() -> str:
    """Retrieve MKTXP version, checking pyproject.toml in local dev repository first."""
    try:
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pyproject = os.path.join(repo_root, "pyproject.toml")
        if os.path.isfile(pyproject):
            with open(pyproject, "r", encoding="utf-8") as f:
                match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', f.read())
                if match:
                    return match.group(1)
    except Exception:
        pass

    try:
        return pkg_version("mktxp")
    except PackageNotFoundError:
        return "unknown"


__version__ = get_version()
