import sqlite3

# Connect to the database
conn = sqlite3.connect('sports.db')
c = conn.cursor()

# Sample sports data
sports_data = [
    {"title": "LeBron James Scores 40 Points", "link": "https://example.com/lebron", "description": "LeBron leads Lakers to victory."},
    {"title": "NBA Finals Game 5 Recap", "link": "https://example.com/nba-finals", "description": "An intense game between the Heat and Nuggets."}
]

# Insert data into the table
for item in sports_data:
    c.execute('''
    INSERT INTO sports_data (title, link, description)
    VALUES (?, ?, ?)
    ''', (item['title'], item['link'], item['description']))

conn.commit()
conn.close()

print("Sample data inserted successfully.")
