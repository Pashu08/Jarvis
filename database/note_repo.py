from database.connection import get_connection

def add_note(content):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notes (content) VALUES (?)", (content,))
    conn.commit()
    conn.close()

def get_notes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, content FROM notes ORDER BY id")
    notes = cursor.fetchall()
    conn.close()
    return notes

def get_note_by_id(note_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, content FROM notes WHERE id = ?", (note_id,))
    note = cursor.fetchone()
    conn.close()
    return note

def get_recent_notes(limit=5):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, content FROM notes ORDER BY id DESC LIMIT ?", (limit,))
    notes = cursor.fetchall()
    conn.close()
    notes.reverse()
    return notes

def update_note(note_id, new_content):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE notes SET content = ? WHERE id = ?", (new_content, note_id))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0

def search_notes_db(keyword):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, content FROM notes WHERE LOWER(content) LIKE LOWER(?)", (f"%{keyword}%",))
    results = cursor.fetchall()
    conn.close()
    return results
