# Tej_AI_assignment

The following assignment involves developing an AI research agent with the following capabilities.

## Features and Capabilities

### 1. Web Search and Report Generation

- Perform web searches on any given topic.
- Generate a detailed report on the searched topic.
- Include source links for all referenced information.

### 2. Organization Data Fetch and Storage

- Accept an organization (political) name as input.
- Fetch open-source details about the organization (news, posts, wiki), including information about its leaders and members.
- Fetch detailed information about each leader/member of that organization.
- Store the retrieved data in a database for future reference.

### Exclusive Features

- **Rate-Limit Handling**: Implements robust mechanisms to handle scraper rate limits effectively.
- **Advanced AI Integration**: Utilizes the LLaMA 3.2 model via the Ollama environment to power the assistant.
- **Markdown Report Generation**: Reports are generated in markdown format, ensuring easy readability and formatting.
- **Database Storage**: Generated reports and fetched data can be saved in an SQLite database for future retrieval.

## Components

- **Google Web Scraper**: Custom-built scraper to fetch data from Google searches.
- **AI Agent**: Exclusively uses the scraper to fetch data and prepare a well-drafted, insightful report.
- **Database Class**: Leverages SQLite to store the scraped and processed data for further use.

## Installation

Follow these steps to set up and run the project:

1. Clone the repository:

   ```bash
   git clone <repository_url>
   ```
2. Create a Conda environment:

   ```bash
   conda create -n tej_ai_env python=3.12
   conda activate tej_ai_env
   ```
3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```
4. Run the backend implementation demo:

   ```bash
   python src/demo.py
   ```
5. Launch the Streamlit app:

   ```bash
   streamlit run src/app.py
   ```

## Pending/Future Works

- **Multithreading**: Implement a multithreading approach to enhance performance and efficiency.
- **UI Enhancements**: Add more interactive and user-friendly features to the Streamlit app.
- **Extended Database Functionality**: Include advanced querying options for stored data.

---

Feel free to contribute to the project or raise issues if you encounter any challenges!
