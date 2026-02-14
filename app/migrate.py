import sqlite3
conn = sqlite3.connect("music.db")
cursor = conn.cursor()
cursor.execute("SELECT id, email FROM users;")
print(cursor.fetchall())
conn.close()
