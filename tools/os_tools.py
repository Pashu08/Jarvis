def execute_tool(intent, payload=None):
    """
    Central execution engine for the Tool Subsystem. Receives routed intents 
    and handles system, OS, and application-level execution hooks.
    
    Args:
        intent (str): The specific tool action to execute.
        payload (str, optional): Target data, such as a specific app name or arguments.
        
    Returns:
        str: A descriptive execution status message or an error message.
    """
    try:
        # Route specific known app shortcuts
        if intent == "open_whatsapp":
            return _handle_app_launch("WhatsApp")
            
        elif intent == "open_discord":
            return _handle_app_launch("Discord")
            
        elif intent == "open_chrome":
            return _handle_app_launch("Chrome")
            
        elif intent == "open_browser":
            return _handle_app_launch("Browser")
            
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
    Helper function to abstract application launching logic.
    """
    # Clean the app name for consistent messaging
    target_app = app_name.strip()
    
    # FUTURE EXPANSION: Insert real Android Automation / OS-level hooks here.
    # For Android automation via Termux, ADB, or Python frameworks (like Kivy/Pyjnius), 
    # you will replace this return block with intent launching code:
    # 
    # Example (Android Intent via Termux API):
    # import subprocess
    # subprocess.run(["termux-open-url", f"intent:#Intent;component={package_name};end"])
    #
    # Example (ADB command injection for desktop development):
    # import os
    # os.system(f"adb shell monkey -p {package_name} -c android.intent.category.LAUNCHER 1")
    
    return f"Opening {target_app}..."
