import sqlite3

# Connect to the database
conn = sqlite3.connect('sports.db')
c = conn.cursor()

# Create the sports_data table
c.execute('''
CREATE TABLE IF NOT EXISTS sports_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    link TEXT,
    description TEXT
)
''')

# Commit and close the connection
conn.commit()
conn.close()

print("Table 'sports_data' created successfully.")
