import subprocess

def speak(text):
    """
    Outputs text to Android's native Text-to-Speech using Termux:API.
    """
    if not text:
        return
    try:
        subprocess.run(["termux-tts-speak", text], check=True)
    except Exception as e:
        print(f"[TTS Error]: {e}")

def listen():
    """
    Triggers the Android Google Speech Recognition UI and returns the transcribed text.
    """
    try:
        result = subprocess.run(
            ["termux-speech-to-text"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"[STT Error]: {e}")
        return ""
