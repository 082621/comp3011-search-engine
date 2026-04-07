import pytest
from src.indexer import Indexer
from src.search import Searcher


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def searcher():
    """A Searcher pre-loaded with three test pages."""
    idx = Indexer()
    idx.add_page(
        "https://example.com/a",
        "<html><body><p>good friends are good</p></body></html>"
    )
    idx.add_page(
        "https://example.com/b",
        "<html><body><p>good books only</p></body></html>"
    )
    idx.add_page(
        "https://example.com/c",
        "<html><body><p>friends and books together</p></body></html>"
    )
    return Searcher(idx)


# ── find: single word ─────────────────────────────────────────────────────────

class TestFindSingleWord:
    def test_finds_pages_containing_word(self, searcher):
        results = searcher.find("good")
        assert "https://example.com/a" in results
        assert "https://example.com/b" in results

    def test_word_not_in_all_pages(self, searcher):
        results = searcher.find("books")
        assert "https://example.com/b" in results
        assert "https://example.com/c" in results
        assert "https://example.com/a" not in results

    def test_nonexistent_word_returns_empty(self, searcher):
        assert searcher.find("zzzzz") == []

    def test_case_insensitive_find(self, searcher):
        lower = searcher.find("good")
        upper = searcher.find("GOOD")
        mixed = searcher.find("Good")
        assert lower == upper == mixed

    def test_returns_sorted_urls(self, searcher):
        results = searcher.find("good")
        assert results == sorted(results)


# ── find: multi-word ──────────────────────────────────────────────────────────

class TestFindMultiWord:
    def test_multi_word_returns_intersection(self, searcher):
        # only page a has both "good" and "friends"
        results = searcher.find("good friends")
        assert results == ["https://example.com/a"]

    def test_multi_word_no_match(self, searcher):
        # no page has both "good" and "together"
        results = searcher.find("good together")
        assert results == []

    def test_multi_word_all_pages_match(self, searcher):
        # "good" is in a and b; "friends" is in a and c → intersection = a
        results = searcher.find("good friends")
        assert "https://example.com/a" in results

    def test_one_word_missing_returns_empty(self, searcher):
        results = searcher.find("good zzzzz")
        assert results == []


# ── find: edge cases ──────────────────────────────────────────────────────────

class TestFindEdgeCases:
    def test_empty_query_returns_empty(self, searcher):
        assert searcher.find("") == []

    def test_whitespace_only_query_returns_empty(self, searcher):
        assert searcher.find("   ") == []

    def test_extra_spaces_in_query(self, searcher):
        # "good  friends" (double space) should still work
        results = searcher.find("good  friends")
        assert "https://example.com/a" in results


# ── print_word ────────────────────────────────────────────────────────────────

class TestPrintWord:
    def test_print_existing_word(self, searcher):
        output = searcher.print_word("good")
        assert output is not None
        assert "good" in output
        assert "https://example.com/a" in output
        assert "frequency" in output
        assert "positions" in output

    def test_print_nonexistent_word_returns_none(self, searcher):
        assert searcher.print_word("zzzzz") is None

    def test_print_case_insensitive(self, searcher):
        lower = searcher.print_word("good")
        upper = searcher.print_word("GOOD")
        assert lower == upper

    def test_print_shows_all_pages(self, searcher):
        output = searcher.print_word("good")
        assert "https://example.com/a" in output
        assert "https://example.com/b" in output