# core/assistant.py
from ai.gemini_client import ask_gemini
from database.task_repo import get_tasks, search_tasks_db
from database.project_repo import get_projects, get_project_tasks, search_projects_db, search_project_tasks_db
from database.note_repo import get_recent_notes, search_notes_db
from database.memory_repo import search_memories_db

def extract_keywords(question):
    """
    Strips out common conversational stop words to isolate 
    searchable keywords for the database lookup.
    """
    stop_words = {
        "what", "who", "is", "a", "at", "he", "help", "me", 
        "with", "my", "how", "do", "i", "can", "you", "tell", 
        "about", "the", "for", "in", "of", "and", "to", "on"
    }
    words = question.lower().replace("?", "").replace(".", "").split()
    return [w for w in words if w not in stop_words and len(w) > 2]

def ask_with_context(question):
    """
    PHASE 1: Context Engine (RAG)
    Extracts keywords from the user's question, searches all 5 database 
    tables, and builds a targeted context block before calling Gemini.
    """
    keywords = extract_keywords(question)
    context_set = set()
    
    for kw in keywords:
        # Search Memories
        for key, value in search_memories_db(kw):
            context_set.add(f"[Memory] {key}: {value}")
            
        # Search Notes
        for _, content in search_notes_db(kw):
            context_set.add(f"[Note] {content}")
            
        # Search Tasks
        for _, task, completed in search_tasks_db(kw):
            status = "Completed" if completed else "Pending"
            context_set.add(f"[Task] {task} (Status: {status})")
            
        # Search Projects
        for _, name, desc in search_projects_db(kw):
            description = desc if desc else "No description"
            context_set.add(f"[Project] {name}: {description}")
            
        # Search Project Tasks
        for _, task, pname, completed in search_project_tasks_db(kw):
            status = "Completed" if completed else "Pending"
            context_set.add(f"[Project Task for '{pname}'] {task} (Status: {status})")

    system_context = ""
    if context_set:
        system_context = "JARVIS INTERNAL DATABASE CONTEXT:\n" + "\n".join(list(context_set))
    else:
        system_context = "No specific database records found for this query."
        
    return ask_gemini(question, system_context)

def generate_daily_plan():
    """
    PHASE 3: Personal Assistant Engine
    Analyzes pending tasks and recent notes to draft a cohesive daily plan.
    """
    tasks = get_tasks()
    pending_tasks = [t[1] for t in tasks if not t[2]]
    recent_notes = [n[1] for n in get_recent_notes(3)]
    
    system_context = (
        "You are an executive assistant helping the user plan their day. "
        "Review their pending tasks and recent notes. Build a logical, motivating, "
        "and structured daily plan. Suggest what they should tackle first and why."
    )
    
    system_context += f"\nPENDING TASKS: {pending_tasks}\n"
    system_context += f"RECENT NOTES: {recent_notes}\n"
    
    question = "Based on my pending tasks and recent notes, draft a logical daily plan for me."
    
    return ask_gemini(question, system_context)

def analyze_priorities():
    """
    PHASE 3: Personal Assistant Engine
    Reviews the entire workload and determines the highest impact priorities.
    """
    tasks = get_tasks()
    pending_tasks = [t[1] for t in tasks if not t[2]]
    
    projects = get_projects()
    project_status = []
    
    for p in projects:
        p_name = p[1]
        p_tasks = get_project_tasks(p_name)
        pending_p = [pt[1] for pt in p_tasks if not pt[2]]
        if pending_p:
            project_status.append(f"Project '{p_name}' has {len(pending_p)} pending tasks: {pending_p[:3]}")
            
    system_context = (
        "You are an analytical assistant. Review the user's workload, identify bottlenecks, "
        "and determine the top 3 highest impact priorities. Explain your reasoning briefly."
    )
    
    system_context += f"\nGENERAL PENDING TASKS: {pending_tasks}\n"
    system_context += f"PROJECT STATUS: {project_status}\n"
    
    question = "Analyze my current workload and tell me my top 3 priorities right now."
    
    return ask_gemini(question, system_context)

def summarize_recent_activity():
    """
    PHASE 3: Personal Assistant Engine
    Summarizes recent achievements and completed work.
    """
    tasks = get_tasks()
    completed_tasks = [t[1] for t in tasks if t[2]]
    recent_notes = [n[1] for n in get_recent_notes(5)]
    
    system_context = (
        "You are an encouraging assistant summarizing the user's recent achievements. "
        "Keep the summary brief, professional, and motivating."
    )
    
    # Grab the last 5 completed tasks to represent recent work
    system_context += f"\nRECENTLY COMPLETED TASKS: {completed_tasks[-5:]}\n"
    system_context += f"RECENT NOTES: {recent_notes}\n"
    
    question = "Summarize what I have been working on recently based on my completed tasks and notes."
    
    return ask_gemini(question, system_context)
