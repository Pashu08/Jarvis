from database.task_repo import (add_task, get_tasks, get_task_by_id, 
                                complete_task, update_task, delete_task, search_tasks_db)

def handle_task_commands(user_input):
    if user_input.startswith("add task "):
        task = user_input[len("add task "):].strip()
        if task:
            add_task(task)
            print("JARVIS > Task added.")
        else:
            print("JARVIS > Task description cannot be empty.")
        return True

    elif user_input == "list tasks":
        tasks = get_tasks()
        if not tasks:
            print("JARVIS > No tasks found.")
        else:
            print("JARVIS > Tasks:")
            for task_id, task, completed in tasks:
                status = "✓" if completed else " "
                print(f"[{status}] {task_id}. {task}")
        return True

    elif user_input.startswith("edit task "):
        parts = user_input[len("edit task "):].strip().split(" ", 1)
        if len(parts) < 2:
            print("JARVIS > Usage: edit task <id> <new text>")
        else:
            try:
                task_id = int(parts[0])
                new_text = parts[1].strip()
                if not new_text:
                    print("JARVIS > Task description cannot be empty.")
                elif get_task_by_id(task_id) is not None:
                    update_task(task_id, new_text)
                    print("JARVIS > Task updated.")
                else:
                    print("JARVIS > Task not found.")
            except ValueError:
                print("JARVIS > Invalid task ID.")
        return True

    elif user_input.startswith("find task "):
        keyword = user_input[len("find task "):].strip()
        matched_tasks = search_tasks_db(keyword)
        print("\n===== TASK SEARCH RESULTS =====\n")
        if matched_tasks:
            for task_id, task, completed in matched_tasks:
                status = "✓" if completed else " "
                print(f"[{status}] {task_id}. {task}")
        else:
            print("No matching tasks found.")
        print("\n==============================\n")
        return True
    
    elif user_input.startswith("complete task "):
        try:
            task_id = int(user_input.split()[-1])
            complete_task(task_id)
            print("JARVIS > Task completed.")
        except ValueError:
            print("JARVIS > Invalid task ID.")
        return True

    elif user_input.startswith("delete task "):
        target = user_input[len("delete task "):].strip()
        try:
            task_id = int(target)
            if delete_task(task_id):
                print("JARVIS > Task deleted.")
            else:
                print("JARVIS > Task not found.")
        except ValueError:
            print("JARVIS > Invalid task ID.")
        return True

    return False
