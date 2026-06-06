import re

def route_request(user_input):
    """
    Central routing engine for JARVIS. Inspects user intent, extracts payloads,
    and returns a structured dictionary matching the system routing matrix.
    
    Returns:
        dict: {
            "route": str (tool | assistant | memory | command | gemini),
            "intent": str (specific block sub-intent),
            "payload": str (extracted parameters or raw input)
        }
    """
    cleaned_input = user_input.strip()
    text = cleaned_input.lower()

    # 1. Check Tool Route (Infrastructure ready for OS & Android automation hooks)
    tool_res = _match_tool_route(text, cleaned_input)
    if tool_res:
        return tool_res

    # 2. Check Assistant Route (Executive summary & planning engine)
    assistant_res = _match_assistant_route(text, cleaned_input)
    if assistant_res:
        return assistant_res

    # 3. Check Memory Route (NLP-driven state management & memory storage)
    memory_res = _match_memory_route(text, cleaned_input)
    if memory_res:
        return memory_res

    # 4. Check Command Route (Rigid structural database CRUD operations)
    command_res = _match_command_route(text, cleaned_input)
    if command_res:
        return command_res

    # 5. Default Fallback Route (Pass through to LLM / Agent reasoning loops)
    # FUTURE EXPANSION: Insert a router hook here to classify intent via zero-shot LLM 
    # instead of string match if the confidence of regex/deterministic parsing is 0.
    return {
        "route": "gemini",
        "intent": "general_query",
        "payload": cleaned_input
    }


def _match_tool_route(text, raw_text):
    """Parses environment-level execution hooks, apps, and system actions."""
    if text.startswith("open "):
        app_target = raw_text[5:].strip()
        app_lower = app_target.lower()
        
        # FUTURE EXPANSION: Map these intents directly to Android Intent URIs 
        # (e.g., android.intent.action.VIEW) or deep-link packages for mobile automation.
        if "whatsapp" in app_lower:
            intent = "open_whatsapp"
        elif "discord" in app_lower:
            intent = "open_discord"
        elif "chrome" in app_lower:
            intent = "open_chrome"
        elif "browser" in app_lower:
            intent = "open_browser"
        else:
            # Catch-all app launch intent to maximize scalability for arbitrary voice commands
            intent = "open_app"
            
        return {
            "route": "tool",
            "intent": intent,
            "payload": app_target
        }
    return None


def _match_assistant_route(text, raw_text):
    """Parses structural analytical, reasoning, and context compilation triggers."""
    # FUTURE EXPANSION: Expand these targets to support semantic variations via 
    # audio transcription tokens or text embeddings to prevent rigid phrasing failures.
    assistant_map = {
        "help me plan my day": "daily_plan",
        "what are my priorities": "priorities",
        "what have i been working on": "recent_activity"
    }
    
    if text in assistant_map:
        return {
            "route": "assistant",
            "intent": assistant_map[text],
            "payload": raw_text
        }
    return None


def _match_memory_route(text, raw_text):
    """Parses unstructured declarative phrases meant for internal semantic memory tables."""
    if text.startswith("remember that "):
        return {
            "route": "memory",
            "intent": "remember_fact",
            "payload": raw_text[14:].strip()
        }
    elif text.startswith("remember "):
        return {
            "route": "memory",
            "intent": "remember",
            "payload": raw_text[9:].strip()
        }
    elif text.startswith("add note ") or text.startswith("note that "):
        payload_idx = 9 if text.startswith("add note ") else 10
        return {
            "route": "memory",
            "intent": "note",
            "payload": raw_text[payload_idx:].strip()
        }
    return None


def _match_command_route(text, raw_text):
    """Parses strict structural database system administration commands."""
    # Exact keyword triggers
    exact_commands = {
        "status": "status",
        "today": "today",
        "focus": "focus",
        "list tasks": "list_tasks",
        "list projects": "list_projects"
    }
    if text in exact_commands:
        return {
            "route": "command",
            "intent": exact_commands[text],
            "payload": ""
        }

    # Dynamic action prefix parsing (CRUD)
    # FUTURE EXPANSION: These prefixes can feed straight into deterministic 
    # execution nodes inside an autonomous Multi-Agent graph workflow.
    prefixes = [
        ("add task ", "add_task"),
        ("delete task ", "delete_task"),
        ("edit task ", "edit_task"),
        ("complete task ", "complete_task"),
        ("add project ", "add_project"),
        ("delete project ", "delete_project")
    ]
    
    for prefix, intent in prefixes:
        if text.startswith(prefix):
            return {
                "route": "command",
                "intent": intent,
                "payload": raw_text[len(prefix):].strip()
            }
            
    return None
