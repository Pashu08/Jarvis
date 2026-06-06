from database.note_repo import add_note, get_notes, get_note_by_id, update_note, search_notes_db

def handle_note_commands(user_input):
    if user_input.startswith("add note "):
        note = user_input[len("add note "):].strip()
        if note:
            add_note(note)
            print("JARVIS > Note saved.")
        else:
            print("JARVIS > Note cannot be empty.")
        return True

    elif user_input == "list notes":
        notes = get_notes()
        if not notes:
            print("JARVIS > No notes found.")
        else:
            print("JARVIS > Notes:")
            for note_id, content in notes:
                print(f"{note_id}. {content}")
        return True

    elif user_input.startswith("edit note "):
        parts = user_input[len("edit note "):].strip().split(" ", 1)
        if len(parts) < 2:
            print("JARVIS > Usage: edit note <id> <new text>")
        else:
            try:
                note_id = int(parts[0])
                new_text = parts[1].strip()
                if not new_text:
                    print("JARVIS > Note content cannot be empty.")
                elif get_note_by_id(note_id) is not None:
                    update_note(note_id, new_text)
                    print("JARVIS > Note updated.")
                else:
                    print("JARVIS > Note not found.")
            except ValueError:
                print("JARVIS > Invalid note ID.")
        return True

    elif user_input.startswith("find note "):
        keyword = user_input[len("find note "):].strip()
        matched_notes = search_notes_db(keyword)
        print("\n===== NOTE SEARCH RESULTS =====\n")
        if matched_notes:
            for note_id, content in matched_notes:
                print(f"{note_id}. {content}")
        else:
            print("No matching notes found.")
        print("\n===============================\n")
        return True

    return False
