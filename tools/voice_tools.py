import os
import subprocess
import time
import tempfile
import urllib.request
import json
import socket

# --- CONSTANTS ---
WHISPER_HOST = "127.0.0.1"
WHISPER_PORT = 8080
WHISPER_MODEL = os.path.expanduser("~/whisper.cpp/models/ggml-tiny.en.bin")
WHISPER_CLI_BIN = os.path.expanduser("~/whisper.cpp/build/bin/whisper-cli")

def get_whisper_server_bin():
    """Detects the server binary based on whisper.cpp compilation naming."""
    paths = [
        os.path.expanduser("~/whisper.cpp/build/bin/whisper-server"),
        os.path.expanduser("~/whisper.cpp/build/bin/server")
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return paths[0] 

def is_whisper_server_running():
    """Checks if the whisper server socket is responsive."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((WHISPER_HOST, WHISPER_PORT)) == 0

def start_whisper_server():
    """Starts the whisper.cpp server in the background if not already running."""
    if is_whisper_server_running():
        print("[DEBUG] whisper-server is already loaded in RAM.")
        return True

    print("[DEBUG] Starting whisper-server...")
    server_bin = get_whisper_server_bin()
    
    if not os.path.exists(server_bin):
        print(f"[System Error] whisper-server binary not found at {server_bin}.")
        return False

    if not os.path.exists(WHISPER_MODEL):
        print(f"[System Error] Model not found at {WHISPER_MODEL}. Check path.")
        return False

    cmd = [
        server_bin,
        "-m", WHISPER_MODEL,
        "--host", WHISPER_HOST,
        "--port", str(WHISPER_PORT)
    ]
    
    # Launch detached daemon safely
    try:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"[System Error] Failed to launch whisper-server process: {e}")
        return False
    
    # Wait for the model to load into memory
    for _ in range(15):
        time.sleep(1)
        if is_whisper_server_running():
            print("[DEBUG] whisper-server successfully started.")
            return True

    print("[System Error] whisper-server failed to start or timed out.")
    return False

def speak(text):
    """Outputs text to Android's native Text-to-Speech using Termux:API."""
    if not text: 
        return
    try:
        subprocess.run(["termux-tts-speak", text], check=True)
    except Exception as e:
        print(f"[TTS Error]: {e}")

def transcribe_with_server(wav_path):
    """Sends the WAV file to the local API endpoint for instant transcription."""
    t_start = time.time()
    
    url = f"http://{WHISPER_HOST}:{WHISPER_PORT}/inference"
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    headers = {'Content-Type': f'multipart/form-data; boundary={boundary}'}

    try:
        with open(wav_path, 'rb') as f:
            audio_data = f.read()

        body = (
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="file"; filename="audio.wav"\r\n'
            f'Content-Type: audio/wav\r\n\r\n'.encode('utf-8') +
            audio_data +
            f'\r\n--{boundary}--\r\n'.encode('utf-8')
        )
        
        t_prep = time.time()
        print(f"[TIMER-DEBUG] Server Req Prep took: {t_prep - t_start:.2f}s")

        req = urllib.request.Request(url, data=body, headers=headers, method='POST')
        
        print("[TIMER-DEBUG] Sending to Server (Waiting for inference...)")
        with urllib.request.urlopen(req, timeout=60) as response:
            t_infer = time.time()
            print(f"[TIMER-DEBUG] Server Inference Block took: {t_infer - t_prep:.2f}s")
            
            res_body = response.read()
            t_read = time.time()
            print(f"[TIMER-DEBUG] Reading Response took: {t_read - t_infer:.2f}s")
            
            print("[DEBUG] RAW SERVER RESPONSE:")
            print(res_body.decode("utf-8", errors="ignore"))
            data = json.loads(res_body)
            text = data.get('text', '').strip()

            # Filter out hallucinated silence tags common in Whisper
            if text.startswith("[") and text.endswith("]"):
                return ""
            return text

    except Exception as e:
        print(f"[DEBUG] Server Transcription Error: {e}")
        return None  # Return None to explicitly trigger the CLI fallback

def transcribe_with_cli(wav_path):
    """Fallback mechanism using whisper-cli if the server is unavailable."""
    print("[DEBUG] Falling back to whisper-cli transcription...")
    
    # Fallback to older 'main' binary naming if 'whisper-cli' doesn't exist
    bin_path = WHISPER_CLI_BIN
    if not os.path.exists(bin_path):
        alt_path = os.path.expanduser("~/whisper.cpp/main")
        if os.path.exists(alt_path):
            bin_path = alt_path
        else:
            print("[System Error] whisper-cli binary not found.")
            return ""
            
    if not os.path.exists(WHISPER_MODEL):
        print(f"[System Error] Whisper model not found at {WHISPER_MODEL}")
        return ""

    whisper_cmd = [
        bin_path,
        "-m", WHISPER_MODEL,
        "-f", wav_path,
        "-nt", "-np"
    ]
    
    try:
        result = subprocess.run(whisper_cmd, capture_output=True, text=True, check=True)
        text = result.stdout.strip().replace("\n", " ")
        
        if not text or (text.startswith("[") and text.endswith("]")):
            return ""
        return text
        
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else str(e)
        print(f"[DEBUG] whisper-cli Execution Error: {error_msg}")
        return ""
    except Exception as e:
        print(f"[DEBUG] whisper-cli Unexpected Error: {e}")
        return ""

def listen(duration=5):
    """
    Records audio via Termux, converts it using FFmpeg, and transcribes locally.
    Prioritizes whisper-server, but gracefully falls back to whisper-cli on failure.
    """
    t0 = time.time()
    temp_dir = tempfile.gettempdir()
    raw_audio_path = os.path.join(temp_dir, "jarvis_raw_audio.m4a")
    wav_audio_path = os.path.join(temp_dir, "jarvis_16k_audio.wav")

    try:
        # 1. Start Recording Audio
        print(f"[DEBUG] listen(): Recording audio for {duration} seconds...")
        subprocess.run(["termux-microphone-record", "-f", raw_audio_path], check=True)
        
        time.sleep(duration)
        print("[DEBUG] Stopping microphone...")
        
        # Stop Recording
        subprocess.run(["termux-microphone-record", "-q"], check=True)
        print("[DEBUG] Microphone stopped.")
        time.sleep(0.3) # Buffer to let the file save completely to Android storage
        
        print(f"[TIME] Recording: {time.time()-t0:.2f}s")

        # Validate recording success
        if not os.path.exists(raw_audio_path) or os.path.getsize(raw_audio_path) == 0:
            print("[DEBUG] listen(): Error - Raw audio file was not created or is empty.")
            return ""

        # 2. Convert Audio via FFmpeg to Whisper-compliant WAV
        print("[DEBUG] listen(): Converting audio via FFmpeg...")
        t1 = time.time()
        ffmpeg_cmd = [
            "ffmpeg", 
            "-y", 
            "-i", raw_audio_path,
            "-ar", "16000",
            "-ac", "1",
            "-c:a", "pcm_s16le",
            wav_audio_path
        ]
        
        subprocess.run(ffmpeg_cmd, capture_output=True, check=True)
        
        print(f"[TIME] FFmpeg: {time.time()-t1:.2f}s")

        if not os.path.exists(wav_audio_path) or os.path.getsize(wav_audio_path) == 0:
            print("[DEBUG] listen(): Error - FFmpeg conversion failed or output is empty.")
            return ""

        # 3. Transcribe Audio (Server Primary)
        transcribed_text = None
        
        if is_whisper_server_running():
            print("[DEBUG] listen(): Transcribing via whisper-server...")
            t2 = time.time()
            transcribed_text = transcribe_with_server(wav_audio_path)
            if transcribed_text is not None:
                print(f"[TIME] Whisper Server: {time.time()-t2:.2f}s")
        else:
            print("[DEBUG] listen(): whisper-server is not running. Attempting auto-start...")
            start_whisper_server()
            if is_whisper_server_running():
                print("[DEBUG] listen(): Transcribing via whisper-server...")
                t2 = time.time()
                transcribed_text = transcribe_with_server(wav_audio_path)
                if transcribed_text is not None:
                    print(f"[TIME] Whisper Server: {time.time()-t2:.2f}s")

        # 4. Transcribe Audio (CLI Fallback)
        if transcribed_text is None:
            transcribed_text = transcribe_with_cli(wav_path=wav_audio_path)

        final_text = transcribed_text if transcribed_text else ""
        print(f"[TIME] Total Voice Pipeline: {time.time()-t0:.2f}s")
        return final_text

    except Exception as e:
        print(f"[DEBUG] listen(): Critical Error in audio pipeline: {e}")
        return ""
        
    finally:
        # 5. Guaranteed File Cleanup
        try:
            if os.path.exists(raw_audio_path):
                os.remove(raw_audio_path)
            if os.path.exists(wav_audio_path):
                os.remove(wav_audio_path)
        except Exception as e:
            print(f"[DEBUG] listen(): Failed to clean temp files: {e}")
