import sqlite3

DB_NAME = 'cultivation.db'

def init_db():
    """Initializes the database and ensures all columns exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 1. Create the base table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            rank TEXT DEFAULT 'Mortal',
            stage TEXT DEFAULT 'None',
            progress INTEGER DEFAULT 0,
            silver INTEGER DEFAULT 0,
            copper INTEGER DEFAULT 0,
            internal_ki REAL DEFAULT 0.0,
            external_ki REAL DEFAULT 0.0,
            ki_density REAL DEFAULT 1.0,
            ki_control REAL DEFAULT 1.0,
            vessel_cap INTEGER DEFAULT 100,
            talent TEXT DEFAULT 'None',
            constitution TEXT DEFAULT 'None',
            path TEXT DEFAULT 'None',
            family_id INTEGER DEFAULT 0,
            energy_current REAL DEFAULT 100.0,
            energy_max REAL DEFAULT 100.0,
            last_updated INTEGER DEFAULT 0,
            jail_until INTEGER DEFAULT 0,
            faint_count INTEGER DEFAULT 0
        )
    ''')

    # 2. AUTO-FIXER LOGIC: Add missing columns if they don't exist
    # This list contains all the columns we need for the Murim Engine
    required_columns = [
        ('rank', 'TEXT DEFAULT "Mortal"'),
        ('stage', 'TEXT DEFAULT "None"'),
        ('progress', 'INTEGER DEFAULT 0'),
        ('silver', 'INTEGER DEFAULT 0'),
        ('copper', 'INTEGER DEFAULT 0'),
        ('internal_ki', 'REAL DEFAULT 0.0'),
        ('external_ki', 'REAL DEFAULT 0.0'),
        ('ki_density', 'REAL DEFAULT 1.0'),
        ('ki_control', 'REAL DEFAULT 1.0'),
        ('vessel_cap', 'INTEGER DEFAULT 100'),
        ('talent', 'TEXT DEFAULT "None"'),
        ('constitution', 'TEXT DEFAULT "None"'),
        ('path', 'TEXT DEFAULT "None"'),
        ('family_id', 'INTEGER DEFAULT 0'),
        ('energy_current', 'REAL DEFAULT 100.0'),
        ('energy_max', 'REAL DEFAULT 100.0'),
        ('last_updated', 'INTEGER DEFAULT 0'),
        ('jail_until', 'INTEGER DEFAULT 0'),
        ('faint_count', 'INTEGER DEFAULT 0')
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

# --- GETTERS AND SETTERS (The "Vault Manager" Tools) ---

def get_player_data(user_id):
    """Fetches all data for a specific player."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # Allows accessing columns by name
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def update_val(user_id, column, value):
    """Updates a single specific value in the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute(f"UPDATE users SET {column} = ? WHERE user_id = ?", (value, user_id))
        conn.commit()
    except Exception as e:
        print(f"❌ Database Update Error ({column}): {e}")
    finally:
        conn.close()

def adjust_val(user_id, column, amount):
    """Adds or subtracts a value (like Silver or Ki)."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute(f"UPDATE users SET {column} = {column} + ? WHERE user_id = ?", (amount, user_id))
        conn.commit()
    except Exception as e:
        print(f"❌ Database Adjustment Error ({column}): {e}")
    finally:
        conn.close()

def create_user(user_id, talent, constitution):
    """Initializes a brand new user with their rolled Talent/Constitution."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, talent, constitution) 
        VALUES (?, ?, ?)
    ''', (user_id, talent, constitution))
    conn.commit()
    conn.close()
