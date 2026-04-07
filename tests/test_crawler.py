import pytest
from unittest.mock import patch, MagicMock
from src.crawler import Crawler


# ── Helpers ──────────────────────────────────────────────────────────────────

SIMPLE_HTML = """
<html><body>
  <a href="/page2">Page 2</a>
  <a href="/page3">Page 3</a>
  <a href="https://external.com/other">External</a>
</body></html>
"""

EMPTY_HTML = "<html><body></body></html>"


def make_response(text, status_code=200):
    mock = MagicMock()
    mock.status_code = status_code
    mock.text = text
    return mock


# ── Unit Tests ────────────────────────────────────────────────────────────────

class TestIsValidUrl:
    def test_same_domain_is_valid(self):
        c = Crawler("https://quotes.toscrape.com/")
        assert c._is_valid_url("https://quotes.toscrape.com/page/2/") is True

    def test_external_domain_is_invalid(self):
        c = Crawler("https://quotes.toscrape.com/")
        assert c._is_valid_url("https://external.com/page") is False

    def test_different_subdomain_is_invalid(self):
        c = Crawler("https://quotes.toscrape.com/")
        assert c._is_valid_url("https://other.toscrape.com/") is False


class TestGetLinks:
    def test_extracts_internal_links(self):
        c = Crawler("https://quotes.toscrape.com/")
        links = c._get_links(SIMPLE_HTML, "https://quotes.toscrape.com/")
        assert "https://quotes.toscrape.com/page2" in links
        assert "https://quotes.toscrape.com/page3" in links

    def test_excludes_external_links(self):
        c = Crawler("https://quotes.toscrape.com/")
        links = c._get_links(SIMPLE_HTML, "https://quotes.toscrape.com/")
        assert "https://external.com/other" not in links

    def test_empty_page_returns_no_links(self):
        c = Crawler("https://quotes.toscrape.com/")
        links = c._get_links(EMPTY_HTML, "https://quotes.toscrape.com/")
        assert links == set()

    def test_strips_fragment_from_url(self):
        html = '<html><body><a href="/page#section">Link</a></body></html>'
        c = Crawler("https://quotes.toscrape.com/")
        links = c._get_links(html, "https://quotes.toscrape.com/")
        assert "https://quotes.toscrape.com/page" in links
        for link in links:
            assert "#" not in link


# ── Integration Tests (mocked network) ───────────────────────────────────────

class TestCrawl:
    @patch("src.crawler.time.sleep")
    @patch("src.crawler.requests.get")
    def test_crawl_visits_linked_pages(self, mock_get, mock_sleep):
        page1 = '<html><body><a href="/page2">P2</a></body></html>'
        page2 = "<html><body>No links here</body></html>"

        mock_get.side_effect = [
            make_response(page1),
            make_response(page2),
        ]

        c = Crawler("https://quotes.toscrape.com/", politeness_delay=0)
        pages = c.crawl()

        assert "https://quotes.toscrape.com/" in pages
        assert "https://quotes.toscrape.com/page2" in pages

    @patch("src.crawler.time.sleep")
    @patch("src.crawler.requests.get")
    def test_crawl_skips_non_200_responses(self, mock_get, mock_sleep):
        mock_get.return_value = make_response("", status_code=404)
        c = Crawler("https://quotes.toscrape.com/", politeness_delay=0)
        pages = c.crawl()
        assert pages == {}

    @patch("src.crawler.time.sleep")
    @patch("src.crawler.requests.get")
    def test_crawl_does_not_visit_same_url_twice(self, mock_get, mock_sleep):
        # Both pages link back to each other
        html = '<html><body><a href="/">Home</a></body></html>'
        mock_get.return_value = make_response(html)

        c = Crawler("https://quotes.toscrape.com/", politeness_delay=0)
        pages = c.crawl()

        # Should only visit base URL once despite circular link
        assert mock_get.call_count == 1

    @patch("src.crawler.time.sleep")
    @patch("src.crawler.requests.get")
    def test_crawl_handles_network_error_gracefully(self, mock_get, mock_sleep):
        import requests as req
        mock_get.side_effect = req.RequestException("Connection failed")
        c = Crawler("https://quotes.toscrape.com/", politeness_delay=0)
        pages = c.crawl()  # Should not raise
        assert pages == {}

    @patch("src.crawler.time.sleep")
    @patch("src.crawler.requests.get")
    def test_politeness_delay_is_called(self, mock_get, mock_sleep):
        page1 = '<html><body><a href="/page2">P2</a></body></html>'
        page2 = "<html><body></body></html>"
        mock_get.side_effect = [make_response(page1), make_response(page2)]

        c = Crawler("https://quotes.toscrape.com/", politeness_delay=6)
        c.crawl()

        mock_sleep.assert_called_with(6)