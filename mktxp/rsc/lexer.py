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
from typing import List, Tuple, Optional


class RSCLexer:
    """
    Lexer for RouterOS .rsc export scripts.
    Assembles physical lines into logical statements by resolving line continuations (`\\`),
    respecting quoted strings and comment lines.
    """

    @staticmethod
    def split_logical_lines(raw_text: str) -> List[Tuple[str, int, List[str]]]:
        """
        Takes raw .rsc text and yields logical lines.
        Each item is a tuple: (logical_line_text, start_line_no, leading_comments)
        """
        lines = raw_text.splitlines()
        logical_lines: List[Tuple[str, int, List[str]]] = []

        current_line_parts: List[str] = []
        current_leading_comments: List[str] = []
        statement_start_line = 1
        in_continuation = False

        for line_idx, line in enumerate(lines, start=1):
            stripped = line.strip()

            # Comment lines outside continuation
            if not in_continuation and (stripped.startswith('#') or stripped == ''):
                if stripped.startswith('#'):
                    current_leading_comments.append(line)
                continue

            # If we were not in continuation, this is the start of a new statement
            if not in_continuation:
                statement_start_line = line_idx
                current_line_parts = []

            # Check if this physical line ends with continuation `\`
            # Note: inside quoted strings, `\` can be continuation if at line end.
            # Let's check whether the physical line ends with `\`
            # RouterOS continuation is backslash as the last non-whitespace character
            ends_with_backslash = line.rstrip().endswith('\\')

            if ends_with_backslash:
                # Remove the trailing backslash
                trimmed = line.rstrip()[:-1]
                # If we are continuing previous parts, strip leading whitespace for the continuation line
                if in_continuation:
                    trimmed = trimmed.lstrip()
                current_line_parts.append(trimmed)
                in_continuation = True
            else:
                trimmed = line
                if in_continuation:
                    trimmed = trimmed.lstrip()
                current_line_parts.append(trimmed)
                
                # Completed logical line
                full_logical_line = "".join(current_line_parts)
                logical_lines.append((full_logical_line, statement_start_line, current_leading_comments))
                current_leading_comments = []
                current_line_parts = []
                in_continuation = False

        # In case file ended with a trailing continuation
        if current_line_parts:
            full_logical_line = "".join(current_line_parts)
            logical_lines.append((full_logical_line, statement_start_line, current_leading_comments))

        return logical_lines

    @staticmethod
    def tokenize_statement(statement: str) -> List[str]:
        """
        Tokenizes a single logical statement into atomic tokens, respecting:
        - Double-quoted strings with escape sequences: "..."
        - Bracket expressions: [ find ... ]
        - Standard whitespace-separated tokens
        """
        tokens: List[str] = []
        i = 0
        n = len(statement)

        while i < n:
            # Skip whitespace
            while i < n and statement[i].isspace():
                i += 1
            if i >= n:
                break

            char = statement[i]

            # Quoted string
            if char == '"':
                start = i
                i += 1
                while i < n:
                    if statement[i] == '\\':
                        # Skip escaped character
                        i += 2
                    elif statement[i] == '"':
                        i += 1
                        break
                    else:
                        i += 1
                tokens.append(statement[start:i])

            # Bracket expression: e.g., [ find default=yes ]
            elif char == '[':
                start = i
                bracket_depth = 1
                i += 1
                in_quote = False
                while i < n and bracket_depth > 0:
                    c = statement[i]
                    if in_quote:
                        if c == '\\':
                            i += 2
                            continue
                        elif c == '"':
                            in_quote = False
                    else:
                        if c == '"':
                            in_quote = True
                        elif c == '[':
                            bracket_depth += 1
                        elif c == ']':
                            bracket_depth -= 1
                    i += 1
                tokens.append(statement[start:i])

            # Regular token (or key=value where value might be quoted or bracketed)
            else:
                start = i
                in_quote = False
                bracket_depth = 0
                while i < n:
                    c = statement[i]
                    if in_quote:
                        if c == '\\':
                            i += 2
                            continue
                        elif c == '"':
                            in_quote = False
                    else:
                        if c == '"':
                            in_quote = True
                        elif c == '[':
                            bracket_depth += 1
                        elif c == ']':
                            bracket_depth = max(0, bracket_depth - 1)
                        elif c.isspace() and bracket_depth == 0:
                            break
                    i += 1
                tokens.append(statement[start:i])

        return tokens
