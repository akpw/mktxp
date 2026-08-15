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

from typing import List, Optional
from .ast import CommandNode, SectionNode, RSCConfig


class RSCFormatter:
    """
    Formats AST sections and commands back to RouterOS .rsc syntax.
    Supports deterministic line-wrapping, section headers, and comments.
    """

    def __init__(self, wrap_lines: bool = False, wrap_col: int = 80, add_section_headers: bool = True):
        self.wrap_lines = wrap_lines
        self.wrap_col = wrap_col
        self.add_section_headers = add_section_headers

    def format_config(self, config: RSCConfig, include_header_comments: bool = False) -> str:
        lines: List[str] = []

        if include_header_comments and config.header_comments:
            for hc in config.header_comments:
                lines.append(hc)
            if lines and lines[-1] != '':
                lines.append('')

        for section in config.sections:
            sec_str = self.format_section(section)
            if sec_str:
                lines.append(sec_str)

        return "\n\n".join(lines).rstrip() + "\n"

    def format_section(self, section: SectionNode) -> str:
        if not section.commands and not section.leading_comments:
            return ""

        lines: List[str] = []

        # Optional section leading comments
        for lc in section.leading_comments:
            lines.append(lc)

        # Standardized Section Header
        if self.add_section_headers:
            lines.append(f"# Section: {section.path}")

        # Path declaration
        lines.append(section.path)

        # Commands under this section
        for cmd in section.commands:
            cmd_str = self.format_command(cmd)
            if cmd_str:
                lines.append(cmd_str)

        return "\n".join(lines)

    def format_command(self, cmd: CommandNode) -> str:
        if cmd.note_comment:
            return cmd.note_comment

        lines: List[str] = []

        # Leading comments attached to this command
        for lc in cmd.leading_comments:
            lines.append(lc)

        # Build tokens
        tokens: List[str] = [cmd.command]

        if cmd.find_expr:
            tokens.append(cmd.find_expr)
        elif cmd.target:
            tokens.append(cmd.target)

        for k, v in cmd.params.items():
            tokens.append(f"{k}={v}")

        for flag in cmd.flags:
            tokens.append(flag)

        if not self.wrap_lines:
            statement = " ".join(tokens)
            lines.append(statement)
        else:
            wrapped = self._wrap_tokens(tokens)
            lines.append(wrapped)

        return "\n".join(lines)

    def _wrap_tokens(self, tokens: List[str]) -> str:
        """
        Wraps tokens across multiple lines with trailing '\\' and 4-space indentation,
        targeting the configured column width.
        """
        if not tokens:
            return ""

        lines: List[str] = []
        current_line = tokens[0]

        for token in tokens[1:]:
            # Check if token can fit on current line
            potential_len = len(current_line) + 1 + len(token)
            if potential_len <= self.wrap_col:
                current_line += " " + token
            else:
                # If current token is key=value and is very long, check if we should split key=\ and value
                if "=" in token and len(token) > (self.wrap_col - 4):
                    eq_idx = token.index("=")
                    key_part = token[:eq_idx + 1]
                    val_part = token[eq_idx + 1:]
                    
                    if len(current_line) + 1 + len(key_part) <= self.wrap_col:
                        current_line += " " + key_part
                        lines.append(current_line + " \\")
                        current_line = "    " + val_part
                    else:
                        lines.append(current_line + " \\")
                        lines.append("    " + key_part + " \\")
                        current_line = "    " + val_part
                else:
                    lines.append(current_line + " \\")
                    current_line = "    " + token

        lines.append(current_line)
        return "\n".join(lines)
