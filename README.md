# DarkPatternsWebScrapers

This repository provides two Python-based web scrapers for collecting BibTeX entries from academic search engines: Google Scholar and arXiv. These scripts automate the process of gathering scholarly references for systematic literature reviews or citation management.

## Features

- **Google Scholar Scraper**: Uses Selenium to interact with Google Scholar, click through citation options, and download BibTeX entries for each paper.
- **arXiv Scraper**: Uses `requests` and `BeautifulSoup` to fetch and parse arXiv search results, then retrieves BibTeX entries using the [arxiv2bib](https://github.com/nathangrigg/arxiv2bib) command-line tool.

## Requirements

- **Python 3.8+**
- **Required Python packages**:
  - `selenium` (for Google Scholar scraper)
  - `requests`
  - `beautifulsoup4`
- **arXiv2bib**: Install via `pip install arxiv2bib` (or clone the GitHub repo and ensure the `arxiv2bib` command is in your PATH).
- **ChromeDriver**: Required for Selenium to control Google Chrome (download from [ChromeDriver Downloads](https://chromedriver.chromium.org/downloads)).

## Usage

### Google Scholar Scraper

1. **Install dependencies**:
