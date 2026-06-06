from database.connection import initialize_database
from database.note_repo import get_notes
from database.task_repo import get_tasks
from database.project_repo import get_projects

from ai.assistant import (
    ask_with_context,
    generate_daily_plan,
    analyze_priorities,
    summarize_recent_activity
)

from core.parser import parse_natural_language
from core.router import route_request
from tools.os_tools import execute_tool

from handlers.task_handlers import handle_task_commands
from handlers.note_handlers import handle_note_commands
from handlers.memory_handlers import handle_memory_commands
from handlers.project_handlers import handle_project_commands
from handlers.system_handlers import handle_system_commands

initialize_database()

notes = get_notes()
tasks = get_tasks()
projects = get_projects()

completed_tasks = sum(1 for _, _, completed in tasks if completed)
pending_tasks = [(task_id, task) for task_id, task, completed in tasks if not completed]

print("\n=================================")
print("          JARVIS ONLINE          ")
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

    # --- ACTION HANDLERS ---
    if handle_task_commands(user_input): continue
    if handle_note_commands(user_input): continue
    if handle_memory_commands(user_input): continue
    if handle_project_commands(user_input): continue
    if handle_system_commands(user_input): continue

    # --- SYSTEM & AI COMMANDS ---
    if user_input.lower() == "exit":
        print("JARVIS > Goodbye.")
        break
        
    elif user_input.lower() == "help":
        print("\n===== JARVIS COMMANDS =====")
        print("Refer to internal documentation for full command list.")
        print("Categories: Tasks, Notes, Memory, Projects, AI (ask <question>), Tools")
        print("===========================\n")
        
    elif user_input.lower() in ["today", "help me plan my day"]:
        print(f"JARVIS > {generate_daily_plan()}")
        
    elif user_input.lower() in ["focus", "what should i work on", "what are my priorities"]:
        print(f"JARVIS > {analyze_priorities()}")
        
    elif user_input.lower() == "what have i been working on":
        print(f"JARVIS > {summarize_recent_activity()}")
        
    elif user_input.startswith("ask "):
        question = user_input[4:].strip()
        print(f"JARVIS > {ask_with_context(question)}")
        
    else:
        # --- NLP PARSER FALLBACK ---
        parsed_data = parse_natural_language(user_input)
        if parsed_data:
            print(f"JARVIS > [NLP Parsed Action]: {parsed_data.get('action')}")
            print("JARVIS > Route requires manual connection to handlers.")
        else:
            print("JARVIS > Unrecognized command. Type 'help' or use 'ask <question>'")
