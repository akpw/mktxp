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


class PrometheusHeadersDeduplicatingMiddleware:
    """WSGI Middleware to deduplicate repeating # HELP and # TYPE lines in Prometheus output."""

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        captured_status = []
        captured_headers = []

        def custom_start_response(status, headers, exc_info=None):
            captured_status.append(status)
            captured_headers.append(headers)

        app_iter = self.app(environ, custom_start_response)
        body = b"".join(app_iter)

        response_headers = dict(captured_headers[0])
        is_gzipped = response_headers.get("Content-Encoding") == "gzip"

        if is_gzipped:
            try:
                uncompressed_body = gzip.decompress(body)
            except gzip.BadGzipFile:
                uncompressed_body = body
        else:
            uncompressed_body = body

        lines = uncompressed_body.decode("utf-8").split("\n")
        seen_headers = set()
        output_lines = []
        for line in lines:
            if line.startswith("# HELP") or line.startswith("# TYPE"):
                if line in seen_headers:
                    continue
                seen_headers.add(line)
            output_lines.append(line)

        processed_text = "\n".join(output_lines)

        if is_gzipped:
            output_body = gzip.compress(processed_text.encode("utf-8"))
        else:
            output_body = processed_text.encode("utf-8")

        status = captured_status[0]
        original_headers = captured_headers[0]

        new_headers = []
        for k, v in original_headers:
            if k.lower() == "content-length":
                new_headers.append((k, str(len(output_body))))
            else:
                new_headers.append((k, v))

        start_response(status, new_headers)
        return [output_body]
