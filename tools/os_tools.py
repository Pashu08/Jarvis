import subprocess

# Scalable mapping for Android app components
APP_COMPONENTS = {
    "whatsapp": "com.whatsapp/.Main",
    "discord": "com.discord/.main.MainActivity",
    "chrome": "com.android.chrome/com.google.android.apps.chrome.Main",
    "browser": "com.android.chrome/com.google.android.apps.chrome.Main"
}

def execute_tool(intent, payload=None):
    """
    Central execution engine for the Tool Subsystem. Receives routed intents 
    and handles system, OS, and application-level execution hooks.
    """
    try:
        # Route specific known app shortcuts
        if intent == "open_whatsapp":
            return _handle_app_launch("whatsapp")

        elif intent == "open_discord":
            return _handle_app_launch("discord")

        elif intent == "open_chrome":
            return _handle_app_launch("chrome")

        elif intent == "open_browser":
            return _handle_app_launch("browser")

        # Route arbitrary / dynamic application launches
        elif intent == "open_app":
            if not payload:
                return "Error: Cannot open application without a target application name specified in payload."
            return _handle_app_launch(payload)

        # Handle unrecognized tool intents gracefully
        else:
            return f"Error: Tool intent '{intent}' is currently unsupported by this execution layer."

    except Exception as e:
        # Prevent runtime crashes by capturing unexpected exceptions safely
        return f"Execution Error: Failed to process tool action due to: {str(e)}"


def _handle_app_launch(app_name):
    """
    Executes Android Activity Manager (am) commands to launch applications via Termux.
    """
    target_app = app_name.strip().lower()

    # Look up the strict Android component name
    component = APP_COMPONENTS.get(target_app)
    
    if not component:
        return f"Error: Do not know the Android component name for '{app_name}'. Please update APP_COMPONENTS mapping."

    try:
        # Execute the am start command
        result = subprocess.run(
            ["am", "start", "-n", component],
            capture_output=True,
            text=True,
            check=True
        )
        return f"Successfully opened {app_name.capitalize()}."
        
    except subprocess.CalledProcessError as e:
        # Captures OS-level errors (e.g., app not installed, permission denied)
        error_msg = e.stderr.strip() if e.stderr else "Unknown OS error."
        return f"Execution Error: Failed to open {app_name.capitalize()}. (Code: {e.returncode}, Error: {error_msg})"
        
    except FileNotFoundError:
        # Triggers if the 'am' command isn't found in the system path
        return "System Error: 'am' command not found. Ensure JARVIS is running in a Termux environment with correct path variables."
        
    except Exception as e:
        # Ultimate fallback to prevent total system crash
        return f"Unexpected Error launching {app_name.capitalize()}: {str(e)}"
