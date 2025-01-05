from typing import List, Tuple, Optional, Any
import sqlite3
import markdown
import json
from sqlite3 import Connection, Cursor

class Database:
    """
    A class to manage database operations for storing and retrieving response data.
    
    This class provides functionality to store and retrieve markdown content, queries,
    reference links in a SQLite database.
    
    Attributes:
        DB (str): The name/path of the SQLite database file.
    """

    def __init__(self, DB_NAME: str = "response.db") -> None:
        """
        Initialize the Database instance and create the required table if it doesn't exist.
        
        Args:
            DB_NAME (str, optional): Name of the database file. Defaults to "response.db".
        
        Raises:
            sqlite3.Error: If there's an error creating the database or table.
        """
        self.DB = DB_NAME
        try:
            conn = sqlite3.connect(self.DB)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    markdown_content TEXT NOT NULL,
                    reference_links TEXT,  -- Stored as JSON string
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to initialize database: {str(e)}")
        finally:
            conn.close()

    def store_data(self, query: str, markdown_content: str, reference_links: List[str]) -> None:
        """
        Store response data in the database.
        
        Args:
            query (str): The search query or question.
            markdown_content (str): The markdown formatted content.
            reference_links (List[str]): List of reference URLs.
            
        Raises:
            TypeError: If any input parameter is of incorrect type.
            sqlite3.Error: If there's an error during database operation.
        """
        # Type checking
        if not isinstance(query, str):
            raise TypeError("Query must be a string")
        if not isinstance(markdown_content, str):
            raise TypeError("Markdown content must be a string")
        if not isinstance(reference_links, list) or not all(isinstance(link, str) for link in reference_links):
            raise TypeError("Reference links must be a list of strings")
        
        # Convert reference_links to JSON
        reference_links_json = json.dumps(reference_links)

        try:
            conn = sqlite3.connect(self.DB)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO responses (query, markdown_content, reference_links)
                VALUES (?, ?, ?)
            ''', (query, markdown_content, reference_links_json))
            conn.commit()
            print(f"Response data stored in {self.DB}")
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to store data: {str(e)}")
        finally:
            conn.close()

    def fetch_all(self) -> List[Tuple]:
        """
        Fetch all rows from the responses table.
        
        Returns:
            List[Tuple]: List of tuples containing all response records.
            
        Raises:
            sqlite3.Error: If there's an error during database operation.
        """
        try:
            conn = sqlite3.connect(self.DB)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM responses')
            rows = cursor.fetchall()
            return rows
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to fetch data: {str(e)}")
        finally:
            conn.close()

    def fetch_by_id(self, record_id: int) -> Optional[Tuple]:
        """
        Fetch a single row by ID.
        
        Args:
            record_id (int): The ID of the record to fetch.
            
        Returns:
            Optional[Tuple]: The requested record as a tuple, or None if not found.
            
        Raises:
            TypeError: If record_id is not an integer.
            sqlite3.Error: If there's an error during database operation.
        """
        if not isinstance(record_id, int):
            raise TypeError("Record ID must be an integer")

        try:
            conn = sqlite3.connect(self.DB)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM responses WHERE id = ?', (record_id,))
            row = cursor.fetchone()
            return row
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to fetch record {record_id}: {str(e)}")
        finally:
            conn.close()