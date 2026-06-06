import subprocess

# Scalable mapping for Android app components
# Format: "app_name_in_lowercase": "package.name/component.Activity"
APP_COMPONENTS = {
    "whatsapp": "com.whatsapp/.Main",
    "discord": "com.discord/.main.MainActivity",
    "chrome": "com.android.chrome/com.google.android.apps.chrome.Main",
    "browser": "com.android.chrome/com.google.android.apps.chrome.Main",
    "youtube": "com.google.android.youtube/com.google.android.youtube.HomeActivity",
    "gmail": "com.google.android.gm/.ConversationListActivityGmail",
    "camera": "com.android.camera/.Camera",
    "calculator": "com.google.android.calculator/com.android.calculator2.Calculator",
    "settings": "com.android.settings/.Settings",
    "files": "com.google.android.documentsui/com.android.documentsui.files.FilesActivity",
    "google maps": "com.google.android.apps.maps/com.google.android.maps.MapsActivity",
    "maps": "com.google.android.apps.maps/com.google.android.maps.MapsActivity"
}

def execute_tool(intent, payload=None):
    """
    Central execution engine for the Tool Subsystem. 
    Receives routed intents and handles dynamic Android app launches.
    """
    try:
        # Dynamically handle any intent starting with "open_"
        if intent.startswith("open_"):
            
            # If it's the catch-all "open_app" intent, we must rely on the payload
            if intent == "open_app":
                if not payload:
                    return "Error: Cannot open application without a target application name."
                target_app = payload.strip().lower()
                
            # Otherwise, extract the app name directly from the intent (e.g., "open_whatsapp" -> "whatsapp")
            else:
                target_app = intent.replace("open_", "").strip().lower()

            return _handle_app_launch(target_app)

        # Handle unrecognized tool intents gracefully
        return f"Error: Tool intent '{intent}' is currently unsupported by this execution layer."

    except Exception as e:
        # Prevent runtime crashes
        return f"Execution Error: Failed to process tool action due to: {str(e)}"

def _handle_app_launch(app_name):
    """
    Executes Android Activity Manager (am) commands to launch applications via Termux.
    """
    # Look up the exact Android component name from the registry
    component = APP_COMPONENTS.get(app_name)
    
    if not component:
        return f"Error: Application '{app_name}' is not registered in the APP_COMPONENTS dictionary."

    try:
        # Execute the required Termux 'am start -n <component>' command
        result = subprocess.run(
            ["am", "start", "-n", component],
            capture_output=True,
            text=True,
            check=True
        )
        return f"Successfully opened {app_name.title()}."
        
    except subprocess.CalledProcessError as e:
        # Captures OS-level errors (e.g., app not installed, incorrect component name)
        error_msg = e.stderr.strip() if e.stderr else "Unknown OS error."
        return f"Execution Error: Failed to open {app_name.title()}. (Code: {e.returncode}, Error: {error_msg})"
        
    except FileNotFoundError:
        # Triggers if the 'am' command isn't found in the system path
        return "System Error: 'am' command not found. Ensure JARVIS is running in a Termux environment."
        
    except Exception as e:
        # Ultimate fallback
        return f"Unexpected Error launching {app_name.title()}: {str(e)}"
