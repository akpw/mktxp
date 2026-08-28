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

from unittest.mock import MagicMock
from io import BytesIO
from mktxp.exporter.router import MetricsRouter
from mktxp.exporter.middleware import PrometheusHeadersDeduplicatingMiddleware
from mktxp.exporter.server import ExportProcessor


def _call_wsgi_app(app, path='/', method='GET', query_string=''):
    """Helper to call WSGI app without external test dependencies."""
    status_and_headers = {}

    def start_response(status, headers):
        status_and_headers['status'] = status
        status_and_headers['headers'] = headers

    environ = {
        'REQUEST_METHOD': method,
        'PATH_INFO': path,
        'QUERY_STRING': query_string,
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '80',
        'wsgi.version': (1, 0),
        'wsgi.input': BytesIO(b''),
        'wsgi.errors': BytesIO(),
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
    }

    body_chunks = app(environ, start_response)
    body = b''.join(body_chunks)
    return status_and_headers.get('status', ''), status_and_headers.get('headers', []), body


def test_metrics_router_metrics_endpoint():
    """Verify /metrics route delegates to wrapped metrics_app."""
    def dummy_metrics_app(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return [b'mktxp_metric 1\n']

    app = MetricsRouter(dummy_metrics_app)
    status, headers, body = _call_wsgi_app(app, '/metrics')
    assert '200 OK' in status
    assert b'mktxp_metric 1' in body


def test_metrics_router_probe_missing_module():
    """Verify /probe returns error when missing module parameter."""
    def dummy_metrics_app(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return [b'ok']

    app = MetricsRouter(dummy_metrics_app)
    status, headers, body = _call_wsgi_app(app, '/probe')
    assert '503 Service Unavailable' in status
    assert b"Missing or invalid 'module' parameter" in body


def test_middleware_deduplication():
    """Verify middleware deduplicates repeated HELP and TYPE comment lines."""
    def dummy_app(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/plain; charset=utf-8')])
        return [
            b'# HELP test_metric A test\n',
            b'# TYPE test_metric gauge\n',
            b'test_metric{label="a"} 1\n',
            b'# HELP test_metric A test\n',
            b'# TYPE test_metric gauge\n',
            b'test_metric{label="b"} 2\n',
        ]

    wrapped_app = PrometheusHeadersDeduplicatingMiddleware(dummy_app)
    status, headers, body = _call_wsgi_app(wrapped_app, '/metrics')
    assert '200 OK' in status

    lines = body.decode('utf-8').splitlines()
    assert lines.count('# HELP test_metric A test') == 1
    assert lines.count('# TYPE test_metric gauge') == 1
    assert 'test_metric{label="a"} 1' in lines
    assert 'test_metric{label="b"} 2' in lines


def test_export_processor_exists():
    """Verify ExportProcessor has start method."""
    assert hasattr(ExportProcessor, 'start')
    assert callable(ExportProcessor.start)
