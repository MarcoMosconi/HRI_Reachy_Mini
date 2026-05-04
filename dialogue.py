import sys
import subprocess
import time
import pyttsx3
import speech_recognition as sr
import asyncio
import edge_tts
from reachy_mini import ReachyMini
from reachy_mini.motion.recorded_move import RecordedMoves
import threading

emotions = RecordedMoves("pollen-robotics/reachy-mini-emotions-library")

async def speak_neural(text, voice="en-US-AndrewMultilingualNeural", rate="+0%", pitch="+0Hz"):
    communicate = edge_tts.Communicate(text, voice=voice, rate=rate, pitch=pitch)
    await communicate.save("speech.mp3")

# Cross-platform TTS (see Part 1 for explanation)
def speak(text, mini=None, emotion="welcoming1"):
    print(f"[Robot]: {text}")
    stop_event = threading.Event()

    async def run_movement():
        if mini:
            while not stop_event.is_set():
                await mini.async_play_move(emotions.get(emotion), sound=False)
                await asyncio.sleep(0.1)
    
    def run_speech():
        try:
            if sys.platform == "darwin":
                subprocess.run(["say", "-v", "Samantha", "-r", "160", text])
            else: 
                asyncio.run(speak_neural(text))
                subprocess.run(["ffplay", "-nodisp", "-autoexit", "speech.mp3"], 
                            capture_output=True)
        finally:
            stop_event.set()
    speech_thread = threading.Thread(target=run_speech)
    speech_thread.start()

    if mini:
        asyncio.run(run_movement())
    speech_thread.join()



recognizer = sr.Recognizer()

def listen(mini=None, emotion="attentive1", use_whisper=False):
    """Listen for user input and transcribe to text.
    
    Args:
        mini: ReachyMini instance for animations
        emotion: Emotion animation to play while listening
        use_whisper: If True, use local Whisper model. If False, use Google Speech Recognition.
    """
    audio = None
    stop_event = threading.Event()

    def run_audio():
        nonlocal audio
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("[Listening...]")
                audio = recognizer.listen(source, timeout=8)
        except sr.WaitTimeoutError:
            return ""
        finally:
            stop_event.set()
        
    async def run_movement():
        if mini:
            while not stop_event.is_set():
                await mini.async_play_move(emotions.get(emotion), sound=False)
                await asyncio.sleep(0.1)
    audio_thread = threading.Thread(target=run_audio)
    audio_thread.start()
    if mini:
        asyncio.run(run_movement())
    audio_thread.join()
    if audio is None:
        return ""
    
    try:
        if use_whisper:
            # Use local Whisper model (no internet required)
            import whisper
            import numpy as np
            
            # Convert audio to numpy array
            audio_data = np.frombuffer(audio.get_wav_data(), dtype=np.int16).astype(np.float32) / 32768.0
            
            # Load Whisper model and transcribe
            model = whisper.load_model("base")
            result = model.transcribe(audio_data)
            text = result["text"].strip()
        else:
            # Use Google Speech Recognition (requires internet)
            text = recognizer.recognize_google(audio)
        
        print(f"[User]: {text}")
        return text
    except sr.UnknownValueError:
        print("[Could not understand audio]")
        return ""
    except sr.RequestError:
        print("Speech recognition service unavailable.")
        return ""
    except Exception as e:
        print(f"[Speech recognition error]: {e}")
        return ""
    
    


# async def list_voices():
#     voices = await edge_tts.list_voices()
#     for v in voices:
#         if v["Locale"].startswith("en"):
#             print(v["ShortName"], "-", v["Gender"])

# asyncio.run(list_voices())


# with ReachyMini(media_backend="no_media") as mini:
#     speak("Hello! I'm your empathetic robot companion. How are you feeling today?", mini=mini)
#     user_input = listen(mini=mini)