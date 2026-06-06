from core.database import initialize_database

from core.memory import (
    save_memory,
    get_memory,
    get_all_memories,
    update_memory,
    add_note,
    get_notes,
    get_note_by_id,
    get_recent_notes,
    update_note,
    add_task,
    get_tasks,
    get_task_by_id,
    complete_task,
    update_task,
    delete_task,
    add_project,
    get_projects,
    get_project_by_name,
    update_project_description,
    update_project_name,
    add_project_task,
    get_project_tasks,
    get_project_task_by_id,
    complete_project_task,
    update_project_task,
    delete_project_task,
    delete_project,
    get_tasks_by_name,
    get_project_tasks_by_name,
    search_memories_db,
    search_notes_db,
    search_tasks_db,
    search_projects_db,
    search_project_tasks_db
)

# Phase 1 & 3: New Assistant Engine Imports
from core.assistant import (
    ask_with_context,
    generate_daily_plan,
    analyze_priorities,
    summarize_recent_activity
)

# Phase 2: Upgraded NLP Parser
from core.parser import parse_natural_language
from core.conversation import get_history

# Phase V4.1: Routing & Tool Execution Layer
from core.router import route_request
from core.tools import execute_tool

initialize_database()

notes = get_notes()
tasks = get_tasks()
projects = get_projects()

completed_tasks = sum(
    1 for _, _, completed in tasks if completed
)

pending_tasks = [
    (task_id, task)
    for task_id, task, completed in tasks
    if not completed
]

print("\n=================================")
print("JARVIS ONLINE")
print("=================================\n")

print(f"Projects: {len(projects)}")
print(f"Notes: {len(notes)}")
print(f"Tasks: {len(tasks)}")
print(f"Completed Tasks: {completed_tasks}")

print("\nPending Tasks:")

if pending_tasks:
    for _, task in pending_tasks[:5]:
        print(f"[ ] {task}")
else:
    print("None")

print("\nType 'help' for commands.")
print("=================================\n")

