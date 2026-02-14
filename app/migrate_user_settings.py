import sqlite3

DB_PATH = "music.db"  # <-- change if needed


def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1️⃣ Check if column exists
    cursor.execute("PRAGMA table_info(user_settings)")
    columns = [row[1] for row in cursor.fetchall()]

    if "rating_floor" not in columns:
        print("rating_floor column does not exist. Nothing to do.")
        conn.close()
        return

    print("Removing rating_floor column...")

    # 2️⃣ Create new table WITHOUT rating_floor
    cursor.execute("""
        CREATE TABLE user_settings_new (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL UNIQUE,
            average_power FLOAT,
            greatness_threshold FLOAT,
            scaling_factor FLOAT,
            steep_factor FLOAT,
            average_rating_weight FLOAT,
            interlude_weight FLOAT
        )
    """)

    # 3️⃣ Copy data (excluding rating_floor)
    cursor.execute("""
        INSERT INTO user_settings_new (
            id,
            user_id,
            average_power,
            greatness_threshold,
            scaling_factor,
            steep_factor,
            average_rating_weight,
            interlude_weight
        )
        SELECT
            id,
            user_id,
            average_power,
            greatness_threshold,
            scaling_factor,
            steep_factor,
            average_rating_weight,
            interlude_weight
        FROM user_settings
    """)

    # 4️⃣ Drop old table
    cursor.execute("DROP TABLE user_settings")

    # 5️⃣ Rename new table
    cursor.execute("ALTER TABLE user_settings_new RENAME TO user_settings")

    conn.commit()
    conn.close()

    print("Migration complete. rating_floor removed.")


if __name__ == "__main__":
    main()
