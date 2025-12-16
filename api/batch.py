"""
Batch API - Processes multiple briefs from Excel upload
Returns ZIP file as base64 for serverless compatibility
"""
import json
import sys
import os
import zipfile
import io
import base64

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))

from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            from brief_generator import BriefGenerator
            from web_researcher import WebResearcher
            from document_formatter import DocumentFormatter

            content_length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(content_length))

            provider = body.get('provider', 'claude')
            items = body.get('items', [])

            if not items:
                raise ValueError("No items to process")

            # Process all items and collect documents
            documents = []  # List of (filename, bytes) tuples
            results = []
            total = len(items)

            for idx, item in enumerate(items):
                current = idx + 1

                try:
                    researcher = WebResearcher()
                    generator = BriefGenerator(provider=provider)
                    formatter = DocumentFormatter()

                    # Research website
                    research_data = researcher.research_website(item['url'], item['topic'])

                    # Find internal links
                    all_keywords = [item['primaryKeyword']] + item.get('secondaryKeywords', [])
                    internal_links = researcher.find_internal_links(item['url'], item['topic'], all_keywords)

                    # Generate brief
                    brief_data = generator.generate_brief(
                        url=item['url'],
                        topic=item['topic'],
                        primary_keyword=item['primaryKeyword'],
                        secondary_keywords=item.get('secondaryKeywords', []),
                        internal_links=internal_links,
                        website_research=research_data
                    )

                    # Create document
                    doc_path = formatter.create_brief_document(brief_data)

                    # Read document bytes
                    with open(doc_path, 'rb') as f:
                        doc_bytes = f.read()

                    documents.append((os.path.basename(doc_path), doc_bytes))

                    results.append({
                        'row': item.get('row', idx + 1),
                        'topic': item['topic'],
                        'status': 'success'
                    })

                except Exception as e:
                    results.append({
                        'row': item.get('row', idx + 1),
                        'topic': item.get('topic', 'Unknown'),
                        'status': 'error',
                        'error': str(e)
                    })

            # Create ZIP archive in memory
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for filename, doc_bytes in documents:
                    zip_file.writestr(filename, doc_bytes)

            zip_buffer.seek(0)
            zip_base64 = base64.b64encode(zip_buffer.getvalue()).decode('utf-8')

            # Send response with all data
            response = {
                'results': results,
                'zip_base64': zip_base64,
                'zip_filename': 'content_briefs.zip',
                'success_count': len([r for r in results if r['status'] == 'success']),
                'error_count': len([r for r in results if r['status'] == 'error']),
                'total': total
            }

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            import traceback
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': str(e),
                'detail': traceback.format_exc()
            }).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
