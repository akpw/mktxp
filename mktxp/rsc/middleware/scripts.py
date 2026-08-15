# coding=utf8
## Copyright (c) 2026 Arseniy Kuznetsov
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
from typing import Optional
from mktxp.rsc.ast import RSCConfig, ScriptNode, CommandNode
from .base import BaseMiddleware


class ScriptExtractor(BaseMiddleware):
    """
    Extracts multi-line / complex inline scripts under /system script into clean, standalone
    .rsc files for readability in Git, replacing their AST node with a readable pointer note.
    """

    def __init__(self, enabled: bool = True):
        self.enabled = enabled

    def process(self, config: RSCConfig) -> RSCConfig:
        if not self.enabled:
            return config

        for section in config.sections:
            if section.path.strip() != '/system script':
                continue

            new_commands = []
            for cmd in section.commands:
                if cmd.command == 'add' and 'source' in cmd.params and 'name' in cmd.params:
                    script_name = cmd.params['name'].strip('"\'')
                    source_val = cmd.params['source']

                    # Check if this script should be extracted
                    # e.g., if source has '# Script:' header or is a multi-line script (> 300 chars or > 5 logical lines)
                    if self._should_extract(script_name, source_val):
                        unescaped_code = self._unescape_source(source_val)
                        script_node = ScriptNode(
                            name=script_name,
                            source_code=unescaped_code,
                            original_command=cmd.clone()
                        )
                        config.extracted_scripts.append(script_node)

                        # Replace AST node with note comment
                        note_cmd = CommandNode(
                            command='',
                            note_comment=f"# Note: {script_name} script source is exported to {script_name}.rsc in this directory"
                        )
                        new_commands.append(note_cmd)
                        continue

                new_commands.append(cmd)

            section.commands = new_commands

        return config

    def _should_extract(self, script_name: str, source_val: str) -> bool:
        # When extract_scripts is enabled, extract any script with a non-empty source body
        cleaned = source_val.strip('"\'')
        return bool(cleaned)

    @staticmethod
    def _unescape_source(source_str: str) -> str:
        """
        Unescapes RouterOS string literal escapes:
        \\n -> newline
        \\_ -> space
        \\$ -> $
        \\" -> "
        \\\\ -> \\
        """
        # Strip outer quotes if present
        text = source_str
        if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
            text = text[1:-1]

        # Handle carriage returns
        text = text.replace('\r\n', '\n').replace('\\r\\n', '\n').replace('\\r', '')
        # Replace escaped newlines
        text = text.replace('\\n', '\n')
        # Replace escaped spaces
        text = text.replace('\\_', ' ')
        # Replace escaped dollar signs
        text = text.replace('\\$', '$')
        # Replace escaped quotes
        text = text.replace('\\"', '"')
        # Replace escaped semicolons if any
        text = text.replace('\\;', ';')
        # Replace escaped backslashes
        text = text.replace('\\\\', '\\')

        if not text.endswith('\n'):
            text += '\n'

        return text
