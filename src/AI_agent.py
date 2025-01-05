from typing import List, Optional, Dict, Any
import ollama
from prompts import query_msg, combine_search, final_combine
from web_scraper import GoogleSearchScraper
import markdown
import os
from tqdm import tqdm

class Agent:
    """
    An AI agent that processes queries, performs web searches, and generates markdown responses.
    
    This class integrates with Ollama for AI processing and GoogleSearchScraper for web scraping.
    It manages the entire pipeline from query processing to final markdown generation.
    
    Attributes:
        query (str): The user's input query.
        source_links (List[str]): Collection of scraped URLs.
        markdown (str): Generated markdown content.
        markdown_path (str): Path to save the markdown file.
        pdf_path (str): Path to save the PDF file (if generated).
        scraper (GoogleSearchScraper): Instance of web scraper.
        search_limit (int): Maximum number of search results to process.
    """

    def __init__(self, query: str, search_limit: int = 3, markdown_path: str = 'report.md') -> None:
        """
        Initialize the Agent with search and processing parameters.
        
        Args:
            query (str): The user's input query.
            search_limit (int, optional): Maximum number of search results. Defaults to 3.
            markdown_path (str, optional): Path to save markdown output. Defaults to 'report.md'.
        
        Raises:
            ValueError: If query is empty or search_limit is less than 1.
        """
        if not query.strip():
            raise ValueError("Query cannot be empty")
        if search_limit < 1:
            raise ValueError("Search limit must be at least 1")
            
        self.query = query
        self.source_links: List[str] = []
        self.markdown: str = ""
        self.markdown_path = markdown_path
        self.pdf_path: str = ""
        self.scraper = GoogleSearchScraper()
        self.search_limit = search_limit

    def create_search_query(self) -> str:
        """
        Generate an optimized search query using Ollama AI.
        
        Returns:
            str: The optimized search query or error message.
        
        Raises:
            Exception: If there's an error in API communication.
        """
        user_prompt = "CREATE A GOOGLE SEARCH ENGINE PROMPT FOR THIS: " + self.query
    
        try:
            response_assistant = ollama.chat(
                model='llama3.2',
                messages=[
                    {'role': "system", 'content': query_msg}, 
                    {'role': "user", "content": user_prompt}
                ],
            )
            
            if 'message' in response_assistant and 'content' in response_assistant['message']:
                return response_assistant['message']['content']
            raise ValueError("Unexpected response format: Missing 'message' or 'content'")
        
        except Exception as e:
            print(f"Error in create_search_query: {str(e)}")
            return f"Error occurred: {str(e)}"

    def search_ai(self, finetuned_query: str) -> List[str]:
        """
        Perform web search using the finetuned query.
        
        Args:
            finetuned_query (str): The optimized search query.
            
        Returns:
            List[str]: List of discovered URLs.
            
        Raises:
            ValueError: If finetuned_query is empty.
        """
        if not finetuned_query.strip():
            raise ValueError("Finetuned query cannot be empty")
            
        print(f"Reference search prompt: {finetuned_query}. \n \n")
        
        # Remove surrounding quotes if present
        if (finetuned_query.startswith('"') and finetuned_query.endswith('"')) or \
           (finetuned_query.startswith("'") and finetuned_query.endswith("'")):
            finetuned_query = finetuned_query[1:-1]  
        
        try:
            all_urls = self.scraper.get_multiple_result(finetuned_query, self.search_limit)
            self.source_links = all_urls
            return all_urls
        except Exception as e:
            print(f"Error in search_ai: {str(e)}")
            return []

    def get_raw_filtered_data(self) -> str:
        """
        Process scraped URLs and filter relevant content using AI.
        
        Returns:
            str: Filtered and processed content from all sources.
        """
        TARGET_PROMPT = self.query
        TOKEN_LIMIT = 4096 // len(self.source_links) if self.source_links else 4096
        
        try:
            all_data = self.scraper.scrape_all_urls(self.source_links)
            
            if not all_data:
                return "No data available from the provided links."
            
            result = ""
            for data in tqdm(all_data, desc="Processing data", unit="item"):
                dat_prompt = f"TARGET_PROMPT: {TARGET_PROMPT}, TOKEN_LIMIT: {TOKEN_LIMIT}, RAW_DATA: {data}"
                
                try:
                    response = ollama.chat(
                        model='llama3.2',
                        messages=[{'role': 'system', 'content': combine_search},
                                {'role': 'user', 'content': dat_prompt}],
                    )
                    if 'message' in response and 'content' in response['message']:
                        result += response['message']['content'] + '\n\n'
                    else:
                        print("Unexpected response format in data processing")
                except Exception as e:
                    print(f"Error processing individual data item: {e}")
                    continue
                    
            return result or "No valid data could be processed."
            
        except Exception as e:
            print(f"Error in get_raw_filtered_data: {str(e)}")
            return f"Error processing data: {str(e)}"

    def final_response(self, filtered_data: str) -> str:
        """
        Generate final markdown response using processed data.
        
        Args:
            filtered_data (str): Processed and filtered content.
            
        Returns:
            str: Generated markdown content.
            
        Raises:
            ValueError: If filtered_data is empty.
            IOError: If unable to save markdown file.
        """
        if not filtered_data.strip():
            raise ValueError("Filtered data cannot be empty")
            
        try:
            response = ollama.chat(
                model='llama3.2',
                messages=[{'role': 'system', 'content': final_combine},
                        {'role': 'user', 'content': filtered_data}]
            )
            
            if 'message' not in response or 'content' not in response['message']:
                raise ValueError("Unexpected response format from Ollama")
                
            self.markdown = response['message']['content']
            print(self.markdown)
            
            # Save the content to a markdown file
            try:
                with open(self.markdown_path, 'w', encoding='utf-8') as md_file:
                    md_file.write(self.markdown)
                print(f"Markdown file saved at {self.markdown_path}")
            except IOError as e:
                print(f"Error saving markdown file: {e}")
                
            return self.markdown
            
        except Exception as e:
            print(f"Error in final_response: {str(e)}")
            return f"Error generating response: {str(e)}"