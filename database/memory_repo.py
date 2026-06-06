from database.connection import get_connection

def save_memory(key, value):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO memories (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def get_memory(key):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM memories WHERE key = ?", (key,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_all_memories():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM memories")
    memories = cursor.fetchall()
    conn.close()
    return memories

def update_memory(key, value):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE memories SET value = ? WHERE key = ?", (value, key))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0

def search_memories_db(keyword):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM memories WHERE LOWER(key) LIKE LOWER(?) OR LOWER(value) LIKE LOWER(?)", (f"%{keyword}%", f"%{keyword}%"))
    results = cursor.fetchall()
    conn.close()
    return results
