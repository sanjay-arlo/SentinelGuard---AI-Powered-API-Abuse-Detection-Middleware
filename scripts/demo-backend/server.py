#!/usr/bin/env python3
"""
Demo backend server for testing SentinelGuard proxy functionality.
This is a simple HTTP server that responds to basic API calls.
"""

import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


class DemoBackendHandler(BaseHTTPRequestHandler):
    """Simple HTTP request handler for demo backend."""
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/health':
            self._send_json_response({
                'status': 'healthy',
                'timestamp': time.time(),
                'service': 'demo-backend'
            })
        elif parsed_path.path == '/api/users':
            self._send_json_response({
                'users': [
                    {'id': 1, 'name': 'Alice'},
                    {'id': 2, 'name': 'Bob'},
                    {'id': 3, 'name': 'Charlie'}
                ]
            })
        elif parsed_path.path == '/api/status':
            self._send_json_response({
                'status': 'ok',
                'message': 'Demo backend is running',
                'requests_served': getattr(self.server, 'request_count', 0)
            })
        else:
            self._send_error(404, 'Not Found')
    
    def do_POST(self):
        """Handle POST requests."""
        parsed_path = urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        
        if parsed_path.path == '/api/auth/login':
            try:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                # Simulate authentication
                username = data.get('username', '')
                password = data.get('password', '')
                
                if username == 'demo' and password == 'password':
                    self._send_json_response({
                        'status': 'success',
                        'token': 'demo-token-12345',
                        'user': {'id': 1, 'username': 'demo'}
                    })
                else:
                    self._send_json_response({
                        'status': 'error',
                        'message': 'Invalid credentials'
                    }, status=401)
            except (json.JSONDecodeError, UnicodeDecodeError):
                self._send_error(400, 'Invalid JSON')
        else:
            self._send_error(404, 'Not Found')
    
    def do_PUT(self):
        """Handle PUT requests."""
        self._send_json_response({
            'status': 'ok',
            'message': 'PUT request received'
        })
    
    def do_DELETE(self):
        """Handle DELETE requests."""
        self._send_json_response({
            'status': 'ok',
            'message': 'DELETE request received'
        })
    
    def _send_json_response(self, data, status=200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        
        response_json = json.dumps(data, indent=2)
        self.wfile.write(response_json.encode('utf-8'))
    
    def _send_error(self, status, message):
        """Send error response."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        error_json = json.dumps({'error': message})
        self.wfile.write(error_json.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override log method for cleaner output."""
        # Increment request counter
        if not hasattr(self.server, 'request_count'):
            self.server.request_count = 0
        self.server.request_count += 1
        
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")


def run_server(port=8001):
    """Run the demo backend server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, DemoBackendHandler)
    
    print(f"Demo backend server starting on port {port}")
    print("Available endpoints:")
    print("  GET  /health")
    print("  GET  /api/users")
    print("  GET  /api/status")
    print("  POST /api/auth/login")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()


if __name__ == '__main__':
    run_server()
