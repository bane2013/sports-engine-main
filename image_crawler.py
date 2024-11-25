import requests
from bs4 import BeautifulSoup
import sqlite3


def create_image_table():
    """Create the database table for storing image data."""
    conn = sqlite3.connect('sports.db')
    c = conn.cursor()

    # Create table if it doesn't exist
    c.execute('''
    CREATE TABLE IF NOT EXISTS image_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        src TEXT UNIQUE,
        description TEXT
    )
    ''')
    conn.commit()
    conn.close()


def fetch_description(link):
    """Follow the image link to fetch the description."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(link, headers=headers)
        if response.status_code != 200:
            return "No Description"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        # Adjust this selector based on where the description is located on the linked page
        description_element = soup.select_one("#imagedetailsdiv > div:nth-child(4) > p:nth-child(2)")
        return description_element.text.strip() if description_element else "No Description"
    except Exception as e:
        print(f"Error fetching description from {link}: {e}")
        return "No Description"


def crawl_images(url, rules, source_name):
    """Crawl websites for images and save data to the database."""
    print(f"Starting image crawl for {source_name}: {url}")

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
            # Extract the title from img.alt
            img_element = item.select_one(rules.get('img_selector'))
            title = img_element['alt'].strip() if img_element and 'alt' in img_element.attrs else "No Title"

            # Extract the image link (src)
            image_link = img_element['src'] if img_element and 'src' in img_element.attrs else "No Image Link"

            # Fetch the description by following the link
            a_container = item.select_one(rules.get('description_link_selector'))
            description_link = a_container['href'].strip() if a_container and 'href' in a_container.attrs else "No Description Link"

            # Handle relative links
            if description_link.startswith('/'):
                description_link = rules.get('base_url', '') + description_link

            description = fetch_description(description_link) if description_link != "No Link" else "No Description"
            description = description.split("NOTE TO USER")[0]

            # Insert the data into the database
            c.execute('''
            INSERT INTO image_data (title, src, description)
            VALUES (?, ?, ?)
            ''', (title, image_link, description))
            conn.commit()

            print(f"Title: {title}, \nImage src: {image_link}, \nDescription link: {description_link}, \nDescription: {description}\n----------------------------------------------------")
        except sqlite3.IntegrityError:
            print(f"Skipped duplicate image: {image_link} from {source_name}")
        except Exception as e:
            print(f"Error processing image: {e} from {source_name}")

    conn.close()
    print(f"Finished image crawl for {source_name}")

# Configuration for image sources
image_sources = [
    {
        "name": "NBA Images",
        "url": "https://photostore.nba.com/collections/nba+photos?page=1",
        "rules": {
            "item_selector": "#imageFlowContainerDiv > div > div.flowImageContainerDiv",
            "description_link_selector": "#imageFlowContainerDiv > div > div.flowImageContainerDiv > a",
            "img_selector": "#imageFlowContainerDiv > div > div.flowImageContainerDiv > a > img",
            "base_url": "https://photostore.nba.com"
        }
    },
    {
        "name": "NBA Images",
        "url": "https://photostore.nba.com/collections/nba+photos?page=2",
        "rules": {
            "item_selector": "#imageFlowContainerDiv > div > div.flowImageContainerDiv",
            "description_link_selector": "#imageFlowContainerDiv > div > div.flowImageContainerDiv > a",
            "img_selector": "#imageFlowContainerDiv > div > div.flowImageContainerDiv > a > img", 
            "base_url": "https://photostore.nba.com"
        }
    },
    {
        "name": "NBA Images",
        "url": "https://photostore.nba.com/collections/nba+photos?page=3",
        "rules": {
            "item_selector": "#imageFlowContainerDiv > div > div.flowImageContainerDiv",
            "description_link_selector": "#imageFlowContainerDiv > div > div.flowImageContainerDiv > a",
            "img_selector": "#imageFlowContainerDiv > div > div.flowImageContainerDiv > a > img",
            "base_url": "https://photostore.nba.com"
        }
    }
]

if __name__ == "__main__":
    create_image_table()

    for source in image_sources:
        crawl_images(source['url'], source['rules'], source['name'])
