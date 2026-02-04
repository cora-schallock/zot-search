import requests
from bs4 import BeautifulSoup

def scrape_wiki_page(url):
    # Set a user-agent to abide by Wikipedia's robots policy
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title
        title = soup.find('h1', {'id': 'firstHeading'}).text
        print(f"Title: {title}")
        
        # Extract paragraphs (removing references like [1], [2])
        paragraphs = soup.find('div', {'class': 'mw-content-container'}).find_all('p')
        content = ""
        for p in paragraphs:
            content += p.text + '\n'
        
        # Clean up citation bracket references
        import re
        content = re.sub(r'\[.*?\]', '', content)
        return content
        
    else:
        print("Failed to retrieve page")
        return ""

if __name__ == "__main__":
    test_page = "https://en.wikipedia.org/wiki/Anteater"
    scrape_wiki_page(test_page)
