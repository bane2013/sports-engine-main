from flask import Flask, request, jsonify, render_template  # Ensure Flask imports are included
import sqlite3  # Import sqlite3 for database operations

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
    conn = sqlite3.connect('sports.db')
    c = conn.cursor()

    c.execute('''
    SELECT title, link, description
    FROM sports_data
    WHERE LOWER(title) LIKE ? OR LOWER(description) LIKE ?
    ''', (f'%{query}%', f'%{query}%'))
    results = c.fetchall()
    conn.close()

    return jsonify(results)

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