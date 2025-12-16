from flask import Flask, request, jsonify
from flask_cors import CORS
from web_research import search_google, scrape_website, verify_urls
from urllib.parse import urlparse
from client_guidelines import get_client_guidelines
from brief_generator import generate_brief_markdown

app = Flask(__name__)
CORS(app)

@app.route('/api/brief', methods=['POST'])
def generate_brief():
    data = request.get_json()
    url = data.get('url')
    topic = data.get('topic')
    keywords = data.get('keywords')

    print(f"Received data: {data}")

    # Extract domain from URL
    domain = urlparse(url).netloc

    # Get client guidelines
    client_guidelines = get_client_guidelines(domain)

    # Perform web research
    topic_query = f"site:{domain} {topic}"
    topic_results = search_google(topic_query, num_results=10) # Get more results to have enough for verification

    # Verify URLs
    verified_urls = verify_urls(topic_results)
    internal_links = verified_urls[:3]

    scraped_texts = []
    for result_url in internal_links:
        text = scrape_website(result_url)
        if text:
            scraped_texts.append(text[:1000]) # Limit the text size for now

    brief_data = {
        'url': url,
        'topic': topic,
        'keywords': keywords,
        'internal_links': internal_links,
        'scraped_texts': scraped_texts,
        'client_guidelines': client_guidelines
    }

    brief = generate_brief_markdown(brief_data)

    return jsonify({
        'message': 'Brief generated successfully!',
        'brief': brief
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)