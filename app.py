from flask import Flask, request, jsonify, render_template  # Ensure Flask imports are included
import sqlite3  # Import sqlite3 for database operations

app = Flask(__name__, template_folder='.')  # Use current directory as template folder

@app.route('/')
def index():
    # Serve the index.html file
    return render_template('index.html')

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

if __name__ == '__main__':
    app.run(debug=True)
