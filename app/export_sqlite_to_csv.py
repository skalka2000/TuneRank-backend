import sqlite3
import os
import csv

# Path to your SQLite DB
DB_PATH = "music.db"

# Output folder
EXPORT_FOLDER = "sqlite_csv_exports"
os.makedirs(EXPORT_FOLDER, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall()]

for table in tables:
    print(f"Exporting table: {table}")
    cursor.execute(f"SELECT * FROM {table}")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    with open(os.path.join(EXPORT_FOLDER, f"{table}.csv"), "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(columns)  # header
        writer.writerows(rows)

conn.close()
print("\n✅ Export complete. CSVs saved to:", EXPORT_FOLDER)
