from core.database import get_connection

def save_memory(key, value):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO memories (key, value)
    VALUES (?, ?)
    """, (key, value))
    conn.commit()
    conn.close()

def get_memory(key):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT value
    FROM memories
    WHERE key = ?
    """, (key,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    return None

def get_all_memories():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT key, value
    FROM memories
    """)
    memories = cursor.fetchall()
    conn.close()
    return memories

def update_memory(key, value):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE memories
    SET value = ?
    WHERE key = ?
    """, (value, key))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0

def add_note(content):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO notes (content)
    VALUES (?)
    """, (content,))
    conn.commit()
    conn.close()

def get_notes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, content
    FROM notes
    ORDER BY id
    """)
    notes = cursor.fetchall()
    conn.close()
    return notes

def get_note_by_id(note_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, content
    FROM notes
    WHERE id = ?
    """, (note_id,))
    note = cursor.fetchone()
    conn.close()
    return note

def get_recent_notes(limit=5):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, content
    FROM notes
    ORDER BY id DESC
    LIMIT ?
    """, (limit,))
    notes = cursor.fetchall()
    conn.close()
    notes.reverse()
    return notes

def update_note(note_id, new_content):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE notes
    SET content = ?
    WHERE id = ?
    """, (new_content, note_id))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0

def add_task(task):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO tasks (task)
    VALUES (?)
    """, (task,))
    conn.commit()
    conn.close()

def get_tasks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, task, completed
    FROM tasks
    ORDER BY id
    """)
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def get_task_by_id(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, task, completed
    FROM tasks
    WHERE id = ?
    """, (task_id,))
    task = cursor.fetchone()
    conn.close()
    return task

def complete_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE tasks
    SET completed = 1
    WHERE id = ?
    """, (task_id,))
    conn.commit()
    conn.close()

def update_task(task_id, new_task):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE tasks
    SET task = ?
    WHERE id = ?
    """, (new_task, task_id))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0

def delete_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    DELETE FROM tasks
    WHERE id = ?
    """, (task_id,))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0

def add_project(name, description=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO projects (name, description)
    VALUES (?, ?)
    """, (name, description))
    conn.commit()
    conn.close()

def get_projects():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, name, description
    FROM projects
    ORDER BY id
    """)
    projects = cursor.fetchall()
    conn.close()
    return projects

def get_project_by_name(project_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, name, description
    FROM projects
    WHERE LOWER(name) = LOWER(?)
    """, (project_name,))
    project = cursor.fetchone()
    conn.close()
    return project

def update_project_description(project_name, description):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE projects
    SET description = ?
    WHERE LOWER(name) = LOWER(?)
    """, (description, project_name))
    conn.commit()
    conn.close()

def update_project_name(old_name, new_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE projects
    SET name = ?
    WHERE LOWER(name) = LOWER(?)
    """, (new_name, old_name))
    rows_affected = cursor.rowcount
    if rows_affected > 0:
        cursor.execute("""
        UPDATE project_tasks
        SET project_name = ?
        WHERE LOWER(project_name) = LOWER(?)
        """, (new_name, old_name))
    conn.commit()
    conn.close()
    return rows_affected > 0

def add_project_task(project_name, task):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO project_tasks (project_name, task)
    VALUES (?, ?)
    """, (project_name, task))
    conn.commit()
    conn.close()

def get_project_tasks(project_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, task, completed
    FROM project_tasks
    WHERE LOWER(project_name) = LOWER(?)
    ORDER BY id
    """, (project_name,))
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def get_project_task_by_id(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, task, project_name, completed
    FROM project_tasks
    WHERE id = ?
    """, (task_id,))
    task = cursor.fetchone()
    conn.close()
    return task

def complete_project_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE project_tasks
    SET completed = 1
    WHERE id = ?
    """, (task_id,))
    conn.commit()
    conn.close()

def update_project_task(task_id, new_task):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE project_tasks
    SET task = ?
    WHERE id = ?
    """, (new_task, task_id))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0

def delete_project_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    DELETE FROM project_tasks
    WHERE id = ?
    """, (task_id,))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0

def delete_project(project_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    DELETE FROM project_tasks
    WHERE LOWER(project_name) = LOWER(?)
    """, (project_name,))
    cursor.execute("""
    DELETE FROM projects
    WHERE LOWER(name) = LOWER(?)
    """, (project_name,))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0

def get_tasks_by_name(task_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, task, completed
    FROM tasks
    WHERE LOWER(task) = LOWER(?)
    """, (task_name,))
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def get_project_tasks_by_name(task_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, task, project_name, completed
    FROM project_tasks
    WHERE LOWER(task) = LOWER(?)
    """, (task_name,))
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def search_memories_db(keyword):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT key, value
    FROM memories
    WHERE LOWER(key) LIKE LOWER(?) OR LOWER(value) LIKE LOWER(?)
    """, (f"%{keyword}%", f"%{keyword}%"))
    results = cursor.fetchall()
    conn.close()
    return results

def search_notes_db(keyword):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, content
    FROM notes
    WHERE LOWER(content) LIKE LOWER(?)
    """, (f"%{keyword}%",))
    results = cursor.fetchall()
    conn.close()
    return results

def search_tasks_db(keyword):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, task, completed
    FROM tasks
    WHERE LOWER(task) LIKE LOWER(?)
    """, (f"%{keyword}%",))
    results = cursor.fetchall()
    conn.close()
    return results

def search_projects_db(keyword):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, name, description
    FROM projects
    WHERE LOWER(name) LIKE LOWER(?) OR LOWER(description) LIKE LOWER(?)
    """, (f"%{keyword}%", f"%{keyword}%"))
    results = cursor.fetchall()
    conn.close()
    return results

def search_project_tasks_db(keyword):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, task, project_name, completed
    FROM project_tasks
    WHERE LOWER(task) LIKE LOWER(?)
    """, (f"%{keyword}%",))
    results = cursor.fetchall()
    conn.close()
    return results
