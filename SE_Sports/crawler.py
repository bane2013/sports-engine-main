import requests
from bs4 import BeautifulSoup
import sqlite3


def create_database():
    """Create the database and ensure the table exists."""
    conn = sqlite3.connect('sports.db')
    c = conn.cursor()

    # Create table if it doesn't exist
    c.execute('''
    CREATE TABLE IF NOT EXISTS sports_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT UNIQUE,
        link TEXT,
        description TEXT,
        source TEXT
    )
    ''')
    conn.commit()
    conn.close()


def crawl_website(url, rules, source_name):
    """Crawl NBA.com and save data to the database."""
    print(f"Starting crawl for {source_name}: {url}")

    # Set headers for the request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    # Fetch the webpage
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch {url} - Status Code: {response.status_code}")
        return

    # Parse the webpage using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    items = soup.select(rules['item_selector'])
    print(f"Found {len(items)} items on {source_name}")

    conn = sqlite3.connect('sports.db')
    c = conn.cursor()

    for item in items:
        try:
            # Extract the title
            title_element = item.select_one(rules.get('title_selector')) or item.select_one("h3.Text_text__I2GnQ")
            title = title_element.text.strip() if title_element else "No Title"

            # Skip entries without meaningful titles
            if not title or title.isspace() or title == "No Title":
                print(f"Skipped item with empty or missing title on {source_name}.")
                continue

            # Extract the link
            link_element = item.select_one(rules.get('link_selector'))
            link = link_element['href'] if link_element else "No Link"

            # Handle relative links
            if link.startswith('/'):
                link = rules.get('base_url', '') + link

            # Extract the description
            description_element = item.select_one(rules.get('description_selector')) or item.select_one("p.Text_text__I2GnQ")
            description = description_element.text.strip() if description_element else "No Description"

            # Insert the data into the database
            c.execute('''
            INSERT INTO sports_data (title, link, description, source)
            VALUES (?, ?, ?, ?)
            ''', (title, link, description, source_name))
            conn.commit()

            print(f"Saved: {title} from {source_name}")
        except sqlite3.IntegrityError:
            print(f"Skipped duplicate: {title} from {source_name}")
        except Exception as e:
            print(f"Error processing item: {e} from {source_name}")

    conn.close()
    print(f"Finished crawl for {source_name}")



# Configuration for NHL.com
sources = [

    {
        "name": "NHL",
        "url": "https://www.nhl.com/news",
        "rules": {
            "item_selector": "a.nhl-c-card-wrap",  # Main container for each article
            "title_selector": "h3.fa-text__title",  # Selector for the title
            "link_selector": "a.nhl-c-card-wrap",  # Selector for the link
            "description_selector": "div.fa-text__body",  # Selector for the description
            "base_url": "https://www.nhl.com"  # Base URL for relative links
        }
    },

    {
        "name": "NBA",
        "url": "https://www.nba.com/news",
        "rules": {
            "item_selector": "article.ArticleTile_tileArticle__XV7_D, section.NewsHero_newsBase__wENDX",  # Expanded to include featured articles
            "title_selector": "span.MultilineEllipsis_ellipsis__1H7z, h3.Text_text__I2GnQ",  # Handles regular and featured titles
            "link_selector": "a.Anchor_anchor__cSc3P",  # Selector for the link
            "description_selector": "p.Text_text__I2GnQ.ArticleTile_tileSub__kiMA0",  # Selector for the description
            "base_url": "https://www.nba.com"  # Base URL for relative links
        }
    }

]

if __name__ == "__main__":
    create_database()

    for source in sources:
        crawl_website(source['url'], source['rules'], source['name'])
