from database.memory_repo import save_memory, get_memory, update_memory

def handle_memory_commands(user_input):
    if user_input.startswith("remember "):
        parts = user_input.split(" ", 2)
        if len(parts) < 3:
            print("JARVIS > Usage: remember <key> <value>")
        else:
            key = parts[1]
            value = parts[2]
            save_memory(key, value)
            print(f"JARVIS > Saved '{key}'")
        return True

    elif user_input.startswith("recall "):
        key = user_input.split(" ", 1)[1]
        value = get_memory(key)
        if value:
            print(f"JARVIS > {value}")
        else:
            print("JARVIS > I don't know that yet.")
        return True

    elif user_input.startswith("update memory "):
        parts = user_input[len("update memory "):].strip().split(" ", 1)
        if len(parts) < 2:
            print("JARVIS > Usage: update memory <key> <value>")
        else:
            key = parts[0].strip()
            val = parts[1].strip()
            if not val:
                print("JARVIS > Memory value cannot be empty.")
            elif get_memory(key) is not None:
                update_memory(key, val)
                print(f"JARVIS > Memory '{key}' updated.")
            else:
                print(f"JARVIS > Memory '{key}' not found. Use 'remember' to create it.")
        return True

    return False
