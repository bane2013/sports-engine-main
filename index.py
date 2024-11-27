from whoosh.fields import Schema, TEXT, ID
from whoosh.index import create_in
from whoosh.index import open_dir
from whoosh.writing import AsyncWriter
from whoosh.qparser import MultifieldParser
from whoosh.analysis import StemmingAnalyzer
import os
import sqlite3

# schema for the index
schema = Schema(
     title=TEXT(stored=True, analyzer=StemmingAnalyzer()),
    link=ID(stored=True, unique=True),
    description=TEXT(stored=True, analyzer=StemmingAnalyzer())
    # UPDATE LINE TO INCLUDE CONTENT AFTER ADDING THE SCRAPED PAGE CONTENT TO SCHEMA ---------------
)

# create the index and populate it, only if it doesnt exist already
if not os.path.exists("indexdir"):
    os.mkdir("indexdir")

    # Create the index
    index = create_in("indexdir", schema)

    conn = sqlite3.connect('sports.db')
    cursor = conn.cursor()

    # Fetch articles
    cursor.execute("SELECT title, link, description FROM sports_data")      # UPDATE LINE TO INCLUDE CONTENT AFTER ADDING THE SCRAPED PAGE CONTENT TO SCHEMA ---------------
    articles = cursor.fetchall()
    conn.close()

    # open the index
    index = open_dir("indexdir")
    writer = AsyncWriter(index)

    # Add article entries into the index
    for article in articles:
        title, link, description = article      # UPDATE LINE TO INCLUDE CONTENT AFTER ADDING THE SCRAPED PAGE CONTENT TO SCHEMA ---------------
        writer.add_document(title=title, link=link, description=description)      # UPDATE LINE TO INCLUDE CONTENT AFTER ADDING THE SCRAPED PAGE CONTENT TO SCHEMA ---------------

    writer.commit()


index = open_dir("indexdir")
searcher = index.searcher()

query_parser = MultifieldParser(["title", "description"], index.schema)      # UPDATE LINE TO INCLUDE CONTENT AFTER ADDING THE SCRAPED PAGE CONTENT TO SCHEMA ---------------


with index.searcher() as searcher:
    query = query_parser.parse("westbrook")
    results = searcher.search(query, limit=10)

    for result in results:
        print(f"Title: {result['title']}, Link: {result['link']}")