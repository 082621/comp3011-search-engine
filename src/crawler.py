import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class Crawler:
    def __init__(self, base_url, politeness_delay=6):
        self.base_url = base_url
        self.politeness_delay = politeness_delay
        self.visited = set()
        self.pages = {}  # {url: html_content}

    def _is_valid_url(self, url):
        """Check the URL belongs to the same domain as base_url."""
        parsed_base = urlparse(self.base_url)
        parsed_url = urlparse(url)
        return parsed_url.netloc == parsed_base.netloc

    def _get_links(self, html, current_url):
        """Extract all valid internal links from a page."""
        soup = BeautifulSoup(html, "html.parser")
        links = set()
        for tag in soup.find_all("a", href=True):
            full_url = urljoin(current_url, tag["href"])
            # Strip fragment (#section) from URL
            full_url = full_url.split("#")[0]
            if self._is_valid_url(full_url) and full_url not in self.visited:
                links.add(full_url)
        return links

    def crawl(self):
        """
        Crawl all pages starting from base_url.
        Returns a dict of {url: html_content}.
        """
        queue = [self.base_url]

        while queue:
            url = queue.pop(0)

            if url in self.visited:
                continue

            try:
                print(f"Crawling: {url}")
                response = requests.get(url, timeout=10)

                if response.status_code != 200:
                    print(f"  Skipped (status {response.status_code})")
                    continue

                html = response.text
                self.visited.add(url)
                self.pages[url] = html

                new_links = self._get_links(html, url)
                queue.extend(new_links)

            except requests.RequestException as e:
                print(f"  Error fetching {url}: {e}")

            # Politeness window: wait before next request
            if queue:
                time.sleep(self.politeness_delay)

        print(f"\nCrawling complete. {len(self.pages)} pages visited.")
        return self.pages