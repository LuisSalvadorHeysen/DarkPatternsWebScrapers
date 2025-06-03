#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import subprocess
import time
import sys
from urllib.parse import urlencode

def get_arxiv_results(query_params):
    """
    Fetches the HTML content of an arXiv search results page based on query parameters.
    Args:
        query_params: A dictionary of search parameters for arXiv.
    Returns:
        The HTML content of the search results page.
    """
    base_url = "https://arxiv.org/search/"
    
    # Constructs the full query URL using the provided parameters
    query_string = urlencode(query_params)
    url = f"{base_url}?{query_string}"
    
    # Sets headers to mimic a browser request, helping avoid being blocked
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Sends a GET request to arXiv with a timeout
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()  # Raises an exception for HTTP errors
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching search results: {e}", file=sys.stderr)
        sys.exit(1)

def extract_arxiv_ids(html):
    """
    Extracts arXiv IDs and titles from the search results HTML.
    Args:
        html: The HTML content of the arXiv search results page.
    Returns:
        A tuple of (list of arXiv IDs, list of dictionaries with paper details).
    """
    soup = BeautifulSoup(html, 'html.parser')
    papers = soup.find_all('p', class_='list-title')
    arxiv_ids = []
    paper_details = []
    
    for paper in papers:
        # Extracts the arXiv ID from the text, which follows 'arXiv:'
        if 'arXiv:' in paper.get_text():
            arxiv_id = paper.get_text().split('arXiv:')[1].split()[0].strip()
            
            # Finds the title in the next sibling element with class 'title'
            title_elem = paper.find_next('p', class_='title')
            title = title_elem.get_text().strip() if title_elem else "Title not found"
            
            arxiv_ids.append(arxiv_id)
            paper_details.append({
                'id': arxiv_id,
                'title': title
            })
    
    return arxiv_ids, paper_details

def get_bibtex(arxiv_id):
    """
    Uses the arxiv2bib command-line tool to fetch the BibTeX entry for a given arXiv ID.
    Args:
        arxiv_id: The arXiv identifier for the paper.
    Returns:
        The BibTeX entry as a string, or None if an error occurs.
    """
    try:
        # Runs the arxiv2bib command and captures its output
        result = subprocess.run(['arxiv2bib', arxiv_id], 
                              capture_output=True, 
                              text=True,
                              timeout=30)
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"Error processing {arxiv_id}: {result.stderr}", file=sys.stderr)
            return None
    except subprocess.CalledProcessError as e:
        print(f"Error processing {arxiv_id}: {e}", file=sys.stderr)
        return None
    except subprocess.TimeoutExpired:
        print(f"Timeout while processing {arxiv_id}", file=sys.stderr)
        return None

def main():
    """
    Main function that orchestrates the search, extraction, and BibTeX fetching process.
    """
    # Define the search parameters for arXiv
    query_params = {
        'searchtype': 'all',
        'query': '(dark pattern OR dark patterns OR dark design OR dark designs OR deceptive design OR deceptive designs OR manipulative design OR manipulative designs OR coercive design OR coercive designs OR dark default OR dark defaults OR dark-pattern OR dark-patterns) AND experiment*',
        'abstracts': 'show',
        'size': '200',
        'order': ''  # Default ordering
    }
    
    # Fetch the arXiv search results
    print("Fetching arXiv search results...")
    html = get_arxiv_results(query_params)
    
    # Extract arXiv IDs and paper details from the results
    arxiv_ids, paper_details = extract_arxiv_ids(html)
    print(f"\nFound {len(arxiv_ids)} papers")
    
    # Print the list of found papers for verification
    print("\nPapers found:")
    for paper in paper_details:
        print(f"{paper['id']}: {paper['title']}")
    
    # Create and open the output file for BibTeX entries
    print("\nGetting BibTeX entries...")
    with open('dark_patterns_bibtex.bib', 'w', encoding='utf-8') as f:
        for i, arxiv_id in enumerate(arxiv_ids, 1):
            print(f"Processing {i}/{len(arxiv_ids)}: {arxiv_id}")
            
            # Fetch the BibTeX entry for the current arXiv ID
            bibtex = get_bibtex(arxiv_id)
            
            if bibtex:
                f.write(bibtex + '\n')
            
            # Add a small delay between requests to be polite to arXiv servers
            time.sleep(1)
    
    print(f"\nDone! BibTeX entries have been saved to 'dark_patterns_bibtex.bib'")
    print(f"Total papers processed: {len(arxiv_ids)}")

if __name__ == "__main__":
    main()

