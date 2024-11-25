import sqlite3

connection = sqlite3.connect('sports.db')
c = connection.cursor()

# "sports_data" for table with news articles
# "image_data" for table with images
c.execute("SELECT * FROM image_data")

# Fetch all rows
rows = c.fetchall()

# Print the table contents
if rows:
    for row in rows:
        print(row)  # Each row is a tuple (id, title, link, description)
else:
    print("The table 'sports_data' is empty.")


connection.close()