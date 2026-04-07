import os
from src.crawler import Crawler
from src.indexer import Indexer
from src.search import Searcher

BASE_URL = "https://quotes.toscrape.com/"
INDEX_PATH = "data/index.json"


def run():
    indexer = Indexer()
    searcher = Searcher(indexer)

    print("Search Engine Ready.")
    print("Commands: build | load | print <word> | find <query> | quit")
    print("-" * 55)

    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not raw:
            continue

        parts = raw.split()
        command = parts[0].lower()

        # ── build ────────────────────────────────────────────────
        if command == "build":
            print(f"Starting crawl of {BASE_URL} ...")
            crawler = Crawler(BASE_URL, politeness_delay=6)
            pages = crawler.crawl()

            print("Building index ...")
            indexer = Indexer()
            indexer.build(pages)

            os.makedirs("data", exist_ok=True)
            indexer.save(INDEX_PATH)

            searcher = Searcher(indexer)

        # ── load ─────────────────────────────────────────────────
        elif command == "load":
            if not os.path.exists(INDEX_PATH):
                print(f"Error: No index file found at '{INDEX_PATH}'.")
                print("Run 'build' first to create the index.")
            else:
                indexer = Indexer()
                indexer.load(INDEX_PATH)
                searcher = Searcher(indexer)

        # ── print ─────────────────────────────────────────────────
        elif command == "print":
            if len(parts) < 2:
                print("Usage: print <word>")
            else:
                word = parts[1]
                output = searcher.print_word(word)
                if output is None:
                    print(f"'{word}' not found in index.")
                else:
                    print(output)

        # ── find ──────────────────────────────────────────────────
        elif command == "find":
            if len(parts) < 2:
                print("Usage: find <word> [word2 ...]")
            else:
                query = " ".join(parts[1:])
                results = searcher.find(query)
                if not results:
                    print(f"No pages found for '{query}'.")
                else:
                    print(f"Found {len(results)} page(s) for '{query}':")
                    for url in results:
                        print(f"  {url}")

        # ── quit ──────────────────────────────────────────────────
        elif command in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        else:
            print(f"Unknown command: '{command}'")
            print("Commands: build | load | print <word> | find <query> | quit")


if __name__ == "__main__":
    run()