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

import gzip
import pytest
from mktxp.flow.processor.base_proc import PrometheusHeadersDeduplicatingMiddleware

# A mock WSGI app to simulate the prometheus_client
def mock_app(environ, start_response):
    status = '200 OK'
    body = b'# HELP metric1 doc1\n# TYPE metric1 gauge\nmetric1{label="a"} 1\n# HELP metric1 doc1\n# TYPE metric1 gauge\nmetric1{label="b"} 2\n'
    headers = [('Content-Type', 'text/plain; version=0.0.4; charset=utf-8')]
    
    accept_encoding = environ.get('HTTP_ACCEPT_ENCODING', '')
    if 'gzip' in accept_encoding:
        headers.append(('Content-Encoding', 'gzip'))
        body = gzip.compress(body)

    headers.append(('Content-Length', str(len(body))))
    start_response(status, headers)
    return [body]

@pytest.mark.parametrize(
    "case_name, accept_encoding, expected_gzipped",
    [
        ("plain_text", "", False),
        ("gzipped", "gzip, deflate", True),
    ]
)
def test_deduplicating_middleware(case_name, accept_encoding, expected_gzipped):
    """
    Tests the Prometheus client middleware to de-duplicates HELP/TYPE headers
    Parameterized to run for both plain text and gzipped responses
    """
    middleware = PrometheusHeadersDeduplicatingMiddleware(mock_app)
    
    captured_status = []
    captured_headers = []
    def mock_start_response(status, headers):
        captured_status.append(status)
        captured_headers.append(headers)

    environ = {'HTTP_ACCEPT_ENCODING': accept_encoding}
    
    response_iter = middleware(environ, mock_start_response)
    response_body = b''.join(response_iter)

    assert captured_status[0] == '200 OK'
    
    expected_text = '# HELP metric1 doc1\n# TYPE metric1 gauge\nmetric1{label="a"} 1\nmetric1{label="b"} 2\n'
    
    headers_dict = dict(captured_headers[0])

    if expected_gzipped:
        assert gzip.decompress(response_body).decode('utf-8') == expected_text
        assert headers_dict['Content-Length'] == str(len(response_body))
        assert headers_dict['Content-Encoding'] == 'gzip'
    else:
        assert response_body.decode('utf-8') == expected_text
        assert headers_dict['Content-Length'] == str(len(expected_text.encode('utf-8')))
        assert 'Content-Encoding' not in headers_dict
