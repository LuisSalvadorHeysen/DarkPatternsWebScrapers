# Imports necessary libraries for file operations, system utilities, time management,
# URL parsing, date/time handling, exit handlers, and Selenium web automation.
import os
import sys
import time
import urllib.parse
from datetime import datetime
import atexit
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Global lists to keep track of successful and failed BibTeX downloads.
good = []
bad = []
# List to store all downloaded BibTeX entries.
all_bibtex = []
# Variables to track the current page range being processed.
page_start = None
page_end = None
# Filename where BibTeX entries will be saved.
save_filename = None

def get_bibtex_in_page(driver, encoded_query, page_idx, ylo, yhi, first_call, delay=0.5):
    """
    Scrapes a single Google Scholar results page for BibTeX entries.
    Args:
        driver: Selenium webdriver instance
        encoded_query: URL-encoded search query string
        page_idx: Current results page number
        ylo: Year lower bound for search
        yhi: Year upper bound for search
        first_call: Boolean, True if this is the first page being processed
        delay: Time to wait between actions (in seconds)
    """
    global good, bad

    print(f"Currently extracting page {page_idx}\n")
    # Constructs the Google Scholar URL for the current page and year range.
    url = f'https://scholar.google.com/scholar?start={10 * (page_idx - 1)}&q={encoded_query}&hl=en&as_sdt=0,14&as_ylo={ylo}&as_yhi={yhi}'
    driver.get(url)

    # Waits longer for the first page to ensure page load, then less for subsequent pages.
    time.sleep(30 if first_call else 20)  # Consider reducing this for efficiency

    # Finds all article results on the page.
    articles = driver.find_elements(By.CLASS_NAME, "gs_ri")
    bibtex_list = []
    idx = 0

    for article in articles:
        title = article.find_element(By.TAG_NAME, 'a').text
        idx += 1
        try:
            # Clicks the 'Cite' button for the current article.
            cite_button = article.find_element(By.XPATH, './/span[text()="Cite"]')
            cite_button.click()
            time.sleep(delay)
            # Clicks the 'BibTeX' link in the citation popup.
            bibtex_link = driver.find_element(By.XPATH, '//*[@id="gs_citi"]/a[1]')
            bibtex_link.click()
            time.sleep(delay)
            # Extracts the BibTeX entry from the page.
            curr_bibtex = driver.find_element(By.TAG_NAME, "pre")
            bibtex_list.append(curr_bibtex.text)
            time.sleep(delay)
            # Goes back to the previous page (Google Scholar results).
            driver.execute_script("window.history.go(-1)")
            time.sleep(delay)
            # Closes the citation popup.
            x_button = driver.find_element(By.XPATH, '//*[@id="gs_cit-x"]/span[1]')
            x_button.click()
            time.sleep(delay)
            print(f"Successfully downloaded bibtex for file {title} in page {page_idx}, number {idx}")
            good.append([f"{page_idx}/{idx}", title])
        except Exception as e:
            print(f"Error extracting BibTeX for file {title} in page {page_idx}, number {idx}:", e)
            bad.append([f"{page_idx}/{idx}", title])
            continue

    return bibtex_list

def format_bibtex_entries(bibtex_entries):
    """
    Formats a list of BibTeX entries into a single string with double newlines between entries.
    """
    return "\n\n".join(bibtex_entries)

def get_save_filename(page_start, page_end):
    """
    Generates a filename for saving BibTeX entries, including current timestamp and page range.
    """
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"bibtex_{now}_pages_{page_start}-{page_end}.bib"

def save_bibtex_to_file(bibtex_entries, filename):
    """
    Saves a list of BibTeX entries to a file.
    If no entries are provided, prints a message and returns.
    """
    if not bibtex_entries:
        print("No BibTeX entries to save.")
        return
    with open(filename, "w", encoding="utf-8") as f:
        f.write(format_bibtex_entries(bibtex_entries))
    print(f"Saved {len(bibtex_entries)} BibTeX entries to {filename}")

def main():
    """
    Main function that sets up the Selenium webdriver, encodes the query, and processes each page.
    """
    global all_bibtex, page_start, page_end, save_filename

    # Configure Chrome options for Selenium.
    options = Options()
    # options.add_argument('--headless')
    # options.add_argument('--no-sandbox')
    options.add_argument("--disable-blink-features=AutomationControlled") 
    options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument('--disable-dev-shm-usage')

    # Example proxy configuration (commented out).
    # PROXY = "120.50.18.146:58080"
    # options.add_argument(f"--proxy-server={PROXY}")

    # Initialize Chrome webdriver with specified options.
    cService = webdriver.ChromeService(executable_path='/usr/bin/chromedriver')
    driver = webdriver.Chrome(service = cService)

    # Define the search query for Google Scholar.
    query = '("dark pattern" OR "dark patterns" OR "dark design" OR "dark designs" OR "deceptive design" OR "deceptive designs" OR "manipulative design" OR "manipulative designs" OR "coercive design" OR "coercive designs" OR "dark default" OR "dark defaults" OR "dark-pattern" OR "dark-patterns") AND (experiment*)'
    encoded_query = urllib.parse.quote_plus(query)
    ylo, yhi = 2010, 2025

    # Set the page range to scrape. Adjust as needed.
    page_start = 1
    page_end = 1

    # Generate the filename for saving BibTeX entries.
    save_filename = get_save_filename(page_start, page_end)

    # Loop through each page in the specified range and scrape BibTeX entries.
    for page in range(page_start, page_end + 1):
        curr_bibtex_page = get_bibtex_in_page(driver, encoded_query, page, ylo, yhi, page == page_start, 1)
        all_bibtex += curr_bibtex_page

    # Close the webdriver when done.
    driver.quit()

# Register an exit handler to ensure BibTeX entries are saved even if the script exits unexpectedly.
def exit_handler():
    """
    Exit handler function that saves collected BibTeX entries to file.
    """
    global all_bibtex, save_filename
    save_bibtex_to_file(all_bibtex, save_filename)

atexit.register(exit_handler)

# Standard Python idiom to execute the main function when the script is run directly.
if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nInterrupted. Saving collected BibTeX entries...")
        save_bibtex_to_file(all_bibtex, save_filename)
        sys.exit(0)


