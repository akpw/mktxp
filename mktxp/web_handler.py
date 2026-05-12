import os
import html
import json
import sys
import collections
from datetime import datetime
from configobj import ConfigObj
from urllib.parse import parse_qs
from mktxp.cli.config.config import config_handler, log_capture

class WebUIHandler:
    def __init__(self, metrics_app):
        self.metrics_app = metrics_app
        # Path to web-ui folder (project root)
        self.ui_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'web-ui')

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '')
        if path == '/':
            return self._handle_ui(environ, start_response)
        elif path == '/save' and environ.get('REQUEST_METHOD') == 'POST':
            return self._handle_save(environ, start_response)
        elif path == '/logs':
            return self._handle_logs(environ, start_response)
        elif path == '/restart' and environ.get('REQUEST_METHOD') == 'POST':
            return self._handle_restart(environ, start_response)
        elif path.startswith('/static/'):
            return self._handle_static(environ, start_response)
        
        # Fallback to original metrics router
        return self.metrics_app(environ, start_response)

    def _handle_ui(self, environ, start_response):
        try:
            with open(os.path.join(self.ui_path, 'index.html'), 'r', encoding='utf-8') as f:
                content = f.read()

            # Read configs
            with open(config_handler.usr_conf_data_path, 'r', encoding='utf-8') as f:
                mktxp_conf = f.read()
            with open(config_handler.mktxp_conf_path, 'r', encoding='utf-8') as f:
                system_conf = f.read()

            # Parse configs for Visual Editor
            config_obj = ConfigObj(config_handler.usr_conf_data_path, encoding='utf-8')
            parsed_data = {}
            for section in config_obj.sections:
                parsed_data[section] = dict(config_obj[section])

            # Simple injection
            content = content.replace('{{MKTXP_CONF}}', html.escape(mktxp_conf))
            content = content.replace('{{MKTXP_DATA_JSON}}', json.dumps(parsed_data))
            content = content.replace('{{MKTXP_CONF_ESCAPED}}', mktxp_conf.replace('`', '\\`'))
            content = content.replace('{{SYSTEM_CONF_ESCAPED}}', system_conf.replace('`', '\\`'))

            body = content.encode('utf-8')
            start_response('200 OK', [
                ('Content-Type', 'text/html; charset=utf-8'),
                ('Content-Length', str(len(body))),
                ('Cache-Control', 'no-cache, no-store, must-revalidate'),
                ('Pragma', 'no-cache'),
                ('Expires', '0')
            ])
            return [body]
        except Exception as exc:
            return self._error(start_response, f"UI error: {exc}")

    def _handle_save(self, environ, start_response):
        try:
            length = int(environ.get('CONTENT_LENGTH', '0'))
            body = environ['wsgi.input'].read(length)
            params = parse_qs(body.decode('utf-8'))
            
            config_type = params.get('config_type', [''])[0]
            config_content = params.get('config_content', [''])[0]

            if config_type and config_content:
                target_path = config_handler.usr_conf_data_path if config_type == 'mktxp' else config_handler.mktxp_conf_path
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(config_content)
                config_handler._read_from_disk()
                
                start_response('200 OK', [('Content-Type', 'text/plain')])
                return [b'OK']
            
            return self._error(start_response, "Invalid save request")
        except Exception as exc:
            return self._error(start_response, f"Save error: {exc}")

    def _handle_logs(self, environ, start_response):
        try:
            logs = log_capture.get_logs()
            body = logs.encode('utf-8')
            start_response('200 OK', [
                ('Content-Type', 'text/plain; charset=utf-8'),
                ('Content-Length', str(len(body))),
                ('Cache-Control', 'no-cache, no-store, must-revalidate')
            ])
            return [body]
        except Exception as exc:
            return self._error(start_response, f"Logs error: {exc}")

    def _handle_restart(self, environ, start_response):
        try:
            import threading
            import time
            
            def do_restart():
                time.sleep(0.5)  # Give some time for the response to reach the client
                os.execv(sys.executable, [sys.executable] + sys.argv)
            
            threading.Thread(target=do_restart).start()
            
            body = b'OK'
            start_response('200 OK', [
                ('Content-Type', 'text/plain'),
                ('Content-Length', str(len(body)))
            ])
            return [body]
        except Exception as exc:
            return self._error(start_response, f"Restart error: {exc}")

    def _handle_static(self, environ, start_response):
        filename = environ.get('PATH_INFO', '').split('/')[-1]
        content_type = 'text/plain'
        if filename.endswith('.css'): content_type = 'text/css'
        elif filename.endswith('.js'): content_type = 'application/javascript'

        try:
            file_path = os.path.join(self.ui_path, filename)
            with open(file_path, 'rb') as f:
                body = f.read()
            
            start_response('200 OK', [
                ('Content-Type', content_type),
                ('Content-Length', str(len(body))),
                ('Cache-Control', 'no-cache, no-store, must-revalidate'),
                ('Pragma', 'no-cache'),
                ('Expires', '0')
            ])
            return [body]
        except Exception as exc:
            start_response('404 Not Found', [('Content-Type', 'text/plain')])
            return [b'Not Found']

    def _error(self, start_response, message):
        body = f'Error: {message}\n'.encode('utf-8')
        start_response('500 Internal Server Error', [
            ('Content-Type', 'text/plain; charset=utf-8'),
            ('Content-Length', str(len(body)))
        ])
        return [body]
