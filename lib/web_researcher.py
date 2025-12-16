"""
Web Research Module
Handles website analysis, content scraping, and internal link discovery.
"""

import re
import requests
from typing import Dict, List, Optional
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup


class WebResearcher:
    """Handles website research for content brief generation."""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.cache = {}

    def research_website(self, url: str, topic: str = None) -> Dict:
        """Research a website to extract key information."""
        result = {
            'url': url,
            'domain': self._extract_domain(url),
            'brand_voice': '',
            'services_products': [],
            'target_audience': '',
            'geographic_focus': '',
            'business_model': '',
            'key_content': '',
            'error': None
        }

        try:
            homepage_content = self._fetch_page(url)
            if not homepage_content:
                result['error'] = "Could not fetch homepage"
                return result

            soup = BeautifulSoup(homepage_content, 'html.parser')

            result['brand_voice'] = self._extract_brand_voice(soup)
            result['services_products'] = self._extract_services(soup)
            result['target_audience'] = self._extract_audience(soup)
            result['geographic_focus'] = self._extract_location(soup)
            result['business_model'] = self._detect_business_model(soup)
            result['key_content'] = self._get_clean_text(soup)[:2000]

            if topic:
                relevant_pages = self._find_relevant_pages(url, topic)
                if relevant_pages:
                    additional_content = []
                    for page_url in relevant_pages[:3]:
                        page_content = self._fetch_page(page_url)
                        if page_content:
                            page_soup = BeautifulSoup(page_content, 'html.parser')
                            additional_content.append(self._get_clean_text(page_soup)[:1000])
                    if additional_content:
                        result['topic_relevant_content'] = '\n\n'.join(additional_content)

        except Exception as e:
            result['error'] = str(e)

        return result

    def find_internal_links(self, url: str, topic: str, keywords: List[str] = None) -> List[str]:
        """Find relevant internal links for the given topic."""
        domain = self._extract_domain(url)
        all_links = set()

        try:
            homepage_content = self._fetch_page(url)
            if homepage_content:
                soup = BeautifulSoup(homepage_content, 'html.parser')
                all_links.update(self._extract_internal_links(soup, domain, url))

            topic_terms = topic.lower().split()
            for link in list(all_links):
                link_lower = link.lower()
                for term in topic_terms:
                    if term in link_lower:
                        page_content = self._fetch_page(link)
                        if page_content:
                            page_soup = BeautifulSoup(page_content, 'html.parser')
                            all_links.update(self._extract_internal_links(page_soup, domain, link))
                        break

            filtered_links = self._filter_links(all_links, url)
            scored_links = self._score_links_by_relevance(filtered_links, topic, keywords or [])

            verified_links = []
            for link, score in sorted(scored_links.items(), key=lambda x: x[1], reverse=True):
                if self._verify_url(link):
                    verified_links.append(link)
                    if len(verified_links) >= 3:
                        break

            return verified_links[:3]

        except Exception as e:
            print(f"Error finding internal links: {e}")
            return []

    def _fetch_page(self, url: str) -> Optional[str]:
        if url in self.cache:
            return self.cache[url]

        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200:
                self.cache[url] = response.text
                return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")

        return None

    def _extract_domain(self, url: str) -> str:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain

    def _extract_internal_links(self, soup: BeautifulSoup, domain: str, base_url: str) -> set:
        links = set()
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']

            if href.startswith('/'):
                href = urljoin(base_url, href)
            elif not href.startswith(('http://', 'https://')):
                href = urljoin(base_url, href)

            link_domain = self._extract_domain(href)
            if link_domain == domain:
                parsed = urlparse(href)
                clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                if clean_url.endswith('/'):
                    clean_url = clean_url[:-1]
                links.add(clean_url)

        return links

    def _filter_links(self, links: set, homepage_url: str) -> set:
        homepage = homepage_url.rstrip('/')
        excluded_patterns = [
            '/privacy', '/terms', '/contact', '/login', '/signup', '/register',
            '/cart', '/checkout', '/account', '/search', '/tag/', '/category/',
            '/page/', '/wp-admin', '/wp-login', '/feed', '/rss', '/sitemap',
            '/author/', '#', 'javascript:', 'mailto:', 'tel:'
        ]

        filtered = set()
        for link in links:
            link_lower = link.lower()

            if link.rstrip('/') == homepage:
                continue

            skip = False
            for pattern in excluded_patterns:
                if pattern in link_lower:
                    skip = True
                    break

            if not skip:
                filtered.add(link)

        return filtered

    def _score_links_by_relevance(self, links: set, topic: str, keywords: List[str]) -> Dict[str, float]:
        scores = {}
        topic_terms = set(topic.lower().split())
        keyword_terms = set()
        for kw in keywords:
            keyword_terms.update(kw.lower().split())

        for link in links:
            score = 0.0
            link_lower = link.lower()

            for term in topic_terms:
                if len(term) > 3 and term in link_lower:
                    score += 2.0

            for term in keyword_terms:
                if len(term) > 3 and term in link_lower:
                    score += 1.5

            if '/services' in link_lower or '/service' in link_lower:
                score += 1.0
            if '/about' in link_lower:
                score += 0.5
            if '/blog' in link_lower:
                score += 0.5

            if link.count('/') > 5:
                score -= 0.5

            scores[link] = score

        return scores

    def _verify_url(self, url: str) -> bool:
        try:
            response = self.session.head(url, allow_redirects=True, timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            try:
                response = self.session.get(url, allow_redirects=True, timeout=5)
                return response.status_code == 200
            except requests.RequestException:
                return False

    def _get_clean_text(self, soup: BeautifulSoup) -> str:
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        text = soup.get_text(separator=' ', strip=True)
        text = re.sub(r'\s+', ' ', text)
        return text

    def _extract_brand_voice(self, soup: BeautifulSoup) -> str:
        indicators = []

        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            indicators.append(meta_desc['content'])

        h1 = soup.find('h1')
        if h1:
            indicators.append(h1.get_text(strip=True))

        about_section = soup.find(['section', 'div'], class_=re.compile(r'about|mission|values', re.I))
        if about_section:
            indicators.append(about_section.get_text(separator=' ', strip=True)[:300])

        return ' | '.join(indicators)[:500] if indicators else 'Professional and informative'

    def _extract_services(self, soup: BeautifulSoup) -> List[str]:
        services = []

        service_sections = soup.find_all(['section', 'div'], class_=re.compile(r'service|product|solution|offer', re.I))
        for section in service_sections[:2]:
            headings = section.find_all(['h2', 'h3', 'h4'])
            for h in headings[:5]:
                text = h.get_text(strip=True)
                if text and len(text) < 100:
                    services.append(text)

        nav = soup.find('nav')
        if nav and len(services) < 3:
            nav_links = nav.find_all('a')
            for link in nav_links:
                text = link.get_text(strip=True)
                href = link.get('href', '')
                if '/service' in href.lower() or '/product' in href.lower():
                    if text and len(text) < 50 and text not in services:
                        services.append(text)

        return services[:10]

    def _extract_audience(self, soup: BeautifulSoup) -> str:
        text = self._get_clean_text(soup).lower()

        audience_indicators = []

        b2b_terms = ['business', 'enterprise', 'company', 'organization', 'professional']
        for term in b2b_terms:
            if term in text:
                audience_indicators.append('Business professionals')
                break

        b2c_terms = ['homeowner', 'family', 'individual', 'personal', 'residential']
        for term in b2c_terms:
            if term in text:
                audience_indicators.append('Individual consumers')
                break

        return ', '.join(audience_indicators) if audience_indicators else 'General audience'

    def _extract_location(self, soup: BeautifulSoup) -> str:
        text = self._get_clean_text(soup)

        location_patterns = [
            r'serving\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'located\s+in\s+([A-Z][a-z]+(?:,\s*[A-Z]{2})?)',
            r'based\s+in\s+([A-Z][a-z]+(?:,\s*[A-Z]{2})?)',
        ]

        for pattern in location_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)

        if 'nationwide' in text.lower():
            return 'Nationwide'
        if 'international' in text.lower() or 'global' in text.lower():
            return 'International'

        return 'Not specified'

    def _detect_business_model(self, soup: BeautifulSoup) -> str:
        text = self._get_clean_text(soup).lower()

        b2b_score = 0
        b2c_score = 0

        b2b_indicators = ['enterprise', 'business solution', 'commercial', 'dealer', 'wholesale', 'b2b', 'corporate']
        b2c_indicators = ['consumer', 'personal', 'home', 'family', 'individual', 'residential', 'b2c']

        for term in b2b_indicators:
            if term in text:
                b2b_score += 1

        for term in b2c_indicators:
            if term in text:
                b2c_score += 1

        if b2b_score > b2c_score:
            return 'B2B'
        elif b2c_score > b2b_score:
            return 'B2C'
        elif b2b_score > 0 and b2c_score > 0:
            return 'Both B2B and B2C'
        else:
            return 'Not specified'

    def _find_relevant_pages(self, url: str, topic: str) -> List[str]:
        domain = self._extract_domain(url)
        relevant = []

        try:
            homepage_content = self._fetch_page(url)
            if homepage_content:
                soup = BeautifulSoup(homepage_content, 'html.parser')
                all_links = self._extract_internal_links(soup, domain, url)

                topic_terms = topic.lower().split()
                for link in all_links:
                    link_lower = link.lower()
                    for term in topic_terms:
                        if len(term) > 3 and term in link_lower:
                            relevant.append(link)
                            break

        except Exception as e:
            print(f"Error finding relevant pages: {e}")

        return relevant[:5]
