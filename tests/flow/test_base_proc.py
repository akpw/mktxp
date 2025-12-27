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
from mktxp.flow.processor.base_proc import MetricsRouter, PrometheusHeadersDeduplicatingMiddleware

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


def test_metrics_router_passthrough():
    def metrics_app(environ, start_response):
        start_response('200 OK', [('Content-Length', '2')])
        return [b'ok']

    router = MetricsRouter(metrics_app)
    status_headers = []

    def start_response(status, headers):
        status_headers.append((status, headers))

    body = b''.join(router({'PATH_INFO': '/metrics'}, start_response))

    assert status_headers[0][0] == '200 OK'
    assert body == b'ok'


def test_probe_missing_module_returns_503():
    router = MetricsRouter(lambda environ, start_response: [])
    status_headers = []

    def start_response(status, headers):
        status_headers.append((status, headers))

    body = b''.join(router({'PATH_INFO': '/probe', 'QUERY_STRING': ''}, start_response))

    assert status_headers[0][0].startswith('503')
    assert b'Missing or invalid' in body


def test_probe_unknown_module_returns_503(monkeypatch):
    from mktxp.flow.processor import base_proc

    class DummyConfigHandler:
        def registered_entry(self, name):
            return None

    monkeypatch.setattr(base_proc, 'config_handler', DummyConfigHandler())

    router = base_proc.MetricsRouter(lambda environ, start_response: [])
    status_headers = []

    def start_response(status, headers):
        status_headers.append((status, headers))

    body = b''.join(router({'PATH_INFO': '/probe', 'QUERY_STRING': 'module=missing'}, start_response))

    assert status_headers[0][0].startswith('503')
    assert b'Unknown module' in body


def test_probe_disabled_module_returns_503(monkeypatch):
    from mktxp.flow.processor import base_proc

    class DummyEntry:
        enabled = False
        module_only = False

    class DummyConfigHandler:
        def registered_entry(self, name):
            return True

        def config_entry(self, name):
            return DummyEntry()

    monkeypatch.setattr(base_proc, 'config_handler', DummyConfigHandler())

    router = base_proc.MetricsRouter(lambda environ, start_response: [])
    status_headers = []

    def start_response(status, headers):
        status_headers.append((status, headers))

    body = b''.join(router({'PATH_INFO': '/probe', 'QUERY_STRING': 'module=disabled'}, start_response))

    assert status_headers[0][0].startswith('503')
    assert b'is disabled' in body


def test_probe_valid_module_uses_probe_app(monkeypatch):
    from mktxp.flow.processor import base_proc

    class DummyEntry:
        enabled = True
        hostname = 'original'
        module_only = False

        def _replace(self, **kwargs):
            entry = DummyEntry()
            for key, value in kwargs.items():
                setattr(entry, key, value)
            return entry

    class DummyConfigHandler:
        def registered_entry(self, name):
            return True

        def config_entry(self, name):
            return DummyEntry()

    class DummyRegistry:
        def __init__(self):
            self.registered = []

        def register(self, collector):
            self.registered.append(collector)

    class DummyCollectorHandler:
        def __init__(self, entries_handler, collector_registry):
            self.entries_handler = entries_handler
            self.collector_registry = collector_registry

    class DummyEntriesHandler:
        def __init__(self, modules=None, config_overrides=None):
            self.modules = modules
            self.config_overrides = config_overrides or {}

    class DummyCollectorRegistry:
        pass

    def probe_app(environ, start_response):
        start_response('200 OK', [('Content-Length', '2')])
        return [b'ok']

    captured = {}

    def fake_make_wsgi_app(registry=None):
        captured['registry'] = registry
        return probe_app

    monkeypatch.setattr(base_proc, 'config_handler', DummyConfigHandler())
    monkeypatch.setattr(base_proc, 'PrometheusCollectorRegistry', DummyRegistry)
    monkeypatch.setattr(base_proc, 'CollectorHandler', DummyCollectorHandler)
    monkeypatch.setattr(base_proc, 'RouterEntriesHandler', DummyEntriesHandler)
    monkeypatch.setattr(base_proc, 'MKTXPCollectorRegistry', DummyCollectorRegistry)
    monkeypatch.setattr(base_proc, 'make_wsgi_app', fake_make_wsgi_app)

    router = base_proc.MetricsRouter(lambda environ, start_response: [])
    status_headers = []

    def start_response(status, headers):
        status_headers.append((status, headers))

    body = b''.join(router({'PATH_INFO': '/probe', 'QUERY_STRING': 'module=router1'}, start_response))

    assert status_headers[0][0] == '200 OK'
    assert body == b'ok'
    assert captured['registry'].registered
    handler = captured['registry'].registered[0]
    assert handler.entries_handler.modules == ['router1']
    assert handler.entries_handler.config_overrides == {}


