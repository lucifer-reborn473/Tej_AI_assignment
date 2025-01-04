import requests 
from bs4 import BeautifulSoup
from typing import Dict, List, Optional

class GoogleSearchScraper:
    def __init__(self, headers=None):
        self.url = 'https://www.google.com/search?q='

        if not headers:
            self.headers = {
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.5',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
                }
        else:
            self.headers = headers


    def get_result(self, query:str):
        r = requests.get(self.url + query, headers=self.headers)
        assert r.status_code == 200

        soup = BeautifulSoup(r.text, 'html.parser')

        for a in soup.find('div', id='search').find_all('a'):
            try:
                href = a['href']
                assert type(href) == str

                if href.startswith('http') and 'www.google.com' not in href:
                    return href.strip()
            except:
                continue

        return None

    def get_multiple_result(self, query:str, k:int):
        r = requests.get(self.url + query, headers=self.headers)
        assert r.status_code == 200

        soup = BeautifulSoup(r.text, 'html.parser')
        results = set()

        for a in soup.find('div', id='search').find_all('a'):
            try:
                href = a['href']
                assert type(href) == str

                if href.startswith('http') and 'www.google.com' not in href:
                    if len(results) < k:
                        results.add(href.strip())
                    else:
                        return list(results)
            except:
                continue
            
        if len(results) > 0:
            return list(results)

        return None
    def get_result_with_description(self, query: str) -> Optional[Dict[str, str]]:
        """
        Get a single search result with both link and description
        
        Args:
            query (str): Search query string
            
        Returns:
            Optional[Dict[str, str]]: Dictionary containing link and description, or None if no results
        """
        r = requests.get(self.url + query, headers=self.headers)
        assert r.status_code == 200

        soup = BeautifulSoup(r.text, 'html.parser')
        search_div = soup.find('div', id='search')
        
        # Look for search result divs
        for div in search_div.find_all('div', class_='g'):
            try:
                # Find link
                link_elem = div.find('a')
                if not link_elem:
                    continue
                    
                link = link_elem['href']
                if not (link.startswith('http') and 'www.google.com' not in link):
                    continue

                # Find description
                desc_elem = div.find('div', class_='VwiC3b')
                if not desc_elem:
                    continue
                    
                description = desc_elem.get_text().strip()
                
                return {
                    "link": link.strip(),
                    "description": description
                }
                
            except Exception:
                continue
                
        return None

if __name__ == '__main__':
    search = GoogleSearchScraper()
    query = input('Query: ')

    search_result = search.get_result(query=query)
    print(f'\nResult: {search_result}\n')

    search_results = search.get_multiple_result(query=query, k=5)
    print(f'Top 5 Results: {search_results}')

    search_results= search.get_result_with_description(query=query)
    print(search_results)
