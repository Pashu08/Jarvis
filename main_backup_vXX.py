from core.database import initialize_database

from core.memory import (
    save_memory,
    get_memory,
    add_note,
    get_notes,
    add_task,
    get_tasks,
    complete_task,
    add_project,
    get_projects
)

from core.ai import ask_gemini
from core.parser import detect_intent

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

    if user_input.lower() == "exit":
        print("JARVIS > Goodbye.")
        break

    elif user_input.lower() == "help":

        print("""
===== JARVIS COMMANDS =====

MEMORY
  remember <key> <value>
  recall <key>

NOTES
  add note <text>
  list notes

TASKS
  add task <text>
  list tasks
  complete task <id>

PROJECTS
  add project <name>
  list projects

NATURAL LANGUAGE
  Remember that ...
  I need to ...
  Create a project called ...

AI
  ask <question>

SYSTEM
  status
  help
  exit

==========================
""")

    elif user_input.startswith("ask "):

        question = user_input[4:]

        print("JARVIS > Thinking...\n")

        answer = ask_gemini(question)

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

    elif user_input.startswith("add note "):

        note = user_input[len("add note "):]

        add_note(note)

        print("JARVIS > Note saved.")

    elif user_input == "list notes":

        notes = get_notes()

        if not notes:
            print("JARVIS > No notes found.")
        else:
            print("JARVIS > Notes:")

            for note_id, content in notes:
                print(f"{note_id}. {content}")

    elif user_input.startswith("add task "):

        task = user_input[len("add task "):]

        add_task(task)

        print("JARVIS > Task added.")

    elif user_input == "list tasks":

        tasks = get_tasks()

        if not tasks:
            print("JARVIS > No tasks found.")
        else:
            print("JARVIS > Tasks:")

            for task_id, task, completed in tasks:

                status = "✓" if completed else " "

                print(f"[{status}] {task_id}. {task}")

    elif user_input.startswith("complete task "):

        try:

            task_id = int(user_input.split()[-1])

            complete_task(task_id)

            print("JARVIS > Task completed.")

        except ValueError:
            print("JARVIS > Invalid task ID.")

    elif user_input.startswith("add project "):

        project_name = user_input[len("add project "):]

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

    else:

        intent = detect_intent(user_input)

        if intent == "task":

            task = user_input[10:]

            add_task(task)

            print("JARVIS > Task added.")

        elif intent == "memory":

            memory_text = user_input[14:]

            add_note(memory_text)

            print("JARVIS > Memory stored as note.")

        elif intent == "project":

            project_name = user_input[24:]

            add_project(project_name)

            print("JARVIS > Project added.")

        else:

            print("JARVIS > Command not recognized.")
