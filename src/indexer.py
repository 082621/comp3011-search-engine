import json
import re
from bs4 import BeautifulSoup


class Indexer:
    def __init__(self):
        # {word: {url: {"frequency": int, "positions": [int]}}}
        self.index = {}

    def _extract_text(self, html):
        """Extract visible text from HTML, stripping tags."""
        soup = BeautifulSoup(html, "html.parser")

        # Remove script and style elements
        for tag in soup(["script", "style"]):
            tag.decompose()

        return soup.get_text(separator=" ")

    def _tokenise(self, text):
        """
        Lowercase and split text into words.
        Returns a list of tokens in order (preserving position).
        """
        text = text.lower()
        tokens = re.findall(r"[a-z]+(?:'[a-z]+)*", text)
        return tokens

    def add_page(self, url, html):
        """
        Index a single page.
        Extracts text, tokenises it, and updates the inverted index.
        """
        text = self._extract_text(html)
        tokens = self._tokenise(text)

        for position, word in enumerate(tokens):
            if word not in self.index:
                self.index[word] = {}

            if url not in self.index[word]:
                self.index[word][url] = {"frequency": 0, "positions": []}

            self.index[word][url]["frequency"] += 1
            self.index[word][url]["positions"].append(position)

    def build(self, pages):
        """
        Build the full index from a dict of {url: html}.
        """
        for url, html in pages.items():
            self.add_page(url, html)
        print(f"Index built: {len(self.index)} unique words indexed.")

    def save(self, filepath):
        """Save the index to a JSON file."""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)
        print(f"Index saved to {filepath}")

    def load(self, filepath):
        """Load the index from a JSON file."""
        with open(filepath, "r", encoding="utf-8") as f:
            self.index = json.load(f)
        print(f"Index loaded from {filepath} ({len(self.index)} words)")

    def get_word_data(self, word):
        """
        Return index entry for a word (case-insensitive).
        Returns None if word not found.
        """
        return self.index.get(word.lower(), None)