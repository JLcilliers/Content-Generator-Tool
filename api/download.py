"""
Download API - Serves generated documents
"""
import os
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Parse query string
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            file_path = params.get('path', [''])[0]

            if not file_path or not os.path.exists(file_path):
                self.send_response(404)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'File not found')
                return

            # Determine content type
            if file_path.endswith('.docx'):
                content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            elif file_path.endswith('.zip'):
                content_type = 'application/zip'
            else:
                content_type = 'application/octet-stream'

            # Read and send file
            with open(file_path, 'rb') as f:
                file_data = f.read()

            filename = os.path.basename(file_path)

            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
            self.send_header('Content-Length', str(len(file_data)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(file_data)

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(str(e).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
