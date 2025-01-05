import ollama
from prompts import *

from web_scraper import GoogleSearchScraper
from AI_agent import Agent
from store_db import Database


def main():
    query=input("Enter which person/organization you wish to search:")
    markdown_path="assets/sample_report.md"
    assistant=Agent(query=query,search_limit=3,markdown_path=markdown_path)
    finetuned_query=assistant.create_search_query()
    print(f"the finetuned query is {finetuned_query}")
    all_links=assistant.search_ai(finetuned_query=finetuned_query)
    print(f"links of relevant sources {all_links}")
    filtered_data=assistant.get_raw_filtered_data()
    final_content=assistant.final_response(filtered_data=filtered_data)
    print('content finished')

    save=input("do you wish to save (y/n):")
    if (save=="Y" or save=="y"):
        save_path="assets/sample_save.db"
        db=Database(save_path)
        db.store_data(query=query,markdown_content=markdown_path,reference_links=all_links)


if __name__=="__main__":
    main()