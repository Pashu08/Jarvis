from database.connection import get_connection

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

