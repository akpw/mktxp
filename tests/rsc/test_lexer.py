# coding=utf8
import pytest
from mktxp.rsc.lexer import RSCLexer


def test_split_logical_lines_simple():
    raw = """
# Header comment
/interface bridge
add name=bridge1
add name=bridge2
"""
    logical = RSCLexer.split_logical_lines(raw)
    assert len(logical) == 3
    assert logical[0][0] == "/interface bridge"
    assert logical[1][0] == "add name=bridge1"
    assert logical[2][0] == "add name=bridge2"


def test_split_logical_lines_continuation():
    raw = """
/interface bridge
add comment="Bridge with long \\
    comment" frame-types=\\
    admit-only-vlan-tagged name=br1
"""
    logical = RSCLexer.split_logical_lines(raw)
    assert len(logical) == 2
    assert logical[0][0] == "/interface bridge"
    assert logical[1][0] == 'add comment="Bridge with long comment" frame-types=admit-only-vlan-tagged name=br1'


def test_tokenize_statement_quotes_and_brackets():
    stmt = 'set [ find default-name=ether1 ] comment="Trunk to MKT GT" l2mtu=1598 mac-address=DC:2C:6E:13:58:2E'
    tokens = RSCLexer.tokenize_statement(stmt)
    assert tokens[0] == 'set'
    assert tokens[1] == '[ find default-name=ether1 ]'
    assert tokens[2] == 'comment="Trunk to MKT GT"'
    assert tokens[3] == 'l2mtu=1598'
    assert tokens[4] == 'mac-address=DC:2C:6E:13:58:2E'


def test_tokenize_statement_escaped_quotes_inside_string():
    stmt = 'add name=script1 source="/system backup;\\ndelay 2s;\\n:log info \\"Done\\";"'
    tokens = RSCLexer.tokenize_statement(stmt)
    assert tokens[0] == 'add'
    assert tokens[1] == 'name=script1'
    assert tokens[2] == 'source="/system backup;\\ndelay 2s;\\n:log info \\"Done\\";"'
