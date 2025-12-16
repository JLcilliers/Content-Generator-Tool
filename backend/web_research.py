import requests
from bs4 import BeautifulSoup
from googlesearch import search

def search_google(query, num_results=10):
    """
    Performs a Google search and returns a list of URLs.
    """
    try:
        return list(search(query, num_results=num_results))
    except Exception as e:
        print(f"An error occurred during Google search: {e}")
        return []

def scrape_website(url):
    """
    Scrapes the text content of a website.
    """
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.get_text()
    except Exception as e:
        print(f"An error occurred during website scraping: {e}")
        return None

def verify_urls(urls):
    """
    Verifies a list of URLs and returns the ones that return a 200 status code.
    """
    verified_urls = []
    for url in urls:
        try:
            response = requests.head(url, allow_redirects=True, timeout=5)
            if response.status_code == 200:
                verified_urls.append(url)
        except requests.RequestException as e:
            print(f"Could not verify url {url}: {e}")
    return verified_urls

if __name__ == '__main__':
    # Example usage
    query = "site:healthworkstx.com neck pain"
    results = search_google(query)
    for url in results:
        print(url)

    # Example usage of scrape_website
    if results:
        text = scrape_website(results[0])
        if text:
            print(f"\nScraped text from {results[0]}:\n")
            print(text[:500]) # Print first 500 characters

    # Example usage of verify_urls
    if results:
        verified = verify_urls(results)
        print(f"\nVerified URLs:\n{verified}")

