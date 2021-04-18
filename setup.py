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

from setuptools import setup, find_packages
from os import path

# read the README.md contents
pkg_dir = path.abspath(path.dirname(__file__))
with open(path.join(pkg_dir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='mktxp',
    version='0.30',

    url='https://github.com/akpw/mktxp',

    author='Arseniy Kuznetsov',
    author_email='k.arseniy@gmail.com',

    long_description=long_description,
    long_description_content_type='text/markdown',

    description=('''
                    Prometheus Exporter for Mikrotik RouterOS devices
                '''),
    license='GNU General Public License v2 (GPLv2)',

    packages=find_packages(exclude=['test*']),

    package_data = {
        '': ['config/*.conf'],
    },

    keywords = 'Mikrotik RouterOS Prometheus Exporter',

    install_requires = ['prometheus-client>=0.9.0', 
                        'RouterOS-api>=0.17.0', 
                        'configobj>=5.0.6',
                        'humanize>=3.2.0',
                        'texttable>=1.6.3',
                        'speedtest-cli>=2.1.2'
                        ],

    test_suite = 'tests.mktxp_test_suite',

    entry_points={'console_scripts': [
        'mktxp = mktxp.cli.dispatch:main',
    ]},

    zip_safe=True,

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Information Technology',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Topic :: System',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities'
    ]
)



