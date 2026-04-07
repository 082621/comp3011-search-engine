# COMP3011 Coursework 2: Search Engine Tool

A command-line search engine that crawls [quotes.toscrape.com](https://quotes.toscrape.com/),
builds an inverted index, and allows users to search for words and phrases across all crawled pages.

---

## Project Overview

This tool consists of three core components:

- **Crawler** (`src/crawler.py`): Crawls all pages of the target website while respecting a 6-second politeness window between requests.
- **Indexer** (`src/indexer.py`): Parses HTML, extracts visible text, and builds an inverted index storing word frequency and position data for each page.
- **Searcher** (`src/search.py`): Queries the inverted index to support single and multi-word searches.

---

## Installation

**Requirements:** Python 3.8+

1. Clone the repository:
   git clone https://github.com/082621/comp3011-search-engine.git
   cd comp3011-search-engine

2. Create and activate a virtual environment:
   python3 -m venv .venv
   source .venv/bin/activate      # Mac/Linux
   .venv\Scripts\activate         # Windows

3. Install dependencies:
   pip install -r requirements.txt

---

## Usage

Start the search tool:
   python3 -m src.main

### Commands

| Command | Description | Example |
|---|---|---|
| build | Crawl the website and build the index | > build |
| load | Load a previously built index from disk | > load |
| print <word> | Print the inverted index entry for a word | > print good |
| find <query> | Find all pages containing the query words | > find good friends |
| quit | Exit the program | > quit |

### Example Session

> load
Index loaded from data/index.json (3842 words)

> print good
Index entry for 'good':
  https://quotes.toscrape.com/
    frequency : 2
    positions : [45, 103]
  https://quotes.toscrape.com/page/2/
    frequency : 1
    positions : [88]

> find indifference
Found 2 page(s) for 'indifference':
  https://quotes.toscrape.com/
  https://quotes.toscrape.com/tag/indifference/page/1/

> find good friends
Found 1 page(s) for 'good friends':
  https://quotes.toscrape.com/

> find zzzzz
No pages found for 'zzzzz'.

---

## Inverted Index Structure

The index is stored as a JSON file at data/index.json with the following structure:

  "good": {
    "https://quotes.toscrape.com/": {
      "frequency": 2,
      "positions": [45, 103]
    }
  }

- frequency: number of times the word appears on that page
- positions: token positions of each occurrence (0-indexed)

---

## Testing

Run the full test suite:
   python3 -m pytest tests/ -v

Run with coverage report:
   python3 -m pytest tests/ --cov=src --cov-report=term-missing

The test suite covers:
- Crawler: URL validation, link extraction, politeness window, error handling
- Indexer: text extraction, tokenisation, index building, save/load
- Searcher: single-word search, multi-word intersection, edge cases

---

## Dependencies

| Package | Purpose |
|---|---|
| requests | HTTP requests for web crawling |
| beautifulsoup4 | HTML parsing and text extraction |
| pytest | Test framework |
| pytest-cov | Test coverage reporting |

---

## Architecture

src/
  crawler.py   - Web crawler with politeness window
  indexer.py   - Inverted index builder and storage
  search.py    - Query processor (print + find)
  main.py      - Command-line interface

tests/
  test_crawler.py
  test_indexer.py
  test_search.py

data/
  index.json   - Compiled inverted index
