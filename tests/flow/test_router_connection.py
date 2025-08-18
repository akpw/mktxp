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

import pytest
import routeros_api.api_structure
# monkey patch via importing the module
import mktxp.flow.router_connection

@pytest.mark.parametrize("input_bytes, expected_string", [
    (b'But are these differences really that small?', 'But are these differences really that small?'),  
    (b'\xe4\xbd\x86\xe6\x98\xaf\xef\xbc\x8c\xe8\xbf\x99\xe4\xba\x9b\xe5\xb7\xae\xe5\xbc\x82\xe7\x9c\x9f\xe7\x9a\x84\xe9\x82\xa3\xe4\xb9\x88\xe5\xb0\x8f\xe5\x90\x97\xef\xbc\x9f', '但是，这些差异真的那么小吗？'),  
    (b'Mas ser\xc3\xa3o estas diferen\xc3\xa7as assim t\xc3\xa3o pequenas?', 'Mas serão estas diferenças assim tão pequenas?'),  
    (b'\xd0\x9d\xd0\xbe \xd0\xb4\xd0\xb5\xd0\xb9\xd1\x81\xd1\x82\xd0\xb2\xd0\xb8\xd1\x82\xd0\xb5\xd0\xbb\xd1\x8c\xd0\xbd\xd0\xbe \xd0\xbb\xd0\xb8 \xd1\x8d\xd1\x82\xd0\xb8 \xd1\x80\xd0\xb0\xd0\xb7\xd0\xbb\xd0\xb8\xd1\x87\xd0\xb8\xd1\x8f \xd1\x82\xd0\xb0\xd0\xba \xd0\xbc\xd0\xb0\xd0\xbb\xd1\x8b?', 'Но действительно ли эти различия так малы?'),  
    (b'\xd0\x90\xd0\xbb\xd0\xb5 \xd1\x87\xd0\xb8 \xd1\x81\xd0\xbf\xd1\x80\xd0\xb0\xd0\xb2\xd0\xb4\xd1\x96 \xd1\x86\xd1\x96 \xd0\xb2\xd1\x96\xd0\xb4\xd0\xbc\xd1\x96\xd0\xbd\xd0\xbd\xd0\xbe\xd1\x81\xd1\x82\xd1\x96 \xd1\x82\xd0\xb0\xd0\xba\xd1\x96 \xd0\xbd\xd0\xb5\xd0\xb7\xd0\xbd\xd0\xb0\xd1\x87\xd0\xbd\xd1\x96?', 'Але чи справді ці відмінності такі незначні?'),  
    (b'Jsou v\xc5\xa1ak tyto rozd\xc3\xadly opravdu tak mal\xc3\xa9?', 'Jsou však tyto rozdíly opravdu tak malé?'),  
    (b'\xa1\xa3', '¡£'),  # Some latin-1 characters
    (b'J\xf6rgensen', 'Jörgensen'),
    (b'fran\xe7aise', 'française'),
    (b'espa\xf1ol', 'español'),
    (b'sch\xf6n', 'schön'),
    (b'mixed content \xe4\xbd\xa0\xe5\xa5\xbd', 'mixed content 你好'),
])
def test_decode_bytes_monkey_patch(input_bytes, expected_string):
    field = routeros_api.api_structure.StringField()
    assert field.get_python_value(input_bytes) == expected_string
