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

from collections import OrderedDict
from typing import List, Optional, Tuple
from .ast import CommandNode, SectionNode, RSCConfig
from .lexer import RSCLexer


KNOWN_COMMANDS = {
    'add', 'set', 'remove', 'enable', 'disable', 'print',
    'export', 'reset', 'comment', 'unset', 'move', 'edit'
}


class RSCParser:
    """
    Parses tokenized RouterOS statements into an AST (RSCConfig).
    """

    def __init__(self):
        self.current_path = "/"
        self.sections_dict: OrderedDict[str, SectionNode] = OrderedDict()
        self.header_comments: List[str] = []

    def parse(self, raw_text: str) -> RSCConfig:
        self.current_path = "/"
        self.sections_dict = OrderedDict()
        self.header_comments = []

        logical_lines = RSCLexer.split_logical_lines(raw_text)

        # Check for header comments before first statement
        is_first_statement = True

        for statement_text, line_no, leading_comments in logical_lines:
            tokens = RSCLexer.tokenize_statement(statement_text)
            if not tokens:
                continue

            if is_first_statement and leading_comments and not self.sections_dict:
                # Capture header comments (e.g. export header info)
                self.header_comments = list(leading_comments)
                leading_comments = []
                is_first_statement = False

            self._process_statement(statement_text, tokens, leading_comments)

        return RSCConfig(
            sections=list(self.sections_dict.values()),
            header_comments=self.header_comments
        )

    def _get_or_create_section(self, path: str, leading_comments: Optional[List[str]] = None) -> SectionNode:
        path = path.strip()
        if not path.startswith('/'):
            path = '/' + path

        if path not in self.sections_dict:
            self.sections_dict[path] = SectionNode(
                path=path,
                commands=[],
                leading_comments=leading_comments or []
            )
        elif leading_comments:
            self.sections_dict[path].leading_comments.extend(leading_comments)

        return self.sections_dict[path]

    def _process_statement(self, raw_statement: str, tokens: List[str], leading_comments: List[str]):
        first_token = tokens[0]

        # Case 1: Statement starts with '/' (context path or full command)
        if first_token.startswith('/'):
            # Find if there is a command embedded in the path
            command_idx = -1
            for idx, token in enumerate(tokens):
                if token in KNOWN_COMMANDS or token.startswith('['):
                    command_idx = idx
                    break

            if command_idx == -1:
                # Pure path switch: e.g., '/interface bridge', '/caps-man channel'
                path = " ".join(tokens)
                self.current_path = path
                self._get_or_create_section(self.current_path, leading_comments)
                return
            else:
                # Embedded path and command: e.g., '/system clock set time-zone-name=Europe/Lisbon'
                path = " ".join(tokens[:command_idx])
                self.current_path = path
                section = self._get_or_create_section(self.current_path)
                cmd_tokens = tokens[command_idx:]
                cmd_node = self._parse_command_tokens(cmd_tokens, raw_statement, leading_comments)
                section.commands.append(cmd_node)
                return

        # Case 2: Standard command under current context
        section = self._get_or_create_section(self.current_path)
        cmd_node = self._parse_command_tokens(tokens, raw_statement, leading_comments)
        section.commands.append(cmd_node)

    def _parse_command_tokens(self, tokens: List[str], raw_statement: str, leading_comments: List[str]) -> CommandNode:
        command = tokens[0]
        cmd_node = CommandNode(
            command=command,
            leading_comments=leading_comments,
            raw_line=raw_statement
        )

        idx = 1
        n = len(tokens)

        # For 'set' commands, check if there is a target or [ find ... ] expression
        if command == 'set' and idx < n:
            token = tokens[idx]
            if token.startswith('[') and token.endswith(']'):
                cmd_node.find_expr = token
                idx += 1
            elif '=' not in token:
                cmd_node.target = token
                idx += 1

        # Process remaining parameters
        while idx < n:
            token = tokens[idx]
            if '=' in token:
                # Split key and value on the first '='
                eq_pos = token.index('=')
                key = token[:eq_pos]
                val = token[eq_pos + 1:]
                cmd_node.params[key] = val
            else:
                cmd_node.flags.append(token)
            idx += 1

        return cmd_node
