import sqlite3

DB_NAME = 'cultivation.db'

def init_db():
    """Initializes the database with Whole Number support and new columns."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 1. Create/Update the base table
    # Changed REAL to INTEGER for Ki and Energy
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            rank TEXT DEFAULT 'Mortal',
            stage TEXT DEFAULT 'None',
            progress INTEGER DEFAULT 0,
            silver INTEGER DEFAULT 0,
            copper INTEGER DEFAULT 0,
            internal_ki INTEGER DEFAULT 0,
            external_ki INTEGER DEFAULT 0,
            vessel_cap INTEGER DEFAULT 100,
            talent TEXT DEFAULT 'None',
            constitution TEXT DEFAULT 'None',
            path TEXT DEFAULT 'Neutral',
            energy_current INTEGER DEFAULT 100,
            energy_max INTEGER DEFAULT 100,
            mantra TEXT DEFAULT 'The path to immortality begins with a single step.',
            last_meditate INTEGER DEFAULT 0,
            last_updated INTEGER DEFAULT 0,
            jail_until INTEGER DEFAULT 0
        )
    ''')

    # 2. THE AUTO-FIXER: Ensures your current DB gets the new columns
    required_columns = [
        ('stage', "TEXT DEFAULT 'None'"),
        ('mantra', "TEXT DEFAULT 'The path to immortality begins with a single step.'"),
        ('last_meditate', "INTEGER DEFAULT 0"),
        ('external_ki', "INTEGER DEFAULT 0"),
        ('internal_ki', "INTEGER DEFAULT 0"),
        ('path', "TEXT DEFAULT 'Neutral'"),
        # Ensuring existing stats are converted to integers logic-wise in code, 
        # but adding them here just in case.
        ('copper', "INTEGER DEFAULT 0"),
        ('silver', "INTEGER DEFAULT 0")
    ]

    cursor.execute(f"PRAGMA table_info(users)")
    existing_columns = [info[1] for info in cursor.fetchall()]

    for col_name, col_type in required_columns:
        if col_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
                print(f"🔧 [Database] Added missing column: {col_name}")
            except Exception as e:
                print(f"❌ Error adding column {col_name}: {e}")

    conn.commit()
    conn.close()

# --- VAULT TOOLS ---

def get_player_data(user_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    res = cursor.fetchone()
    conn.close()
    return res

def update_val(user_id, column, value):
    """Updates a value. Code will pass integers to ensure whole numbers."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute(f"UPDATE users SET {column} = ? WHERE user_id = ?", (value, user_id))
        conn.commit()
    except Exception as e:
        print(f"❌ DB Error: {e}")
    finally:
        conn.close()

def adjust_val(user_id, column, amount):
    """Adjusts a value (Copper, Silver, Ki)."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute(f"UPDATE users SET {column} = {column} + ? WHERE user_id = ?", (amount, user_id))
        conn.commit()
    except Exception as e:
        print(f"❌ DB Error: {e}")
    finally:
        conn.close()

def create_user(user_id, talent, constitution):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, talent, constitution) 
        VALUES (?, ?, ?)
    ''', (user_id, talent, constitution))
    conn.commit()
    conn.close()

def delete_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
