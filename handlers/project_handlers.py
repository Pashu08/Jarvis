from database.project_repo import (
    get_projects, get_project_by_name, update_project_name,
    add_project, delete_project, add_project_task, get_project_tasks_by_name,
    get_project_task_by_id, complete_project_task, update_project_task, delete_project_task,
    search_projects_db
)

def handle_project_commands(user_input):
    if user_input.startswith("edit project task "):
        parts = user_input[len("edit project task "):].strip().split(" ", 1)
        if len(parts) < 2:
            print("JARVIS > Usage: edit project task <id> <new text>")
        else:
            try:
                task_id = int(parts[0])
                new_text = parts[1].strip()
                if not new_text:
                    print("JARVIS > Project task description cannot be empty.")
                elif get_project_task_by_id(task_id) is not None:
                    update_project_task(task_id, new_text)
                    print("JARVIS > Project task updated.")
                else:
                    print("JARVIS > Project task not found.")
            except ValueError:
                print("JARVIS > Invalid task ID.")
        return True

    elif user_input.startswith("complete project task "):
        try:
            task_id = int(user_input.split()[-1])
            if get_project_task_by_id(task_id) is not None:
                complete_project_task(task_id)
                print("JARVIS > Project task completed.")
            else:
                print("JARVIS > Project task not found.")
        except ValueError:
            print("JARVIS > Invalid task ID.")
        return True

    elif user_input.startswith("delete project task "):
        target = user_input[len("delete project task "):].strip()
        is_id = False
        try:
            task_id = int(target)
            is_id = True
        except ValueError:
            pass

        if is_id and get_project_task_by_id(task_id) is not None:
            success = delete_project_task(task_id)
            if success:
                print("JARVIS > Project task deleted.")
            else:
                print("JARVIS > Project task not found.")
        else:
            matched_ptasks = get_project_tasks_by_name(target)
            if not matched_ptasks:
                print("JARVIS > Project task not found.")
            elif len(matched_ptasks) == 1:
                delete_project_task(matched_ptasks[0][0])
                print(f"JARVIS > Project task '{target}' deleted.")
            else:
                print("JARVIS > Multiple tasks match that name. Use ID.")
        return True

    elif user_input.startswith("add project task "):
        payload = user_input[len("add project task "):].strip()
        projects = get_projects()
        projects.sort(key=lambda x: len(x[1]), reverse=True)

        matched_project = None
        task_desc = None

        for _, p_name, _ in projects:
            if payload.lower().startswith(p_name.lower() + " "):
                matched_project = p_name
                task_desc = payload[len(p_name):].strip()
                break

        if matched_project and task_desc:
            add_project_task(matched_project, task_desc)
            print(f"JARVIS > Added task to '{matched_project}'")
        else:
            print("JARVIS > Project not found or task missing. Usage: add project task <project_name> <task>")
        return True

    elif user_input.startswith("rename project "):
        payload = user_input[len("rename project "):].strip()
        projects = get_projects()
        projects.sort(key=lambda x: len(x[1]), reverse=True)

        matched_project = None
        new_name = None

        for _, p_name, _ in projects:
            if payload.lower().startswith(p_name.lower() + " "):
                matched_project = p_name
                new_name = payload[len(p_name):].strip()
                break

        if matched_project and new_name:
            if get_project_by_name(new_name):
                print(f"JARVIS > Cannot rename. Project '{new_name}' already exists.")
            else:
                success = update_project_name(matched_project, new_name)
                if success:
                    print(f"JARVIS > Project '{matched_project}' renamed to '{new_name}'.")
                else:
                    print("JARVIS > Error renaming project.")
        else:
            print("JARVIS > Project not found or new name missing. Usage: rename project <old_name> <new_name>")
        return True

    elif user_input.startswith("delete project "):
        project_name = user_input[len("delete project "):].strip()
        project = get_project_by_name(project_name)

        if project:
            print(f"JARVIS > Are you sure you want to delete project '{project[1]}' and all its tasks? (y/n)")
            confirm = input("You > ").strip().lower()
            if confirm in ['y', 'yes']:
                success = delete_project(project[1])
                if success:
                    print(f"JARVIS > Project '{project[1]}' and associated tasks deleted.")
                else:
                    print("JARVIS > Error deleting project.")
            else:
                print("JARVIS > Project deletion cancelled.")
        else:
            print("JARVIS > Project not found.")
        return True

    elif user_input.startswith("add project "):
        project_name = user_input[len("add project "):].strip()
        if not project_name:
            print("JARVIS > Project name cannot be empty.")
        elif get_project_by_name(project_name):
            print(f"JARVIS > Project '{project_name}' already exists.")
        else:
            add_project(project_name)
            print("JARVIS > Project added.")
        return True

    elif user_input == "list projects":
        projects = get_projects()
        if not projects:
            print("JARVIS > No projects found.")
        else:
            print("JARVIS > Projects:")
            for project_id, name, description in projects:
                print(f"{project_id}. {name}")
        return True

    elif user_input.startswith("find project "):
        keyword = user_input[len("find project "):].strip()
        matched_projects = search_projects_db(keyword)
        print("\n===== PROJECT SEARCH RESULTS =====\n")
        if matched_projects:
            for _, name, description in matched_projects:
                desc = description if description else "No description available."
                print(f"- {name}: {desc}")
        else:
            print("No matching projects found.")
        print("\n==================================\n")
        return True
        
    return False
