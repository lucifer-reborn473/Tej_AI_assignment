import streamlit as st
import ollama
from prompts import *

from web_scraper import GoogleSearchScraper
from AI_agent import Agent
from store_db import Database

def main():
    # Add Streamlit title
    st.title("AI Research Agent")

    # Create chatbox where the user can type the text
    query = st.text_input("Enter your query:")
    search_limit = st.slider("Select search limit:", min_value=1, max_value=8, value=3)
    markdown_path = "assets/sample_report_1.md"

    # If the user enters a query, proceed with the assistant logic
    if query:
        assistant = Agent(query=query, search_limit=search_limit, markdown_path=markdown_path)

        # Generate a fine-tuned query
        finetuned_query = assistant.create_search_query()

        # Create an optional dropdown to display the fine-tuned query
        with st.expander("Fine-tuned Query"):
            st.write(finetuned_query)

        # Search for relevant sources
        all_links = assistant.search_ai(finetuned_query=finetuned_query)

        # Display the sources in another dropdown
        with st.expander("Relevant Sources"):
            for link in all_links:
                st.write(link)

        # Indicate that the final report is being processed
        with st.spinner("Processing final report..."):
            filtered_data = assistant.get_raw_filtered_data()
            final_content = assistant.final_response(filtered_data=filtered_data)

        st.success("Content generation finished!")

        # Display the markdown file's content (both code and formatted view)
        with open(markdown_path, "r") as file:
            markdown_content = file.read()

        st.subheader("Formatted Markdown Content")
        st.markdown(markdown_content, unsafe_allow_html=True)

        st.subheader("Markdown Code")
        st.code(markdown_content, language="markdown")

        save = st.radio("Do you wish to save the report?", ("Yes", "No"))
        if save == "Yes":
            save_path = "assets/sample_save_1.db"
            db = Database(save_path)
            db.store_data(query=query, markdown_content=markdown_content, reference_links=all_links)
            st.success(f"Report successfully saved to {save_path}")         
        
        st.download_button(
                label="Download Markdown Report",
                data=markdown_content,
                file_name="report.md",
                mime="text/markdown"
            )
        


if __name__ == "__main__":
    main()
