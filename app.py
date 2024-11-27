from flask import Flask, request, jsonify, render_template  # Ensure Flask imports are included
import sqlite3  # Import sqlite3 for database operations
from whoosh.qparser import MultifieldParser
from whoosh.index import open_dir

app = Flask(__name__, template_folder='.')  # Use current directory as template folder

@app.route('/')
def index():
    """Render the index page with standings data."""
    conn = sqlite3.connect('sports.db')
    c = conn.cursor()

    c.execute('SELECT * FROM nba_standings WHERE conference="Eastern"')
    eastern_standings = c.fetchall()

    c.execute('SELECT * FROM nba_standings WHERE conference="Western"')
    western_standings = c.fetchall()

    conn.close()

    return render_template('index.html', eastern_standings=eastern_standings, western_standings=western_standings)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').lower()
    index = open_dir("indexdir")
    query_parser = MultifieldParser(["title", "description"], index.schema)     # UPDATE LINE TO INCLUDE CONTENT AFTER ADDING THE SCRAPED PAGE CONTENT TO SCHEMA ---------------

    with index.searcher() as searcher:
        search_query = query_parser.parse(query)
        results = searcher.search(search_query, limit=10)
        return jsonify([[r['title'], r['link'], r['description']] for r in results])

@app.route('/imageSearch', methods=['GET'])
def image_search():
    query = request.args.get('q', '').lower()
    conn = sqlite3.connect('sports.db')
    c = conn.cursor()

    c.execute('''
    SELECT title, src, description
    FROM image_data
    WHERE LOWER(title) LIKE ? OR LOWER(description) LIKE ?
    LIMIT 5
    ''', (f'%{query}%', f'%{query}%'))
    
    results = c.fetchall()
    conn.close()

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)