def test_probe_target_override_applies_hostname(monkeypatch):
    from mktxp.flow.processor import base_proc

    class DummyEntry:
        enabled = True
        hostname = 'original'
        module_only = False

        def _replace(self, **kwargs):
            entry = DummyEntry()
            for key, value in kwargs.items():
                setattr(entry, key, value)
            return entry

    class DummyConfigHandler:
        def registered_entry(self, name):
            return True

        def config_entry(self, name):
            return DummyEntry()

    class DummyRegistry:
        def __init__(self):
            self.registered = []

        def register(self, collector):
            self.registered.append(collector)

    class DummyCollectorHandler:
        def __init__(self, entries_handler, collector_registry):
            self.entries_handler = entries_handler
            self.collector_registry = collector_registry

    class DummyEntriesHandler:
        def __init__(self, modules=None, config_overrides=None):
            self.modules = modules
            self.config_overrides = config_overrides or {}

    class DummyCollectorRegistry:
        pass

    def probe_app(environ, start_response):
        start_response('200 OK', [('Content-Length', '2')])
        return [b'ok']

    captured = {}

    def fake_make_wsgi_app(registry=None):
        captured['registry'] = registry
        return probe_app

    monkeypatch.setattr(base_proc, 'config_handler', DummyConfigHandler())
    monkeypatch.setattr(base_proc, 'PrometheusCollectorRegistry', DummyRegistry)
    monkeypatch.setattr(base_proc, 'CollectorHandler', DummyCollectorHandler)
    monkeypatch.setattr(base_proc, 'RouterEntriesHandler', DummyEntriesHandler)
    monkeypatch.setattr(base_proc, 'MKTXPCollectorRegistry', DummyCollectorRegistry)
    monkeypatch.setattr(base_proc, 'make_wsgi_app', fake_make_wsgi_app)

    router = base_proc.MetricsRouter(lambda environ, start_response: [])
    status_headers = []

    def start_response(status, headers):
        status_headers.append((status, headers))

    body = b''.join(router({'PATH_INFO': '/probe', 'QUERY_STRING': 'module=router1&target=1.2.3.4'}, start_response))

    assert status_headers[0][0] == '200 OK'
    assert body == b'ok'
    handler = captured['registry'].registered[0]
    assert handler.entries_handler.config_overrides['router1'].hostname == '1.2.3.4'


def test_probe_module_only_requires_target(monkeypatch):
    from mktxp.flow.processor import base_proc

    class DummyEntry:
        enabled = True
        module_only = True

    class DummyConfigHandler:
        def registered_entry(self, name):
            return True

        def config_entry(self, name):
            return DummyEntry()

    monkeypatch.setattr(base_proc, 'config_handler', DummyConfigHandler())

    router = base_proc.MetricsRouter(lambda environ, start_response: [])
    status_headers = []

    def start_response(status, headers):
        status_headers.append((status, headers))

    body = b''.join(router({'PATH_INFO': '/probe', 'QUERY_STRING': 'module=template'}, start_response))

    assert status_headers[0][0].startswith('503')
    assert b'requires a target override' in body


def test_probe_empty_target_returns_503(monkeypatch):
    from mktxp.flow.processor import base_proc

    class DummyEntry:
        enabled = True
        module_only = False

    class DummyConfigHandler:
        def registered_entry(self, name):
            return True

        def config_entry(self, name):
            return DummyEntry()

    monkeypatch.setattr(base_proc, 'config_handler', DummyConfigHandler())

    router = base_proc.MetricsRouter(lambda environ, start_response: [])
    status_headers = []

    def start_response(status, headers):
        status_headers.append((status, headers))

    body = b''.join(router({'PATH_INFO': '/probe', 'QUERY_STRING': 'module=router1&target='}, start_response))

    assert status_headers[0][0].startswith('503')
    assert b"Invalid 'target' parameter" in body
