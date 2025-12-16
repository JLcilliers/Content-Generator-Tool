"""
Batch API - Processes multiple briefs from Excel upload
Uses streaming response for progress updates
"""
import json
import sys
import os
import zipfile
import io

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

            # Start streaming response
            self.send_response(200)
            self.send_header('Content-Type', 'application/x-ndjson')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Transfer-Encoding', 'chunked')
            self.end_headers()

            documents = []
            results = []
            total = len(items)

            for idx, item in enumerate(items):
                current = idx + 1
                progress = int((current / total) * 100)

                # Send progress update
                progress_msg = json.dumps({
                    'type': 'progress',
                    'progress': progress,
                    'current': f"{current}/{total}: {item.get('topic', 'Item')}"
                })
                self.wfile.write(f"{progress_msg}\n".encode())
                self.wfile.flush()

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
                    documents.append(doc_path)

                    result = {
                        'row': item.get('row', idx + 1),
                        'topic': item['topic'],
                        'status': 'success'
                    }
                    results.append(result)

                    # Send result update
                    result_msg = json.dumps({'type': 'result', 'result': result})
                    self.wfile.write(f"{result_msg}\n".encode())
                    self.wfile.flush()

                except Exception as e:
                    # Send error and stop
                    error_msg = json.dumps({
                        'type': 'error',
                        'error': f"Error on row {item.get('row', idx + 1)} ({item.get('topic', 'Item')}): {str(e)}"
                    })
                    self.wfile.write(f"{error_msg}\n".encode())
                    self.wfile.flush()
                    return

            # Create ZIP archive
            if documents:
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for doc_path in documents:
                        if os.path.exists(doc_path):
                            zip_file.write(doc_path, os.path.basename(doc_path))

                # Save ZIP to temp
                zip_path = '/tmp/briefs/batch_briefs.zip'
                os.makedirs(os.path.dirname(zip_path), exist_ok=True)
                with open(zip_path, 'wb') as f:
                    f.write(zip_buffer.getvalue())

                # Send completion with ZIP URL
                complete_msg = json.dumps({
                    'type': 'complete',
                    'zipUrl': f'/api/download?path={zip_path}'
                })
                self.wfile.write(f"{complete_msg}\n".encode())
                self.wfile.flush()

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