while True:

    user_input = input("You > ").strip()

    if not user_input:
        continue

    # --- PHASE V4.1 ROUTING LAYER INTERCEPT ---
    routing_data = route_request(user_input)
    
    if routing_data and routing_data.get("route") == "tool":
        tool_response = execute_tool(routing_data.get("intent"), routing_data.get("payload"))
        print(f"JARVIS > {tool_response}")
        continue
    # ------------------------------------------

    if user_input.lower() == "exit":
        print("JARVIS > Goodbye.")
        break

    elif user_input.lower() == "help":

        print("""
===== JARVIS COMMANDS =====

MEMORY & SEARCH
  remember <key> <value>
  recall <key>
  knowledge (or 'what do you know about me')
  search memory <keyword>
  update memory <key> <value>

NOTES
  add note <text>
  list notes
  find note <keyword>
  edit note <id> <new text>

TASKS
  add task <text>
  list tasks
  complete task <id>
  delete task <id> or <name>
  find task <keyword>
  edit task <id> <new text>

PROJECTS
  add project <name>
  list projects
  project <project_name>
  describe project <project_name>
  rename project <old_name> <new_name>
  add project task <project> <task>
  complete project task <id>
  delete project task <id> or <name>
  edit project task <id> <new text>
  delete project <name>
  find project <keyword>

DASHBOARD & ASSISTANT
  today
  focus
  projects dashboard
  what should i work on
  help me plan my day
  what are my priorities
  what have i been working on

AI
  ask <question>

TOOLS & AUTOMATION
  open <app_name> (e.g., open whatsapp, open chrome)

SYSTEM
  status
  help
  exit

==========================
""")

    # --- PHASE 3: PERSONAL ASSISTANT ENGINE COMMANDS ---
    elif user_input.lower() == "help me plan my day":
        print("JARVIS > Analyzing your database to build a plan...\n")
        print(generate_daily_plan())

    elif user_input.lower() == "what are my priorities":
        print("JARVIS > Evaluating incomplete tasks and project progress...\n")
        print(analyze_priorities())

    elif user_input.lower() == "what have i been working on":
        print("JARVIS > Fetching recent activity...\n")
        print(summarize_recent_activity())

    elif user_input.lower() in ["knowledge", "what do you know about me"]:
        
        print("\n===== KNOWLEDGE BASE =====\n")
        
        all_memories = get_all_memories()
        print("MEMORIES:")
        if all_memories:
            for key, value in all_memories:
                print(f"- {key}: {value}")
        else:
            print("None")
            
        all_notes = get_notes()
        print("\nNOTES:")
        if all_notes:
            for note_id, content in all_notes:
                print(f"- {content}")
        else:
            print("None")
            
        print("\n==========================\n")

    elif user_input.lower() == "what should i work on":
        
        projects_data = get_projects()
        candidates = []
        
        for proj in projects_data:
            p_id, p_name, p_desc = proj
            p_tasks = get_project_tasks(p_name)
            total = len(p_tasks)
            completed = sum(1 for _, _, c in p_tasks if c)
            pending = [t for t in p_tasks if not t[2]]
            
            if total > 0 and len(pending) > 0:
                pct = (completed / total) * 100
                candidates.append({
                    "name": p_name,
                    "pending_tasks": pending,
                    "percentage": pct
                })
        
        print("\n===== JARVIS RECOMMENDATION =====\n")
        if not candidates:
            print("You have no pending project tasks! Take a well-deserved break.")
        else:
            candidates.sort(key=lambda x: x["percentage"], reverse=True)
            top_candidate = candidates[0]
            rec_task = top_candidate["pending_tasks"][0]
            
            print(f"RECOMMENDED TASK: [{rec_task[0]}] {rec_task[1]}")
            print(f"FROM PROJECT: {top_candidate['name']}")
            print(f"REASONING: This project is {int(top_candidate['percentage'])}% complete. Let's push it closer to the finish line!")
        print("\n=================================\n")

    elif user_input.lower() == "projects dashboard":
        
        print("\n===== PROJECT DASHBOARD =====\n")
        
        dashboard_projects = get_projects()
        
        if dashboard_projects:
            for _, name, _ in dashboard_projects:
                print(name)
                
                proj_tasks = get_project_tasks(name)
                total_t = len(proj_tasks)
                comp_t = sum(1 for _, _, completed in proj_tasks if completed)
                
                if total_t > 0:
                    pct = int((comp_t / total_t) * 100)
                else:
                    pct = 0
                    
                print(f"Progress: {comp_t}/{total_t} ({pct}%)\n")
        else:
            print("No projects found.\n")
            
        print("=============================\n")

    elif user_input.lower() == "today":

        print("\n===== TODAY =====\n")

        projects = get_projects()

        print("PROJECTS:")

        if projects:
            for _, name, _ in projects:
                print(f"- {name}")
        else:
            print("None")

        print("\nPENDING TASKS:")

        tasks = get_tasks()

        pending_found = False

        for _, task, completed in tasks:
            if not completed:
                pending_found = True
                print(f"- {task}")

        if not pending_found:
            print("None")

        print("\nRECENT NOTES:")

        recent_notes = get_recent_notes()

        if recent_notes:
            for _, content in recent_notes:
                print(f"- {content}")
        else:
            print("None")

        print("\nRECENT CONVERSATION:")

        history = get_history(6)

        if history.strip():
            print(history)
        else:
            print("None")

        print("=================\n")

    elif user_input.lower() == "focus":

        print("\n===== FOCUS MODE =====\n")

        tasks = get_tasks()

        pending_tasks = [
            task
            for _, task, completed in tasks
            if not completed
        ]

        if pending_tasks:

            print("TOP PRIORITIES:\n")

            for task in pending_tasks[:3]:
                print(f"- {task}")

        else:
            print("No pending tasks.")

        print("\nPROJECTS:\n")

        projects = get_projects()

        if projects:
            for _, name, _ in projects:
                print(f"- {name}")
        else:
            print("None")

        print("\nREMEMBER:\n")

        recent_notes = get_recent_notes()

        if recent_notes:
            for _, content in recent_notes:
                print(f"- {content}")
        else:
            print("None")

        print("\n======================\n")

    # --- PHASE 1: CONTEXT ENGINE ---
    elif user_input.startswith("ask "):

        question = user_input[4:]

        print("JARVIS > Searching memory and consulting Gemini...\n")

        answer = ask_with_context(question)

        print(answer)

    elif user_input.lower() == "status":

        notes = get_notes()
        tasks = get_tasks()
        projects = get_projects()

        completed_tasks = sum(
            1 for _, _, completed in tasks
            if completed
        )

        print("\n===== JARVIS STATUS =====\n")

        print(f"Projects: {len(projects)}")
        print(f"Notes: {len(notes)}")
        print(f"Tasks: {len(tasks)}")
        print(f"Completed Tasks: {completed_tasks}")

        print("\nCurrent Projects:")

        if projects:
            for _, name, _ in projects:
                print(f"- {name}")
        else:
            print("None")

        print("\n=========================\n")

    elif user_input.startswith("update memory "):
        parts = user_input[len("update memory "):].strip().split(" ", 1)
        if len(parts) < 2:
            print("JARVIS > Usage: update memory <key> <value>")
        else:
            key = parts[0].strip()
            val = parts[1].strip()
            if not val:
                print("JARVIS > Memory value cannot be empty.")
            elif get_memory(key) is not None:
                update_memory(key, val)
                print(f"JARVIS > Memory '{key}' updated.")
            else:
                print(f"JARVIS > Memory '{key}' not found. Use 'remember' to create it.")

    elif user_input.startswith("remember "):

        parts = user_input.split(" ", 2)

        if len(parts) < 3:
            print("JARVIS > Usage: remember <key> <value>")
            continue

        key = parts[1]
        value = parts[2]

        save_memory(key, value)

        print(f"JARVIS > Saved '{key}'")

    elif user_input.startswith("recall "):

        key = user_input.split(" ", 1)[1]

        value = get_memory(key)

        if value:
            print(f"JARVIS > {value}")
        else:
            print("JARVIS > I don't know that yet.")

    elif user_input.startswith("edit note "):
        parts = user_input[len("edit note "):].strip().split(" ", 1)
        if len(parts) < 2:
            print("JARVIS > Usage: edit note <id> <new text>")
        else:
            try:
                note_id = int(parts[0])
                new_text = parts[1].strip()
                if not new_text:
                    print("JARVIS > Note content cannot be empty.")
                elif get_note_by_id(note_id) is not None:
                    update_note(note_id, new_text)
                    print("JARVIS > Note updated.")
                else:
                    print("JARVIS > Note not found.")
            except ValueError:
                print("JARVIS > Invalid note ID.")

    elif user_input.startswith("add note "):

        note = user_input[len("add note "):].strip()

        if note:
            add_note(note)
            print("JARVIS > Note saved.")
        else:
            print("JARVIS > Note cannot be empty.")

    elif user_input == "list notes":

        notes = get_notes()

        if not notes:
            print("JARVIS > No notes found.")
        else:
            print("JARVIS > Notes:")

            for note_id, content in notes:
                print(f"{note_id}. {content}")

    elif user_input.startswith("find note "):
        keyword = user_input[len("find note "):].strip()
        matched_notes = search_notes_db(keyword)
        print("\n===== NOTE SEARCH RESULTS =====\n")
        if matched_notes:
            for note_id, content in matched_notes:
                print(f"{note_id}. {content}")
        else:
            print("No matching notes found.")
        print("\n===============================\n")

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

    elif user_input.startswith("add task "):

        task = user_input[len("add task "):].strip()

        if task:
            add_task(task)
            print("JARVIS > Task added.")
        else:
            print("JARVIS > Task description cannot be empty.")

    elif user_input == "list tasks":

        tasks = get_tasks()

        if not tasks:
            print("JARVIS > No tasks found.")
        else:
            print("JARVIS > Tasks:")

            for task_id, task, completed in tasks:

                status = "✓" if completed else " "

                print(f"[{status}] {task_id}. {task}")

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

    elif user_input.startswith("edit project task "):
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
                print(f"JARVIS > Project task '{matched_ptasks[0][1]}' from project '{matched_ptasks[0][2]}' deleted.")
            else:
                print("JARVIS > Multiple matches found. Protection triggered. Please specify by unique ID:")
                for tid, tdesc, pname, _ in matched_ptasks:
                    print(f"  ID {tid}: '{tdesc}' in Project '{pname}'")

    elif user_input.startswith("complete task "):

        try:
            task_id = int(user_input.split()[-1])
            if get_task_by_id(task_id) is not None:
                complete_task(task_id)
                print("JARVIS > Task completed.")
            else:
                print("JARVIS > Task not found.")
        except ValueError:
            print("JARVIS > Invalid task ID.")

    elif user_input.startswith("delete task "):
        target = user_input[len("delete task "):].strip()
        
        is_id = False
        try:
            task_id = int(target)
            is_id = True
        except ValueError:
            pass

        if is_id and get_task_by_id(task_id) is not None:
            success = delete_task(task_id)
            if success:
                print("JARVIS > Task deleted.")
            else:
                print("JARVIS > Task not found.")
        else:
            matched_tasks = get_tasks_by_name(target)
            if not matched_tasks:
                print("JARVIS > Task not found.")
            elif len(matched_tasks) == 1:
                delete_task(matched_tasks[0][0])
                print(f"JARVIS > Task '{matched_tasks[0][1]}' deleted.")
            else:
                print("JARVIS > Multiple matches found. Protection triggered. Please specify by unique ID:")
                for tid, tdesc, _ in matched_tasks:
                    print(f"  ID {tid}: '{tdesc}'")

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
            print("JARVIS > Project not found or task description missing. Usage: add project task <project_name> <task>")

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

    elif user_input.startswith("add project "):
        project_name = user_input[len("add project "):].strip()
        
        if not project_name:
            print("JARVIS > Project name cannot be empty.")
        elif get_project_by_name(project_name):
            print(f"JARVIS > Project '{project_name}' already exists.")
        else:
            add_project(project_name)
            print("JARVIS > Project added.")

    elif user_input == "list projects":

        projects = get_projects()

        if not projects:
            print("JARVIS > No projects found.")
        else:
            print("JARVIS > Projects:")

            for project_id, name, description in projects:
                print(f"{project_id}. {name}")

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

    elif user_input.startswith("search memory "):
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
            print(f"No records found matching '{keyword}' across the entire matrix.")
            
        print("================================\n")

    elif user_input.startswith("project "):

        project_name = user_input[8:]

        project = get_project_by_name(project_name)

        if project:

            _, name, description = project

            print(f"\n===== {name.upper()} =====\n")

            print("DESCRIPTION:")
            if description:
                print(description)
            else:
                print("No description available.")

            project_tasks_list = get_project_tasks(project_name)
            
            total_tasks = len(project_tasks_list)
            completed_tasks = sum(1 for _, _, completed in project_tasks_list if completed)
            
            print("\nPROGRESS:")
            if total_tasks > 0:
                percentage = int((completed_tasks / total_tasks) * 100)
            else:
                percentage = 0
            print(f"{completed_tasks} / {total_tasks} completed ({percentage}%)")

            print("\nPROJECT TASKS:")
            if project_tasks_list:
                for task_id, task_desc, completed in project_tasks_list:
                    status = "✓" if completed else " "
                    print(f"[{status}] {task_id}. {task_desc}")
            else:
                print("No project tasks.")

            print("\n====================\n")

        else:
            print("JARVIS > Project not found.")

    elif user_input.startswith("describe project "):

        project_name = user_input[len("describe project "):]

        project = get_project_by_name(project_name)

        if not project:
            print("JARVIS > Project not found.")
            continue

        print("\nEnter project description:")
        description = input("> ").strip()

        update_project_description(
            project_name,
            description
        )

        print("JARVIS > Project description updated.")

    # --- PHASE 2: NATURAL LANGUAGE ENGINE ---
    else:
        intent_data = parse_natural_language(user_input)
        
        if intent_data and intent_data.get("action"):
            action = intent_data["action"]
            payload = intent_data.get("payload")
            
            if action == "add_task" and payload:
                add_task(payload)
                print(f"JARVIS > Natural language detected. Task added: '{payload}'")
                
            elif action == "add_note" and payload:
                add_note(payload)
                print(f"JARVIS > Natural language detected. Memory stored as note: '{payload}'")
                
            elif action == "add_project" and payload:
                if get_project_by_name(payload):
                    print(f"JARVIS > Project '{payload}' already exists.")
                else:
                    add_project(payload)
                    print(f"JARVIS > Natural language detected. Project added: '{payload}'")
                    
            elif action == "rename_project":
                old_name = intent_data.get("old_name")
                new_name = intent_data.get("new_name")
                if old_name and new_name:
                    if get_project_by_name(new_name):
                        print(f"JARVIS > Cannot rename. Project '{new_name}' already exists.")
                    else:
                        success = update_project_name(old_name, new_name)
                        if success:
                            print(f"JARVIS > Natural language detected. Project '{old_name}' renamed to '{new_name}'.")
                        else:
                            print("JARVIS > Error renaming project or project not found.")
                else:
                    print("JARVIS > Command not recognized.")
            else:
                print("JARVIS > Command not recognized.")
        else:
            print("JARVIS > Command not recognized.")
