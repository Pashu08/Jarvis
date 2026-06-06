from database.memory_repo import search_memories_db
from database.project_repo import search_projects_db, search_project_tasks_db
from database.note_repo import search_notes_db
from database.task_repo import search_tasks_db

def handle_system_commands(user_input):
    if user_input.startswith("search memory "):
        keyword = user_input[len("search memory "):].strip()

        m_res = search_memories_db(keyword)
        p_res = search_projects_db(keyword)
        pt_res = search_project_tasks_db(keyword)
        n_res = search_notes_db(keyword)
        t_res = search_tasks_db(keyword)

        print("\n===== GLOBAL MEMORY SEARCH =====\n")
        has_results = False

        if m_res:
            has_results = True
            print("MEMORIES")
            for k, v in m_res:
                print(f"- {k}: {v}")
            print()

        if p_res:
            has_results = True
            print("PROJECTS")
            for _, name, _ in p_res:
                print(f"- {name}")
            print()

        if pt_res:
            has_results = True
            print("PROJECT TASKS")
            for _, task, pname, completed in pt_res:
                status = "✓" if completed else " "
                print(f"[{status}] {task} (Project: {pname})")
            print()

        if t_res:
            has_results = True
            print("TASKS")
            for _, task, completed in t_res:
                status = "✓" if completed else " "
                print(f"[{status}] {task}")
            print()

        if n_res:
            has_results = True
            print("NOTES")
            for _, content in n_res:
                print(f"- {content}")
            print()

        if not has_results:
            print("No matching records found.")
            
        print("\n================================\n")
        return True
        
    return False
