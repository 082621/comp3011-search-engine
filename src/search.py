class Searcher:
    def __init__(self, indexer):
        self.indexer = indexer

    def print_word(self, word):
        """
        Return a formatted string of the inverted index entry for a word.
        Returns None if the word is not found.
        """
        data = self.indexer.get_word_data(word)

        if data is None:
            return None

        lines = [f"Index entry for '{word.lower()}':"]
        for url, stats in data.items():
            lines.append(f"  {url}")
            lines.append(f"    frequency : {stats['frequency']}")
            lines.append(f"    positions : {stats['positions']}")

        return "\n".join(lines)

    def find(self, query):
        """
        Find all pages containing every word in the query.
        Query is a string of one or more words.
        Returns a sorted list of matching URLs, or empty list if none found.
        """
        if not query or not query.strip():
            return []

        words = query.lower().split()

        # Get the set of URLs for each word, then intersect
        matching_urls = None

        for word in words:
            data = self.indexer.get_word_data(word)

            if data is None:
                # Word not in index at all — no pages can match
                return []

            urls_for_word = set(data.keys())

            if matching_urls is None:
                matching_urls = urls_for_word
            else:
                matching_urls &= urls_for_word

        if matching_urls is None:
            return []

        return sorted(matching_urls)