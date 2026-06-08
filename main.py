import re
import os
import time
from datetime import datetime

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
from core.router import route_request, parse_multi_action_command
from tools.os_tools import execute_tool, tool_health_check, PackageDiscovery, ActivityResolver
from tools.voice_tools import listen, speak, start_whisper_server

from handlers.task_handlers import handle_task_commands
from handlers.note_handlers import handle_note_commands
from handlers.memory_handlers import handle_memory_commands
from handlers.project_handlers import handle_project_commands
from handlers.system_handlers import handle_system_commands

# --- INITIALIZATION ---
initialize_database()

notes = get_notes()
tasks = get_tasks()
projects = get_projects()

completed_tasks = sum(1 for _, _, completed in tasks if completed)
pending_tasks = [(task_id, task) for task_id, task, completed in tasks if not completed]

# --- COMMAND HISTORY LOGGING & MEMORY STRUCTURES ---
command_history = []  

def append_to_command_history(command_str):
    """Tracks running user context commands in a rolling 100-count memory cache."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    command_history.append((timestamp, command_str))
    if len(command_history) > 100:
        command_history.pop(0)

def log_action(command_label, outcome_msg):
    """Appends atomic execution metrics to a rolling logging path securely."""
    try:
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            
        log_path = os.path.join(log_dir, "jarvis_actions.log")
        
        # --- SAFE LOG ROTATION ---
        try:
            if os.path.exists(log_path) and os.path.getsize(log_path) > 5 * 1024 * 1024:
                old_log_path = os.path.join(log_dir, "jarvis_actions_old.log")
                if os.path.exists(old_log_path):
                    os.remove(old_log_path)
                os.rename(log_path, old_log_path)
        except Exception as e:
            print(f"[DEBUG] Log rotation skipped due to file lock/error: {e}")
            
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {command_label} {outcome_msg}\n")
    except Exception as e:
        print(f"[DEBUG] Error running write sequence to diagnostic logfile: {str(e)}")

# --- MULTI-ACTION PIPELINE HELPERS ---
def execute_action_sequence(actions):
    """Executes actions sequentially with STOP_ON_FAILURE implementation."""
    results = []
    success_count = 0
    failure_count = 0
    
    for i, (intent, payload) in enumerate(actions):
        command_repr = f"{intent} {payload}" if payload else intent
        
        if intent == "raw_intent":
            command_repr = payload
            routing_data = route_request(payload)
            if routing_data and routing_data.get("route") == "tool":
                res = execute_tool(routing_data.get("intent"), routing_data.get("payload"))
            else:
                res = f"Error: Could not resolve command: '{payload}'."
        else:
            res = execute_tool(intent, payload)
            
        results.append(res)
        log_action(command_repr, res)
        
        # STOP_ON_FAILURE Check
        is_failure = res and ("Error" in res or "Failed" in res or "Could not resolve" in res)
        if is_failure:
            failure_count += 1
            break
        else:
            success_count += 1

        if i < len(actions) - 1:
            time.sleep(0.8)
            
    # Clean execution summary
    if len(actions) > 1 or failure_count > 0:
        if failure_count == 0:
            summary_msg = f"Executed {success_count} actions successfully."
        else:
            summary_msg = f"Sequence stopped. Executed {success_count} actions. 1 action failed."
        results.append(summary_msg)
        
    return "\n".join(results)

# --- UNIFIED COMMAND PROCESSOR ---
def process_command(user_input, is_voice=False):
    """Central processing block to eliminate text/voice logic duplication."""
    user_lower = user_input.lower()
    append_to_command_history(user_input)

    # 1. Multi-Action & Core OS Commands Intercept
    actions = parse_multi_action_command(user_input)
    if len(actions) > 1 or (len(actions) == 1 and actions[0][0] != "raw_intent"):
        summary = execute_action_sequence(actions)
        print(f"JARVIS >\n{summary}" if "\n" in summary else f"JARVIS > {summary}")
        if is_voice: speak(summary)
        return

    # 2. Advanced AI Routing Layer Fallback
    routing_data = route_request(user_input)
    if routing_data and routing_data.get("route") == "tool":
        tool_response = execute_tool(routing_data.get("intent"), routing_data.get("payload"))
        log_action(user_input, tool_response)
        print(f"JARVIS > {tool_response}")
        if is_voice: speak(tool_response)
        return

    # 3. Action Database Handlers
    if handle_task_commands(user_input): return
    if handle_note_commands(user_input): return
    if handle_memory_commands(user_input): return
    if handle_project_commands(user_input): return
    if handle_system_commands(user_input): return

    # 4. System & AI Modules
    if user_lower == "help":
        print("\n===== JARVIS COMMANDS =====")
        print("Categories: Tasks, Notes, Memory, Projects, AI (ask <question>), Tools")
        print("System: 'voice', 'exit'")
        print("OS Controls: 'home', 'back', 'recent apps', 'open <app>', 'close <app>', 'current app'")
        print("Interactions: 'type <text>', 'tap <x y>', 'swipe <up/down/left/right>'")
        print("Combo Examples: 'open snapchat then tap 500 1000 then type hello'")
        print("===========================\n")
        if is_voice: speak("Displaying command help menu.")
        return
        
    elif user_lower in ["today", "help me plan my day"]:
        res = generate_daily_plan()
        print(f"JARVIS > {res}")
        if is_voice: speak(res)
        return
        
    elif user_lower in ["focus", "what should i work on", "what are my priorities"]:
        res = analyze_priorities()
        print(f"JARVIS > {res}")
        if is_voice: speak(res)
        return
        
    elif user_lower == "what have i been working on":
        res = summarize_recent_activity()
        print(f"JARVIS > {res}")
        if is_voice: speak(res)
        return
        
    elif user_lower.startswith("ask "):
        question = user_input[4:].strip()
        res = ask_with_context(question)
        print(f"JARVIS > {res}")
        if is_voice: speak(res)
        return
        
    else:
        # NLP PARSER ULTIMATE FALLBACK
        parsed_data = parse_natural_language(user_input)
        if parsed_data:
            print(f"JARVIS > [NLP Parsed Action]: {parsed_data.get('action')}")
            print("JARVIS > Route requires manual connection to handlers.")
            if is_voice: speak("Route requires manual connection.")
        else:
            msg = "Unrecognized command. Type 'help' or use 'ask <question>'"
            print(f"JARVIS > {msg}")
            if is_voice: speak("I did not recognize that command.")
        return

# --- STARTUP DIAGNOSTICS & TELEMETRY ---
print("\n=================================")
print("          JARVIS ONLINE          ")
print("=================================\n")

# Boot Local Server Pipeline
start_whisper_server()

health_status = tool_health_check()
discovered_pkg_count = len(PackageDiscovery._cached_packages)
activity_cache_count = len(ActivityResolver._cached_activities)
log_file_status = "Available" if os.path.exists(os.path.join("logs", "jarvis_actions.log")) else "Not Created Yet"

print("---------------------------------")
print(f"Tool Layer Status: {health_status}")
print(f"Packages Cached: {discovered_pkg_count}")
print(f"Activity Cache Count: {activity_cache_count}")
print(f"Log Status: {log_file_status}")
print("---------------------------------")
print(f"Projects: {len(projects)} | Notes: {len(notes)} | Tasks: {len(tasks)}")
print(f"Completed Tasks: {completed_tasks}")

print("\nPending Tasks:")
if pending_tasks:
    for _, task in pending_tasks[:5]:
        print(f"[ ] {task}")
else:
    print("None")

print("\nType 'help' for commands. Type 'voice' to initiate Voice V2.")
print("=================================\n")

# --- MAIN LOOP ROUTER ---
while True:
    user_input = input("You > ").strip()
    
    if not user_input:
        continue

    if user_input.lower() == "exit":
        print("JARVIS > Goodbye.")
        break
        
    if user_input.lower() == "voice":
        speak("Preparing microphone")
        time.sleep(1.5)
        speak("Speak now")
        print("JARVIS > [Listening via Termux...]")
        recognized_text = listen()
        
        if recognized_text:
            print(f"You (Voice) > {recognized_text}")
            if recognized_text.lower() in ["exit", "exit voice", "stop voice"]:
                print("JARVIS > Voice mode deactivated.")
                speak("Voice mode deactivated.")
                continue
            
            process_command(recognized_text, is_voice=True)
        else:
            print("JARVIS > No speech detected.")
        continue
        
    process_command(user_input, is_voice=False)
