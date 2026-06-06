import re

def detect_intent(user_input):
    """
    Legacy intent detection. Kept for backwards compatibility 
    in case other modules rely on strict string returning.
    """
    text = user_input.lower()

    if text.startswith("remember that "):
        return "memory"

    if text.startswith("i need to "):
        return "task"

    if text.startswith("create a project called "):
        return "project"

    return "ask"


def parse_natural_language(user_input):
    """
    Phase 2: Natural Language Engine.
    Parses conversational input and returns a dictionary with the targeted 
    action and the exact payload extracted from the sentence.
    """
    lower_input = user_input.lower()

    # 1. Conversational Project Renaming
    # Matches formats like: "rename project X to Y", "change the project X to Y"
    rename_match = re.search(r"(?:rename|change)\s+(?:the\s+)?project\s+(.+?)\s+to\s+(.+)", user_input, re.IGNORECASE)
    if rename_match:
        return {
            "action": "rename_project",
            "old_name": rename_match.group(1).strip(),
            "new_name": rename_match.group(2).strip()
        }

    # 2. Project Creation Detection
    project_indicators = [
        "create a project called ",
        "create a new project called ",
        "start a project named ",
        "make a project for ",
        "new project called "
    ]
    for ind in project_indicators:
        if ind in lower_input:
            idx = lower_input.find(ind) + len(ind)
            payload = user_input[idx:].strip()
            # Clean up trailing punctuation if they spoke naturally
            payload = payload.rstrip(".!")
            return {"action": "add_project", "payload": payload}

    # 3. Memory / Note Detection
    note_indicators = [
        "remember that ",
        "keep in mind that ",
        "note that ",
        "don't forget that "
    ]
    for ind in note_indicators:
        if ind in lower_input:
            idx = lower_input.find(ind) + len(ind)
            payload = user_input[idx:].strip()
            return {"action": "add_note", "payload": payload}

    # 4. Task Detection (Scans anywhere in the string)
    task_indicators = [
        "need to ",
        "remember to ",
        "should probably ",
        "i should ",
        "tomorrow i will ",
        "tomorrow i should ",
        "have to ",
        "gotta ",
        "make sure to "
    ]
    for ind in task_indicators:
        if ind in lower_input:
            idx = lower_input.find(ind) + len(ind)
            payload = user_input[idx:].strip()
            return {"action": "add_task", "payload": payload}

    # If no natural language patterns match, return an empty dict
    return {}
