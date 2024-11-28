
from flask import Flask, request, jsonify, render_template, redirect, url_for
import sqlite3
import os

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database setup
DATABASE = 'sports_videos.db'


def init_db():
    """Initialize the SQLite database."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            tags TEXT,
            filename TEXT NOT NULL
        )
        ''')
        conn.commit()


@app.route('/')
def index():
    """Home page for uploading and searching videos."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_video():
    """Upload a new video along with metadata."""
    if 'video' not in request.files:
        return jsonify({'error': 'No video file uploaded'}), 400

    video_file = request.files['video']
    title = request.form.get('title')
    description = request.form.get('description', '')
    tags = request.form.get('tags', '')

    if not title or not video_file:
        return jsonify({'error': 'Title and video file are required'}), 400

    # Save the video file
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_file.filename)
    video_file.save(video_path)

    # Save metadata to the database
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO videos (title, description, tags, filename)
        VALUES (?, ?, ?, ?)
        ''', (title, description, tags, video_file.filename))
        conn.commit()

    return redirect(url_for('index'))


@app.route('/search', methods=['GET'])
def search_videos():
    """Search for videos by title or tags."""
    query = request.args.get('query', '')
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT id, title, description, tags, filename FROM videos
        WHERE title LIKE ? OR tags LIKE ?
        ''', (f'%{query}%', f'%{query}%'))
        results = cursor.fetchall()

    videos = [
        {
            'id': row[0],
            'title': row[1],
            'description': row[2],
            'tags': row[3],
            'filename': row[4]
        }
        for row in results
    ]

    return jsonify(videos)


@app.route('/video/<int:video_id>', methods=['GET'])
def view_video(video_id):
    """View details of a single video."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT id, title, description, tags, filename FROM videos
        WHERE id = ?
        ''', (video_id,))
        row = cursor.fetchone()

    if row is None:
        return jsonify({'error': 'Video not found'}), 404

    video = {
        'id': row[0],
        'title': row[1],
        'description': row[2],
        'tags': row[3],
        'filename': row[4]
    }

    return jsonify(video)


if __name__ == '__main__':
    # Initialize database
    init_db()

    # Start the Flask app
    app.run(debug=True)
