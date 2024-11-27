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

    c.execute('''
    CREATE TABLE IF NOT EXISTS nhl_standings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conference TEXT,
        team_name TEXT,
        wins INTEGER,
        losses INTEGER,
        overtime_losses INTEGER,
        points INTEGER
    )
    ''')
    conn.commit()
    conn.close()

def crawl_standings():
    """Crawl NBA standings and save them to the database."""
    nba_url = "https://www.basketball-reference.com/leagues/NBA_2025_standings.html"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    response = requests.get(nba_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        conferences = {
            "Eastern": "confs_standings_E",
            "Western": "confs_standings_W"
        }

        conn = sqlite3.connect('sports.db')
        c = conn.cursor()

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

    nhl_url = "https://www.hockey-reference.com/leagues/NHL_2025.html"
    response = requests.get(nhl_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        nhl_conferences = {
            "Eastern": "standings_EAS",
            "Western": "standings_WES"
        }

        conn = sqlite3.connect('sports.db')
        c = conn.cursor()

        c.execute('DELETE FROM nhl_standings')
        conn.commit()

        all_teams = [] 

        for conf_name, table_id in nhl_conferences.items():
            standings_table = soup.find('table', {'id': table_id})

            if standings_table:
                rows = standings_table.find('tbody').find_all('tr')

                for row in rows:
                    if 'class' in row.attrs and 'thead' in row.attrs['class']:
                        continue

                    team_name = row.find('th').get_text(strip=True)
                    cells = row.find_all('td')
                    if cells:
                        wins = int(cells[1].get_text(strip=True))
                        losses = int(cells[2].get_text(strip=True))
                        overtime_losses = int(cells[3].get_text(strip=True))
                        points = int(cells[4].get_text(strip=True))

                        all_teams.append((conf_name, team_name, wins, losses, overtime_losses, points))

        all_teams.sort(key=lambda x: (x[0], x[5]), reverse=True)

        for data in all_teams:
            c.execute('''
            INSERT INTO nhl_standings (conference, team_name, wins, losses, overtime_losses, points)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', data)
            conn.commit()

        conn.close()