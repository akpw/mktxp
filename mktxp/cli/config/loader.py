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
import shutil
import importlib.resources
from configobj import ConfigObj

from mktxp.cli.config.keys import MKTXPConfigKeys
from mktxp.cli.config.models import ConfigEntry, mockSystemEntry
from mktxp.cli.config.os_paths import OSConfig


class MKTXPConfigHandler:
    """Core configuration reader, disk I/O manager, and dynamic auto-injection engine."""

    def __init__(self):
        self.system_entry = mockSystemEntry

    def __call__(self, os_config=None):
        self.os_config = os_config if os_config else OSConfig.os_config()
        if not self.os_config:
            sys.exit(1)

        if not os.path.exists(self.os_config.mktxp_user_dir_path):
            os.makedirs(self.os_config.mktxp_user_dir_path)

        self.usr_conf_data_path = os.path.join(
            self.os_config.mktxp_user_dir_path, 'mktxp.conf'
        )
        self.mktxp_conf_path = os.path.join(
            self.os_config.mktxp_user_dir_path, '_mktxp.conf'
        )

        self._create_os_path(self.usr_conf_data_path, 'cli/config/mktxp.conf')
        self._create_os_path(self.mktxp_conf_path, 'cli/config/_mktxp.conf')

        self.re_compiled = {}
        self._read_from_disk()

        self.default_config_entry_reader = self._default_config_entry_reader()
        self.system_entry = self._system_entry()

    def registered_entries(self):
        """All MKTXP registered router entries generator."""
        return (
            entry_name
            for entry_name in self.config.keys()
            if entry_name
            not in (
                MKTXPConfigKeys.DEFAULT_ENTRY_KEY,
                MKTXPConfigKeys.MKTXP_LATEST_DEFAULT_ENTRY_KEY,
            )
        )

    def registered_entry(self, entry_name):
        """A specific MKTXP registered entry raw dict by name."""
        return self.config.get(entry_name)

    def config_entry(self, entry_name):
        """Given an entry name, reads and returns the typed MKTXPConfigEntry."""
        entry_reader = self._config_entry_reader(entry_name)
        return ConfigEntry.MKTXPConfigEntry(**entry_reader) if entry_reader else None

    def _system_entry(self):
        _entry_reader = self._system_entry_reader()
        return ConfigEntry.MKTXPSystemEntry(**_entry_reader)

    def _rsc_template(self):
        try:
            ref = importlib.resources.files('mktxp') / 'cli/config/_mktxp.conf'
            with importlib.resources.as_file(ref) as path:
                template_conf = ConfigObj(str(path), indent_type='    ', encoding='utf-8')
                return template_conf.get('RSC', {})
        except Exception:
            return {}

    def _rsc_config_reader(self):
        template_rsc = self._rsc_template()
        changed = False

        if 'RSC' not in self._config:
            self._config['RSC'] = {}
            for k, v in template_rsc.items():
                self._config['RSC'][k] = v
            changed = True
        else:
            for k, v in template_rsc.items():
                if k not in self._config['RSC']:
                    self._config['RSC'][k] = v
                    changed = True

        if changed:
            try:
                self._config.write()
            except Exception as exc:
                print(f'Error updating _mktxp.conf [RSC] section: {exc}')

        return dict(self._config['RSC'])

    def rsc_config(self):
        """Returns the [RSC] configuration dict from _mktxp.conf, dynamically injecting missing keys."""
        if hasattr(self, '_config') and self._config is not None:
            return self._rsc_config_reader()
        return {}

    def _diag_template(self):
        try:
            ref = importlib.resources.files('mktxp') / 'cli/config/_mktxp.conf'
            with importlib.resources.as_file(ref) as path:
                template_conf = ConfigObj(str(path), indent_type='    ', encoding='utf-8')
                return template_conf.get('DIAG', {})
        except Exception:
            return {
                'low_signal_threshold': -75,
                'min_signal_threshold': -60,
                'low_rate_threshold': '18M',
                'recent_duration': '15m',
                'top_connections_count': 10,
                'rate_above_threshold': '1M',
                'degraded_threshold': '100M',
            }

    def _diag_config_reader(self):
        template_diag = self._diag_template()
        changed = False

        if 'DIAG' not in self._config:
            self._config['DIAG'] = {}
            for k, v in template_diag.items():
                self._config['DIAG'][k] = v
            changed = True
        else:
            for k, v in template_diag.items():
                if k not in self._config['DIAG']:
                    self._config['DIAG'][k] = v
                    changed = True

        if changed:
            try:
                self._config.write()
            except Exception as exc:
                print(f'Error updating _mktxp.conf [DIAG] section: {exc}')

        return dict(self._config['DIAG'])

    def diag_config(self):
        """Returns the [DIAG] configuration dict from _mktxp.conf, dynamically injecting missing keys."""
        if hasattr(self, '_config') and self._config is not None:
            return self._diag_config_reader()
        return {
            'low_signal_threshold': -75,
            'min_signal_threshold': -60,
            'low_rate_threshold': '18M',
            'recent_duration': '15m',
            'top_connections_count': 10,
            'rate_above_threshold': '1M',
            'degraded_threshold': '100M',
        }

    def _read_from_disk(self):
        self.config = ConfigObj(self.usr_conf_data_path, indent_type='    ', encoding='utf-8')
        self.config.preserve_comments = True

        self._config = ConfigObj(self.mktxp_conf_path, indent_type='    ', encoding='utf-8')
        self._config.preserve_comments = True

    def _create_os_path(self, os_path, resource_path):
        if not os.path.exists(os_path):
            ref = importlib.resources.files('mktxp') / resource_path
            with importlib.resources.as_file(ref) as path:
                shutil.copy(path, os_path)

    def _system_entry_reader(self):
        system_entry_reader = {}
        entry_name = MKTXPConfigKeys.MKTXP_CONFIG_ENTRY_NAME
        new_keys, new_keys_values = [], {}

        if not self._config.get(MKTXPConfigKeys.MKTXP_CONFIG_ENTRY_NAME):
            self._config[MKTXPConfigKeys.MKTXP_CONFIG_ENTRY_NAME] = {}
        if not self._config.get(MKTXPConfigKeys.MKTXP_LATEST_SYSTEM_ENTRY_KEY):
            self._config[MKTXPConfigKeys.MKTXP_LATEST_SYSTEM_ENTRY_KEY] = {}

        for key in MKTXPConfigKeys.MKTXP_INT_KEYS:
            if self._config[entry_name].get(key):
                system_entry_reader[key] = self._config[entry_name].as_int(key)
            elif self._config[MKTXPConfigKeys.MKTXP_LATEST_SYSTEM_ENTRY_KEY].get(key):
                system_entry_reader[key] = self._config[
                    MKTXPConfigKeys.MKTXP_LATEST_SYSTEM_ENTRY_KEY
                ].as_int(key)
            else:
                system_entry_reader[key] = self._default_value_for_key(key)
                if key not in (MKTXPConfigKeys.PORT_KEY):
                    new_keys.append(key)
                    new_keys_values[key] = system_entry_reader[key]

        for key in MKTXPConfigKeys.SYSTEM_BOOLEAN_KEYS_NO.union(
            MKTXPConfigKeys.SYSTEM_BOOLEAN_KEYS_YES
        ):
            if self._config[entry_name].get(key) is not None:
                system_entry_reader[key] = self._config[entry_name].as_bool(key)
            elif (
                self._config[MKTXPConfigKeys.MKTXP_LATEST_SYSTEM_ENTRY_KEY].get(key)
                is not None
            ):
                system_entry_reader[key] = self._config[
                    MKTXPConfigKeys.MKTXP_LATEST_SYSTEM_ENTRY_KEY
                ].as_bool(key)
            else:
                system_entry_reader[key] = (
                    True
                    if key in MKTXPConfigKeys.SYSTEM_BOOLEAN_KEYS_YES
                    else False
                )
                new_keys.append(key)
                new_keys_values[key] = system_entry_reader[key]

        for key in MKTXPConfigKeys.MKTXP_STR_KEYS:
            if self._config[entry_name].get(key):
                system_entry_reader[key] = self._config[entry_name].get(key)
            elif self._config[MKTXPConfigKeys.MKTXP_LATEST_SYSTEM_ENTRY_KEY].get(key):
                system_entry_reader[key] = self._config[
                    MKTXPConfigKeys.MKTXP_LATEST_SYSTEM_ENTRY_KEY
                ].get(key)
            else:
                system_entry_reader[key] = self._default_value_for_key(key)
                new_keys.append(key)
                new_keys_values[key] = system_entry_reader[key]

        if self._config[entry_name].get(MKTXPConfigKeys.LISTEN_KEY):
            system_entry_reader[MKTXPConfigKeys.LISTEN_KEY] = self._config[entry_name].get(
                MKTXPConfigKeys.LISTEN_KEY
            )
        elif self._config[MKTXPConfigKeys.MKTXP_LATEST_SYSTEM_ENTRY_KEY].get(
            MKTXPConfigKeys.LISTEN_KEY
        ):
            system_entry_reader[MKTXPConfigKeys.LISTEN_KEY] = self._config[
                MKTXPConfigKeys.MKTXP_LATEST_SYSTEM_ENTRY_KEY
            ].get(MKTXPConfigKeys.LISTEN_KEY)
        else:
            system_entry_reader[MKTXPConfigKeys.LISTEN_KEY] = (
                f'0.0.0.0:{system_entry_reader.get(MKTXPConfigKeys.PORT_KEY, MKTXPConfigKeys.DEFAULT_MKTXP_PORT)}'
            )
            new_keys.append(MKTXPConfigKeys.LISTEN_KEY)
            new_keys_values[MKTXPConfigKeys.LISTEN_KEY] = system_entry_reader[
                MKTXPConfigKeys.LISTEN_KEY
            ]

        if new_keys:
            self._config[MKTXPConfigKeys.MKTXP_LATEST_SYSTEM_ENTRY_KEY].update(
                new_keys_values
            )
            self._config.comments[MKTXPConfigKeys.MKTXP_LATEST_SYSTEM_ENTRY_KEY] = [
                '',
                '# The section below contains the latest system parameters introduced by MKTXP',
                f'# For organizational purposes, you can move these parameters to the [{MKTXPConfigKeys.MKTXP_CONFIG_ENTRY_NAME}] section',
            ]
            try:
                self._config[entry_name].pop(MKTXPConfigKeys.PORT_KEY, None)
                self._config.write()
                if self._config[entry_name].as_bool(
                    MKTXPConfigKeys.MKTXP_VERBOSE_MODE
                ):
                    print(
                        f'Updated system entry {entry_name} with new system keys {new_keys}'
                    )
            except Exception as exc:
                print(
                    f'Error updating system entry {entry_name} with new system keys {new_keys}: {exc}'
                )
                print('Please update _mktxp.conf to its latest version manually')

        return system_entry_reader

    def _config_entry_reader(self, entry_name):
        config_entry_reader = {}
        compact_config = self.system_entry.compact_default_conf_values
        drop_keys = []

        for key in MKTXPConfigKeys.BOOLEAN_KEYS_NO.union(
            MKTXPConfigKeys.BOOLEAN_KEYS_YES
        ):
            if self.config[entry_name].get(key) is not None:
                config_entry_reader[key] = self.config[entry_name].as_bool(key)
                if (
                    compact_config
                    and config_entry_reader[key]
                    == self.default_config_entry_reader[key]
                ):
                    drop_keys.append(key)
            else:
                config_entry_reader[key] = self.default_config_entry_reader[key]

        for key in MKTXPConfigKeys.STR_KEYS:
            if self.config[entry_name].get(key):
                config_entry_reader[key] = self.config[entry_name].get(key)
                if (
                    key is MKTXPConfigKeys.PASSWD_KEY
                    and type(config_entry_reader[key]) is list
                ):
                    config_entry_reader[key] = ','.join(config_entry_reader[key])

                if (
                    compact_config
                    and config_entry_reader[key]
                    == self.default_config_entry_reader[key]
                ):
                    drop_keys.append(key)
            else:
                config_entry_reader[key] = self.default_config_entry_reader[key]

        for key in MKTXPConfigKeys.INT_KEYS:
            if self.config[entry_name].get(key):
                config_entry_reader[key] = self.config[entry_name].as_int(key)
                if (
                    compact_config
                    and config_entry_reader[key]
                    == self.default_config_entry_reader[key]
                ):
                    drop_keys.append(key)
            else:
                config_entry_reader[key] = self.default_config_entry_reader[key]

        if self.config[entry_name].get(MKTXPConfigKeys.PORT_KEY):
            config_entry_reader[MKTXPConfigKeys.PORT_KEY] = self.config[
                entry_name
            ].as_int(MKTXPConfigKeys.PORT_KEY)
            if (
                compact_config
                and config_entry_reader[MKTXPConfigKeys.PORT_KEY]
                == self.default_config_entry_reader[MKTXPConfigKeys.PORT_KEY]
            ):
                drop_keys.append(MKTXPConfigKeys.PORT_KEY)
        else:
            config_entry_reader[MKTXPConfigKeys.PORT_KEY] = (
                self.default_config_entry_reader[MKTXPConfigKeys.PORT_KEY]
            )

        if drop_keys and compact_config:
            for key in drop_keys:
                self.config[entry_name].pop(key, None)
            try:
                self.config.write()
                if self._config[
                    MKTXPConfigKeys.MKTXP_CONFIG_ENTRY_NAME
                ].as_bool(MKTXPConfigKeys.MKTXP_VERBOSE_MODE):
                    print(
                        f'compacted router entry {entry_name} for default values of the feature keys {drop_keys}'
                    )
            except Exception as exc:
                print(
                    f'Error compacting router entry {entry_name} for default values of feature keys {drop_keys}: {exc}'
                )
                print('Please compact mktxp.conf manually')

        return config_entry_reader

    def _default_config_entry_reader(self):
        default_config_entry_reader = {}
        new_keys, new_keys_values = [], {}
        created_latest_section = False

        if not self.config.get(MKTXPConfigKeys.DEFAULT_ENTRY_KEY):
            self.config[MKTXPConfigKeys.DEFAULT_ENTRY_KEY] = {}
        if not self.config.get(MKTXPConfigKeys.MKTXP_LATEST_DEFAULT_ENTRY_KEY):
            self.config[MKTXPConfigKeys.MKTXP_LATEST_DEFAULT_ENTRY_KEY] = {}
            created_latest_section = True

        migrated_entries = []
        for entry_name in list(self.config.keys()):
            if entry_name == MKTXPConfigKeys.MKTXP_LATEST_DEFAULT_ENTRY_KEY:
                continue
            if (
                self.config[entry_name].get(
                    MKTXPConfigKeys.MKTXP_USE_COMMENTS_OVER_NAMES
                )
                is not None
            ):
                legacy_value = self.config[entry_name].as_bool(
                    MKTXPConfigKeys.MKTXP_USE_COMMENTS_OVER_NAMES
                )
                new_value = 'comment' if legacy_value else 'name'
                self.config[entry_name][
                    MKTXPConfigKeys.FE_INTERFACE_NAME_FORMAT
                ] = new_value
                self.config[entry_name].pop(
                    MKTXPConfigKeys.MKTXP_USE_COMMENTS_OVER_NAMES, None
                )
                migrated_entries.append(entry_name)

        if migrated_entries:
            if (
                self.config.get(MKTXPConfigKeys.MKTXP_LATEST_DEFAULT_ENTRY_KEY)
                and len(
                    self.config[MKTXPConfigKeys.MKTXP_LATEST_DEFAULT_ENTRY_KEY]
                )
                == 0
            ):
                del self.config[MKTXPConfigKeys.MKTXP_LATEST_DEFAULT_ENTRY_KEY]

            try:
                self.config.write()
                print(
                    f'Migrated use_comments_over_names to interface_name_format for entries: {", ".join(migrated_entries)}'
                )
            except Exception as exc:
                print(
                    f'Error migrating use_comments_over_names to interface_name_format: {exc}'
                )
                print('Please update mktxp.conf manually')

        for key in MKTXPConfigKeys.BOOLEAN_KEYS_NO.union(
            MKTXPConfigKeys.BOOLEAN_KEYS_YES
        ):
            if self.config[MKTXPConfigKeys.DEFAULT_ENTRY_KEY].get(key) is not None:
                default_config_entry_reader[key] = self.config[
                    MKTXPConfigKeys.DEFAULT_ENTRY_KEY
                ].as_bool(key)
            elif (
                self.config[
                    MKTXPConfigKeys.MKTXP_LATEST_DEFAULT_ENTRY_KEY
                ].get(key)
                is not None
            ):
                default_config_entry_reader[key] = self.config[
                    MKTXPConfigKeys.MKTXP_LATEST_DEFAULT_ENTRY_KEY
                ].as_bool(key)
            else:
                default_config_entry_reader[key] = (
                    True if key in MKTXPConfigKeys.BOOLEAN_KEYS_YES else False
                )
                new_keys.append(key)
                new_keys_values[key] = default_config_entry_reader[key]

        for key in MKTXPConfigKeys.STR_KEYS:
            if (
                self.config[MKTXPConfigKeys.DEFAULT_ENTRY_KEY].get(key)
                is not None
            ):
                default_config_entry_reader[key] = self.config[
                    MKTXPConfigKeys.DEFAULT_ENTRY_KEY
                ].get(key)
            elif (
                self.config[
                    MKTXPConfigKeys.MKTXP_LATEST_DEFAULT_ENTRY_KEY
                ].get(key)
                is not None
            ):
                default_config_entry_reader[key] = self.config[
                    MKTXPConfigKeys.MKTXP_LATEST_DEFAULT_ENTRY_KEY
                ].get(key)
            else:
                default_config_entry_reader[key] = (
                    self._default_value_for_key(key)
                )
                new_keys.append(key)
                new_keys_values[key] = default_config_entry_reader[key]

        for key in MKTXPConfigKeys.INT_KEYS:
            if self.config[MKTXPConfigKeys.DEFAULT_ENTRY_KEY].get(key):
                default_config_entry_reader[key] = self.config[
                    MKTXPConfigKeys.DEFAULT_ENTRY_KEY
                ].as_int(key)
            elif self.config[
                MKTXPConfigKeys.MKTXP_LATEST_DEFAULT_ENTRY_KEY
            ].get(key):
                default_config_entry_reader[key] = self.config[
                    MKTXPConfigKeys.MKTXP_LATEST_DEFAULT_ENTRY_KEY
                ].as_int(key)
            else:
                default_config_entry_reader[key] = (
                    self._default_value_for_key(key)
                )
                new_keys.append(key)
                new_keys_values[key] = default_config_entry_reader[key]

        if self.config[MKTXPConfigKeys.DEFAULT_ENTRY_KEY].get(
            MKTXPConfigKeys.PORT_KEY
        ):
            default_config_entry_reader[MKTXPConfigKeys.PORT_KEY] = (
                self.config[MKTXPConfigKeys.DEFAULT_ENTRY_KEY].as_int(
                    MKTXPConfigKeys.PORT_KEY
                )
            )
        elif self.config[
            MKTXPConfigKeys.MKTXP_LATEST_DEFAULT_ENTRY_KEY
        ].get(MKTXPConfigKeys.PORT_KEY):
            default_config_entry_reader[MKTXPConfigKeys.PORT_KEY] = (
                self.config[
                    MKTXPConfigKeys.MKTXP_LATEST_DEFAULT_ENTRY_KEY
                ].as_int(MKTXPConfigKeys.PORT_KEY)
            )
        else:
            default_config_entry_reader[MKTXPConfigKeys.PORT_KEY] = (
                self._default_value_for_key(
                    MKTXPConfigKeys.SSL_KEY,
                    default_config_entry_reader[MKTXPConfigKeys.SSL_KEY],
                )
            )
            new_keys.append(MKTXPConfigKeys.PORT_KEY)
            new_keys_values[MKTXPConfigKeys.PORT_KEY] = (
                default_config_entry_reader[MKTXPConfigKeys.PORT_KEY]
            )

        if new_keys:
            self.config[
                MKTXPConfigKeys.MKTXP_LATEST_DEFAULT_ENTRY_KEY
            ].update(new_keys_values)
            self.config.comments[
                MKTXPConfigKeys.MKTXP_LATEST_DEFAULT_ENTRY_KEY
            ] = [
                '',
                '# The section below contains the latest default parameters introduced by MKTXP',
                f'# For organizational purposes, you can move these parameters to the [{MKTXPConfigKeys.DEFAULT_ENTRY_KEY}] section',
            ]
            try:
                self.config.write()
                if self._config[
                    MKTXPConfigKeys.MKTXP_CONFIG_ENTRY_NAME
                ].as_bool(MKTXPConfigKeys.MKTXP_VERBOSE_MODE):
                    print(
                        f'Updated default router entry with new feature keys {new_keys}'
                    )
            except Exception as exc:
                print(
                    f'Error updating default router entry with new feature keys {new_keys}: {exc}'
                )
                print('Please update mktxp.conf to its latest version manually')
        else:
            if (
                created_latest_section
                and self.config.get(
                    MKTXPConfigKeys.MKTXP_LATEST_DEFAULT_ENTRY_KEY
                )
                is not None
                and len(
                    self.config[MKTXPConfigKeys.MKTXP_LATEST_DEFAULT_ENTRY_KEY]
                )
                == 0
            ):
                del self.config[MKTXPConfigKeys.MKTXP_LATEST_DEFAULT_ENTRY_KEY]

        return default_config_entry_reader

    def _default_value_for_key(self, key, value=None):
        return {
            MKTXPConfigKeys.SSL_KEY: lambda value: MKTXPConfigKeys.DEFAULT_API_SSL_PORT
            if value
            else MKTXPConfigKeys.DEFAULT_API_PORT,
            MKTXPConfigKeys.HOST_KEY: lambda _: MKTXPConfigKeys.DEFAULT_HOST_KEY,
            MKTXPConfigKeys.USER_KEY: lambda _: MKTXPConfigKeys.DEFAULT_USER_KEY,
            MKTXPConfigKeys.PASSWD_KEY: lambda _: MKTXPConfigKeys.DEFAULT_PASSWORD_KEY,
            MKTXPConfigKeys.CREDENTIALS_FILE_KEY: lambda _: MKTXPConfigKeys.DEFAULT_CREDENTIALS_FILE_KEY,
            MKTXPConfigKeys.FE_CUSTOM_LABELS_KEY: lambda _: MKTXPConfigKeys.DEFAULT_FE_CUSTOM_LABELS_KEY,
            MKTXPConfigKeys.PORT_KEY: lambda _: MKTXPConfigKeys.DEFAULT_MKTXP_PORT,
            MKTXPConfigKeys.SSL_CA_FILE: lambda _: MKTXPConfigKeys.DEFAULT_SSL_CA_FILE,
            MKTXPConfigKeys.FE_REMOTE_DHCP_ENTRY: lambda _: MKTXPConfigKeys.DEFAULT_FE_REMOTE_DHCP_ENTRY,
            MKTXPConfigKeys.FE_REMOTE_CAPSMAN_ENTRY: lambda _: MKTXPConfigKeys.DEFAULT_FE_REMOTE_CAPSMAN_ENTRY,
            MKTXPConfigKeys.FE_ADDRESS_LIST_KEY: lambda _: MKTXPConfigKeys.DEFAULT_FE_ADDRESS_LIST_KEY,
            MKTXPConfigKeys.FE_IPV6_ADDRESS_LIST_KEY: lambda _: MKTXPConfigKeys.DEFAULT_FE_IPV6_ADDRESS_LIST_KEY,
            MKTXPConfigKeys.FE_INTERFACE_NAME_FORMAT: lambda _: MKTXPConfigKeys.DEFAULT_FE_INTERFACE_NAME_FORMAT,
            MKTXPConfigKeys.MKTXP_SOCKET_TIMEOUT: lambda _: MKTXPConfigKeys.DEFAULT_MKTXP_SOCKET_TIMEOUT,
            MKTXPConfigKeys.MKTXP_INITIAL_DELAY: lambda _: MKTXPConfigKeys.DEFAULT_MKTXP_INITIAL_DELAY,
            MKTXPConfigKeys.MKTXP_MAX_DELAY: lambda _: MKTXPConfigKeys.DEFAULT_MKTXP_MAX_DELAY,
            MKTXPConfigKeys.MKTXP_INC_DIV: lambda _: MKTXPConfigKeys.DEFAULT_MKTXP_INC_DIV,
            MKTXPConfigKeys.MKTXP_BANDWIDTH_TEST_INTERVAL: lambda _: MKTXPConfigKeys.DEFAULT_MKTXP_BANDWIDTH_TEST_INTERVAL,
            MKTXPConfigKeys.MKTXP_MIN_COLLECT_INTERVAL: lambda _: MKTXPConfigKeys.DEFAULT_MKTXP_MIN_COLLECT_INTERVAL,
            MKTXPConfigKeys.MKTXP_MAX_WORKER_THREADS: lambda _: MKTXPConfigKeys.DEFAULT_MKTXP_MAX_WORKER_THREADS,
            MKTXPConfigKeys.MKTXP_MAX_SCRAPE_DURATION: lambda _: MKTXPConfigKeys.DEFAULT_MKTXP_MAX_SCRAPE_DURATION,
            MKTXPConfigKeys.MKTXP_TOTAL_MAX_SCRAPE_DURATION: lambda _: MKTXPConfigKeys.DEFAULT_MKTXP_TOTAL_MAX_SCRAPE_DURATION,
            MKTXPConfigKeys.MKTXP_PERSISTENT_DHCP_CACHE: lambda _: True,
            MKTXPConfigKeys.MKTXP_BANDWIDTH_TEST_DNS_SERVER: lambda _: MKTXPConfigKeys.DEFAULT_MKTXP_BANDWIDTH_TEST_DNS_SERVER,
            MKTXPConfigKeys.MKTXP_PROBE_CONNECTION_POOL_TTL: lambda _: MKTXPConfigKeys.DEFAULT_MKTXP_PROBE_CONNECTION_POOL_TTL,
            MKTXPConfigKeys.MKTXP_PROBE_CONNECTION_POOL_MAX_SIZE: lambda _: MKTXPConfigKeys.DEFAULT_MKTXP_PROBE_CONNECTION_POOL_MAX_SIZE,
            MKTXPConfigKeys.MKTXP_HTTP_SERVER_THREADS: lambda _: MKTXPConfigKeys.DEFAULT_MKTXP_HTTP_SERVER_THREADS,
        }[key](value)


config_handler = MKTXPConfigHandler()
