"""
Generate API - Creates a single content brief
"""
import json
import sys
import os

# Add lib to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))

from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Import here to ensure path is set
            from brief_generator import BriefGenerator
            from web_researcher import WebResearcher
            from document_formatter import DocumentFormatter

            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(content_length))

            provider = body.get('provider', 'claude')
            url = body.get('url', '')
            topic = body.get('topic', '')
            primary_keyword = body.get('primary_keyword', '')
            secondary_keywords = body.get('secondary_keywords', [])
            auto_links = body.get('auto_links', True)
            manual_links = body.get('manual_links', [])
            research_data = body.get('research_data')

            # Get internal links
            if auto_links:
                researcher = WebResearcher()
                all_keywords = [primary_keyword] + secondary_keywords
                internal_links = researcher.find_internal_links(url, topic, all_keywords)
            else:
                internal_links = manual_links[:3]

            # Generate brief
            generator = BriefGenerator(provider=provider)
            brief_data = generator.generate_brief(
                url=url,
                topic=topic,
                primary_keyword=primary_keyword,
                secondary_keywords=secondary_keywords,
                internal_links=internal_links,
                website_research=research_data
            )

            # Create document
            formatter = DocumentFormatter()
            doc_path = formatter.create_brief_document(brief_data)

            # Add document URL to response
            brief_data['document_url'] = f'/api/download?path={doc_path}'

            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(brief_data).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
