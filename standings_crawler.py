import requests
from bs4 import BeautifulSoup
import sqlite3

def create_database():
    """Create the database and ensure the table exists."""
    conn = sqlite3.connect('sports.db')
    c = conn.cursor()

    # Create table if it doesn't exist
    c.execute('''
    CREATE TABLE IF NOT EXISTS nba_standings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conference TEXT,
        team_name TEXT,
        wins INTEGER,
        losses INTEGER,
        win_loss_pct TEXT
    )
    ''')
    conn.commit()
    conn.close()

def crawl_standings():
    """Crawl NBA standings and save them to the database."""
    url = "https://www.basketball-reference.com/leagues/NBA_2025_standings.html"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        conferences = {
            "Eastern": "confs_standings_E",
            "Western": "confs_standings_W"
        }

        conn = sqlite3.connect('sports.db')
        c = conn.cursor()

        # Clear table to avoid duplicate data
        c.execute('DELETE FROM nba_standings')
        conn.commit()

        for conf_name, table_id in conferences.items():
            standings_table = soup.find('table', {'id': table_id})

            if standings_table:
                rows = standings_table.find('tbody').find_all('tr')

                for row in rows:
                    if 'class' in row.attrs and 'thead' in row.attrs['class']:
                        continue

                    team_name = row.find('th').get_text(strip=True)
                    cells = row.find_all('td')
                    if cells:
                        wins = int(cells[0].get_text(strip=True))
                        losses = int(cells[1].get_text(strip=True))
                        win_loss_pct = cells[2].get_text(strip=True)

                        c.execute('''
                        INSERT INTO nba_standings (conference, team_name, wins, losses, win_loss_pct)
                        VALUES (?, ?, ?, ?, ?)
                        ''', (conf_name, team_name, wins, losses, win_loss_pct))
                        conn.commit()

        conn.close()