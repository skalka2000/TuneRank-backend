import sqlite3

DB_PATH = "music.db"

def column_exists(cursor, table: str, column: str) -> bool:
    cursor.execute(f"PRAGMA table_info({table});")
    return any(row[1] == column for row in cursor.fetchall())

def run():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # --- 1) songs.song_type ---
    if not column_exists(cursor, "songs", "song_type"):
        print("Adding songs.song_type...")
        cursor.execute("ALTER TABLE songs ADD COLUMN song_type TEXT NOT NULL DEFAULT 'song';")
    else:
        print("songs.song_type already exists.")

    # Backfill from old boolean if it exists
    if column_exists(cursor, "songs", "is_interlude"):
        print("Backfilling songs.song_type from songs.is_interlude...")
        cursor.execute("""
            UPDATE songs
            SET song_type = 'interlude'
            WHERE is_interlude = 1 AND song_type = 'song';
        """)
    else:
        print("songs.is_interlude not found; skipping backfill from it.")

    # Ensure no NULLs (shouldn't happen because NOT NULL + default, but just in case)
    cursor.execute("UPDATE songs SET song_type = 'song' WHERE song_type IS NULL OR song_type = '';")

    # --- 2) user_settings.epic_weight ---
    if not column_exists(cursor, "user_settings", "epic_weight"):
        print("Adding user_settings.epic_weight...")
        cursor.execute("ALTER TABLE user_settings ADD COLUMN epic_weight REAL NOT NULL DEFAULT 2.0;")
    else:
        print("user_settings.epic_weight already exists.")

    # If you have existing rows and want to ensure they all have 2.0 (again, just in case)
    cursor.execute("UPDATE user_settings SET epic_weight = 2.0 WHERE epic_weight IS NULL;")

    conn.commit()

    # Quick sanity prints
    cursor.execute("PRAGMA table_info(songs);")
    print("songs columns:", [c[1] for c in cursor.fetchall()])

    cursor.execute("PRAGMA table_info(user_settings);")
    print("user_settings columns:", [c[1] for c in cursor.fetchall()])

    cursor.execute("SELECT id, title, song_type FROM songs LIMIT 10;")
    print("sample songs:", cursor.fetchall())

    cursor.execute("SELECT id, user_id, epic_weight FROM user_settings LIMIT 10;")
    print("sample settings:", cursor.fetchall())

    conn.close()
    print("Done.")

if __name__ == "__main__":
    run()
