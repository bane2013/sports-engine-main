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
    eastern_nba_standings = c.fetchall()

    c.execute('SELECT * FROM nba_standings WHERE conference="Western"')
    western_nba_standings = c.fetchall()

    c.execute('SELECT * FROM nhl_standings WHERE conference="Eastern"')
    eastern_nhl_standings = c.fetchall()

    c.execute('SELECT * FROM nhl_standings WHERE conference="Western"')
    western_nhl_standings = c.fetchall()

    conn.close()

    return render_template('index.html',
                           eastern_nba_standings=eastern_nba_standings, western_nba_standings=western_nba_standings,
                           eastern_nhl_standings=eastern_nhl_standings, western_nhl_standings=western_nhl_standings)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').lower()
    index = open_dir("indexdir")
    query_parser = MultifieldParser(["title", "description", "content"], index.schema)

    with index.searcher() as searcher:
        search_query = query_parser.parse(query)
        results = searcher.search(search_query, limit=10)
        return jsonify([[r.get('title', ''), r.get('link', ''), r.get('description', '')] for r in results])

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

@app.route('/videoSearch', methods=['GET'])
def video_search():
    query = request.args.get('q', '').lower()
    conn = sqlite3.connect('sports.db')
    c = conn.cursor()

    c.execute('''
    SELECT title, video_link, thumbnail_link, description
    FROM video_data
    WHERE LOWER(title) LIKE ? OR LOWER(description) LIKE ?
    LIMIT 5
    ''', (f'%{query}%', f'%{query}%'))

    results = c.fetchall()
    conn.close()

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)