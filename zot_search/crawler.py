import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin, urlparse

# Use a set to keep track of visited URLs to avoid infinite loops and re-fetching
visited_urls = set()
# Limit the crawl depth for a "tiny" crawler
MAX_DEPTH = 2

def is_wikipedia_url(url):
    """Check if the URL is a valid English Wikipedia article URL."""
    parsed_url = urlparse(url)
    return parsed_url.netloc == 'en.wikipedia.org' and parsed_url.path.startswith('/wiki/') and ':' not in parsed_url.path

def crawl(url, height=0):
    """Fetches a Wikipedia page and extracts links recursively."""
    if url in visited_urls or height < 0:
        return

    print(f"Crawling: {url} Height: {height})")
    documents = {}

    try:
        # Add a delay to avoid overwhelming the server (be a good net citizen!)
        time.sleep(1)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url,headers=headers)
        response.raise_for_status()  # Check for bad response

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract title
        title = soup.find('h1', {'id': 'firstHeading'}).text
        documents[title] = url

        if height - 1 < 0:
            return documents

        content_div = soup.find('div', {'class': 'mw-content-container'})

        if content_div:
            for link in content_div.find_all('a', href=True):
                href = link['href']
                # Construct absolute URL
                absolute_url = urljoin(url, href)
                
                # Check if it's a valid, unvisited Wikipedia article link
                if is_wikipedia_url(absolute_url) and absolute_url not in visited_urls:
                    results = crawl(absolute_url, height - 1)
                    for doc_title, doc_url in results.items():
                        if doc_title in documents:
                            continue
                        documents[doc_title] = doc_url


    except requests.exceptions.RequestException as e:
        print(f"Error crawling {url}: {e}")

    return documents

if __name__ == "__main__":
    start_url = "https://en.wikipedia.org/wiki/Anteater"
    documents = crawl(start_url, height=1)
    print(documents)