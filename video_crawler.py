import requests
from bs4 import BeautifulSoup
import sqlite3


def create_video_table():
    """Create the database table for storing video data."""
    conn = sqlite3.connect('sports.db')
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS video_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        src TEXT UNIQUE,
        description TEXT
    )
    ''')
    conn.commit()
    conn.close()


def crawl_videos(url, rules, source_name):
    """Crawl websites for videos and save data to the database."""
    print(f"Starting video crawl for {source_name}: {url}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch {url} - Status Code: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    items = soup.select(rules['item_selector'])
    print(f"Found {len(items)} videos on {source_name}")

    conn = sqlite3.connect('sports.db')
    c = conn.cursor()

    for item in items:
        try:
            title = item.select_one(rules['title_selector']).text.strip()
            src = item.select_one(rules['video_selector'])['src']
            description = item.select_one(rules['description_selector']).text.strip() if rules.get('description_selector') else "No Description"

            c.execute('''
            INSERT INTO video_data (title, src, description)
            VALUES (?, ?, ?)
            ''', (title, src, description))
            conn.commit()

            print(f"Saved video: {title}")
        except sqlite3.IntegrityError:
            print(f"Skipped duplicate video: {title}")
        except Exception as e:
            print(f"Error processing video: {e}")

    conn.close()
    print(f"Finished video crawl for {source_name}")


if __name__ == "__main__":
    create_video_table()

    # Define sources
    video_sources = [
        {
            "name": "NBA Videos",
            "url": "https://www.sportingnews.com/ca/nba/news/zach-lavine-addresses-trade-rumours-following-hot-season-start/42d3a8fd7fb6d63dc0d34c2a",
            "rules": {
                "item_selector": "body > div.layout-container > main > div.md\:px-3 > div > div > div > div.zephr-feature_hero",
                "title_selector": "body > div.layout-container > main > div.md\:px-3 > div > div > div > div.zephr-feature_page-title",
                "video_selector": "#botr_XmfpSu6u_DBRF0kQO_div",
                "description_selector": "body > div.layout-container > main > div.md\:px-3 > div > div > div > div.zephr-feature_article-content-body"
                "base_url": "https://www.sportingnews.com"
            }
        }
    ]

    for source in video_sources:
        crawl_videos(source['url'], source['rules'], source['name'])
