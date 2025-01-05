import requests 
from bs4 import BeautifulSoup
from typing import Dict, List, Optional,Set
import trafilatura
from requests.exceptions import RequestException
from bs4.element import Tag
import random
from functools import wraps
import time

random_ips = [".".join(str(random.randint(0, 255)) for _ in range(4)) for _ in range(10)]
chosen_ip = random.choice(random_ips)

BROWSER_HEADERS = {
    "windows_chrome": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "X-Forwarded-For": chosen_ip  
    },
    
    "windows_firefox": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "X-Forwarded-For": chosen_ip
    },
    
    "macos_safari": {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "X-Forwarded-For": chosen_ip
    },
    
    "ios_safari": {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "X-Forwarded-For": chosen_ip
    },
    
    "android_chrome": {
        "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "X-Forwarded-For": chosen_ip
    }
}

# def respect_rate_limit(calls: int = 1, period: int = 1):
#     """
#     Decorator to implement rate limiting.
    
#     Args:
#         calls (int): Number of calls allowed
#         period (int): Time period in seconds
        
#     Returns:
#         Decorated function that respects rate limits
#     """
#     min_interval = period / float(calls)
#     last_called = [0.0]  # Using list to maintain state between calls
    
#     def decorator(func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             elapsed = time.time() - last_called[0]
#             left_to_wait = min_interval - elapsed/1e9
#             if left_to_wait > 0:
#                 time.sleep(left_to_wait)
                
#             ret = func(*args, **kwargs)
#             last_called[0] = time.time()
#             return ret
#         return wrapper
#     return decorator


class GoogleSearchScraper:
    """
    A class to scrape search results from Google and extract content from URLs.
    
    Attributes:
        url (str): Base URL for Google search
        headers (dict): HTTP headers for making requests
    """
    
    def __init__(self, headers: Optional[dict] = None) -> None:
        """
        Initialize the GoogleSearchScraper with custom headers if provided.
        
        Args:
            headers (Optional[dict]): Custom HTTP headers. If None, default headers will be used.
        """
        self.url: str = 'https://www.google.com/search?q='
        self.rate_limit=2
        if not headers:
            self.headers: dict =BROWSER_HEADERS['windows_chrome']
        else:
            self.headers = headers

    # @respect_rate_limit(calls=1, period=2)
    def get_result(self, query: str) -> Optional[str]:
        """
        Get the first valid search result for a given query.
        
        Args:
            query (str): Search query string
            
        Returns:
            Optional[str]: First valid URL found or None if no results
            
        Raises:
            RequestException: If the HTTP request fails
            AssertionError: If response status code is not 200
            AttributeError: If HTML parsing fails
        """
        try:
            time.sleep(self.rate_limit)
            response = requests.get(self.url + query, headers=self.headers)
            assert response.status_code == 200, f"HTTP request failed with status code {response.status_code}"
            
            soup = BeautifulSoup(response.text, 'html.parser')
            search_div = soup.find('div', id='search')
            if not search_div:
                return None
                
            for anchor in search_div.find_all('a'):
                try:
                    href: str = anchor['href']
                    assert isinstance(href, str), "href is not a string"
                    
                    if href.startswith('http') and 'www.google.com' not in href:
                        return href.strip()
                except (KeyError, AssertionError):
                    continue
                    
            return None
            
        except (RequestException, AssertionError, AttributeError) as e:
            raise e

    # @respect_rate_limit(calls=1, period=2)
    def get_multiple_result(self, query: str, k: int) -> Optional[List[str]]:
        """
        Get multiple valid search results for a given query.
        
        Args:
            query (str): Search query string
            k (int): Maximum number of results to return
            
        Returns:
            Optional[List[str]]: List of valid URLs found or None if no results
            
        Raises:
            RequestException: If the HTTP request fails
            AssertionError: If response status code is not 200
            AttributeError: If HTML parsing fails
        """
        try:
            time.sleep(self.rate_limit)
            response = requests.get(self.url + query, headers=self.headers)
            assert response.status_code == 200, f"HTTP request failed with status code {response.status_code}"
            
            soup = BeautifulSoup(response.text, 'html.parser')
            search_div = soup.find('div', id='search')
            if not search_div:
                return None
                
            results: Set[str] = set()
            
            for anchor in search_div.find_all('a'):
                try:
                    href: str = anchor['href']
                    assert isinstance(href, str), "href is not a string"
                    
                    if href.startswith('http') and 'www.google.com' not in href:
                        if len(results) < k:
                            results.add(href.strip())
                        else:
                            return list(results)
                except (KeyError, AssertionError):
                    continue
                    
            return list(results) if results else None
            
        except (RequestException, AssertionError, AttributeError) as e:
            raise e

    def scrape_url(self, url: str) -> Optional[str]:
        """
        Extract content from a given URL using trafilatura.
        
        Args:
            url (str): URL to scrape
            
        Returns:
            Optional[str]: Extracted content or None if extraction fails
        """
        try:
            download = trafilatura.fetch_url(url)
            if download:
                return trafilatura.extract(
                    download,
                    include_formatting=False,
                    include_links=True
                )
            return None
        except Exception:
            return None

    def scrape_all_urls(self, url_list: List[str]) -> List[Optional[str]]:
        """
        Extract content from multiple URLs.
        
        Args:
            url_list (List[str]): List of URLs to scrape
            
        Returns:
            List[Optional[str]]: List of extracted contents, None for failed extractions
        """
        results: List[Optional[str]] = []
        
        for url in url_list:
            try:
                data = self.scrape_url(url)
                results.append(data)
            except Exception:
                results.append(None)
                continue
                
        return results

if __name__=="__main__":
    query="Mr. Narendra Modi"
    search=GoogleSearchScraper(headers=BROWSER_HEADERS["windows_firefox"])
    result=search.get_multiple_result(query,2)
    print(result)
    data=search.scrape_all_urls(result)
    print(data)


