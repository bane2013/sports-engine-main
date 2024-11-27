import requests
from bs4 import BeautifulSoup
import sqlite3
import logging

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
    """Crawl the website and save data to the database."""
    print(f"Starting crawl for {source_name}: {url}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch {url} - Status Code: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    items = soup.select(rules['item_selector'])
    print(f"Found {len(items)} items on {source_name}")

    conn = sqlite3.connect('sports.db')
    c = conn.cursor()

    for item in items:
        try:
            # Extract the title
            title_element = item.select_one(rules.get('title_selector'))
            title = title_element.text.strip() if title_element else None

            # Extract the link
            link_element = item.select_one(rules.get('link_selector'))
            link = link_element['href'] if link_element and 'href' in link_element.attrs else None

            # Handle relative links
            if link and link.startswith('/'):
                link = rules['base_url'] + link

            # Extract description if available
            description = None
            if rules.get('description_selector'):
                description_element = item.select_one(rules['description_selector'])
                description = description_element.text.strip() if description_element else "No Description"

            # Save the data to the database
            c.execute('''
                INSERT INTO sports_data (title, link, description, source)
                VALUES (?, ?, ?, ?)
            ''', (title, link, description or "No Description", source_name))
            conn.commit()

            print(f"Saved: {title} from {source_name}")
        except sqlite3.IntegrityError:
            print(f"Skipped duplicate: {title} from {source_name}")
        except Exception as e:
            logging.error(f"Error processing item from {source_name}: {e}\nItem HTML: {item.prettify()}")
            print(f"Error processing item from {source_name}: {e}")

    conn.close()
    print(f"Finished crawl for {source_name}")





# Configuration for NHL.com
sources = [

#Main Sports Website news!

#NHL.COM SITE FOR NHL NEWS
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

#NBA.COM SITE FOR NBA NEWS
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
    },

#NFL.COM SITE FOR NFL NEWS!
    {
        "name": "NFL news on NFL!!!!!",
        "url": "https://www.nfl.com/news/all-news",
        "rules": {
            "item_selector": "div.d3-o-media-object.d3-o-media-object--vertical.d3-o-content-tray__card",  # Main container for each article
            "title_selector": "h3.d3-o-media-object__title",  # Selector for the title
            "link_selector": "a",  # Selector for the link
            "description_selector": None,  # No explicit description available
            "base_url": "https://www.nfl.com"  # Base URL for relative links
        }
    },

#TheScore.COM SITE FOR NFL NEWS!
    {
        "name": "NFL",
        "url": "https://www.thescore.com/nfl/news",
        "rules": {
            "item_selector": "div.masonry__gridItem--3gUaq",  # Main container for each article
            "title_selector": "div.jsx-403783000.title",      # Selector for the title
            "link_selector": "a",                            # Selector for the link
            "description_selector": None,                    # No description is visible
            "base_url": "https://www.thescore.com"           # Base URL for relative links
        }
    },

#TheScore.com SITE FOR NBA NEWS!
    {
        "name": "NBA news on TheScore",
        "url": "https://www.thescore.com/nba/news",
        "rules": {
            "item_selector": "div.masonry__gridItem--3gUaq",  # Main container for each article
            "title_selector": "div.jsx-403783000.title",  # Selector for the article title
            "link_selector": "a",  # Selector for the article link
            "description_selector": None,  # No description available in the HTML
            "base_url": "https://www.thescore.com"  # Base URL for relative links
        }
    },

#TheScore.com SITE FOR NHL NEWS!
    {
        "name": "NHL",
        "url": "https://www.thescore.com/nhl/news",
        "rules": {
            "item_selector": "div.masonry__gridItem--3gUaq",  # Main container for each article
            "title_selector": "div.jsx-403783000.title",  # Selector for the article title
            "link_selector": "a",  # Selector for the article link
            "description_selector": None,  # No description available in the HTML
            "base_url": "https://www.thescore.com"  # Base URL for relative links
        }
    }

]

if __name__ == "__main__":
    create_database()

    for source in sources:
        crawl_website(source['url'], source['rules'], source['name'])
