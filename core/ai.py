import os
import requests

from core.conversation import (
    add_message,
    get_history
)

API_KEY = os.getenv("GEMINI_API_KEY")

MODEL = "gemini-2.5-flash"


def ask_gemini(question, system_context=""):

    if not API_KEY:
        return "GEMINI_API_KEY not found."

    conversation_context = get_history()

    prompt = f"""
You are JARVIS, an advanced personal assistant.

Use the provided system context and recent conversation to assist the user.
If system context is provided, rely heavily on those facts.

{system_context}

RECENT CONVERSATION:
{conversation_context}

USER:
{question}
"""

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{MODEL}:generateContent?key={API_KEY}"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    try:

        response = requests.post(
            url,
            json=payload,
            timeout=60
        )

        data = response.json()
        
        answer = data["candidates"][0]["content"]["parts"][0]["text"]

        add_message("USER", question)
        add_message("JARVIS", answer)

        return answer

    except Exception as e:
        return f"Error: {e}"
