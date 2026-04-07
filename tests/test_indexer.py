import pytest
import json
import os
from src.indexer import Indexer


# ── Fixtures ──────────────────────────────────────────────────────────────────

SIMPLE_HTML = """
<html><body>
  <p>Good books are good for the mind</p>
</body></html>
"""

MULTI_PAGE_HTML_1 = "<html><body><p>the cat sat on the mat</p></body></html>"
MULTI_PAGE_HTML_2 = "<html><body><p>the cat wore a hat</p></body></html>"


# ── _extract_text ─────────────────────────────────────────────────────────────

class TestExtractText:
    def test_extracts_visible_text(self):
        idx = Indexer()
        text = idx._extract_text("<html><body><p>Hello world</p></body></html>")
        assert "hello" in text.lower()
        assert "world" in text.lower()

    def test_strips_script_tags(self):
        idx = Indexer()
        html = "<html><body><script>var x = 1;</script><p>visible</p></body></html>"
        text = idx._extract_text(html)
        assert "var" not in text
        assert "visible" in text

    def test_strips_style_tags(self):
        idx = Indexer()
        html = "<html><body><style>body{color:red}</style><p>text</p></body></html>"
        text = idx._extract_text(html)
        assert "color" not in text
        assert "text" in text


# ── _tokenise ─────────────────────────────────────────────────────────────────

class TestTokenise:
    def test_lowercases_tokens(self):
        idx = Indexer()
        tokens = idx._tokenise("Hello WORLD")
        assert tokens == ["hello", "world"]

    def test_removes_punctuation(self):
        idx = Indexer()
        tokens = idx._tokenise("hello, world!")
        assert "," not in tokens
        assert "!" not in tokens

    def test_handles_empty_string(self):
        idx = Indexer()
        assert idx._tokenise("") == []

    def test_handles_numbers_only(self):
        idx = Indexer()
        tokens = idx._tokenise("123 456")
        assert tokens == []

    def test_preserves_order(self):
        idx = Indexer()
        tokens = idx._tokenise("the quick brown fox")
        assert tokens == ["the", "quick", "brown", "fox"]


# ── add_page ──────────────────────────────────────────────────────────────────

class TestAddPage:
    def test_indexes_word_frequency(self):
        idx = Indexer()
        idx.add_page("https://example.com/", SIMPLE_HTML)
        data = idx.get_word_data("good")
        assert data["https://example.com/"]["frequency"] == 2

    def test_indexes_word_positions(self):
        idx = Indexer()
        idx.add_page("https://example.com/", SIMPLE_HTML)
        data = idx.get_word_data("good")
        positions = data["https://example.com/"]["positions"]
        assert len(positions) == 2
        assert positions[0] < positions[1]

    def test_case_insensitive_indexing(self):
        idx = Indexer()
        idx.add_page("https://example.com/", SIMPLE_HTML)
        # "Good" and "good" should both be stored under "good"
        assert idx.get_word_data("good") is not None
        assert idx.get_word_data("Good") is not None

    def test_unknown_word_returns_none(self):
        idx = Indexer()
        idx.add_page("https://example.com/", SIMPLE_HTML)
        assert idx.get_word_data("zzzzz") is None

    def test_multiple_pages_same_word(self):
        idx = Indexer()
        idx.add_page("https://example.com/1", MULTI_PAGE_HTML_1)
        idx.add_page("https://example.com/2", MULTI_PAGE_HTML_2)
        data = idx.get_word_data("cat")
        assert "https://example.com/1" in data
        assert "https://example.com/2" in data


# ── build ─────────────────────────────────────────────────────────────────────

class TestBuild:
    def test_build_indexes_all_pages(self):
        idx = Indexer()
        pages = {
            "https://example.com/1": MULTI_PAGE_HTML_1,
            "https://example.com/2": MULTI_PAGE_HTML_2,
        }
        idx.build(pages)
        assert len(idx.index) > 0

    def test_build_empty_pages(self):
        idx = Indexer()
        idx.build({})
        assert idx.index == {}


# ── save and load ─────────────────────────────────────────────────────────────

class TestSaveLoad:
    def test_save_creates_file(self, tmp_path):
        idx = Indexer()
        idx.add_page("https://example.com/", SIMPLE_HTML)
        filepath = tmp_path / "index.json"
        idx.save(str(filepath))
        assert filepath.exists()

    def test_save_and_load_roundtrip(self, tmp_path):
        idx = Indexer()
        idx.add_page("https://example.com/", SIMPLE_HTML)
        filepath = str(tmp_path / "index.json")
        idx.save(filepath)

        idx2 = Indexer()
        idx2.load(filepath)
        assert idx2.get_word_data("good") == idx.get_word_data("good")

    def test_load_nonexistent_file_raises(self, tmp_path):
        idx = Indexer()
        with pytest.raises(FileNotFoundError):
            idx.load(str(tmp_path / "nonexistent.json"))