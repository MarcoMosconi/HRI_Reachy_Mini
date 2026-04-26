import sys
import subprocess
import pyttsx3
import speech_recognition as sr
import asyncio
import edge_tts

async def speak_neural(text, voice="it-IT-DiegoNeural", rate="+0%", pitch="+0Hz"):
    communicate = edge_tts.Communicate(text, voice=voice, rate=rate, pitch=pitch)
    await communicate.save("speech.mp3")

# Cross-platform TTS (see Part 1 for explanation)
def speak(text, mini=None):
    print(f"[Robot]: {text}")
    if mini:
        mini.goto_target(antennas=[0.3, -0.3], duration=0.2)
    if sys.platform == "darwin":
        subprocess.run(["say", "-v", "Samantha", "-r", "160", text])
    else:
        # engine = pyttsx3.init()
        # engine.setProperty('rate', 160)
        # engine.say(text)
        # engine.runAndWait()
        # engine.stop()
        asyncio.run(speak_neural(text))
        subprocess.run(["ffplay", "-nodisp", "-autoexit", "speech.mp3"], 
                       capture_output=True)
    if mini:
        mini.goto_target(antennas=[0.0, 0.0], duration=0.2)

recognizer = sr.Recognizer()
def listen():
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("[Listening...]")
            audio = recognizer.listen(source, timeout=8)
        text = recognizer.recognize_google(audio)
        print(f"[User]: {text}")
        return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        print("Speech recognition service unavailable.")
        return ""
    except sr.WaitTimeoutError:
        return ""
    

speak("Helloooooo! It's mee, Mario!!!")
# async def list_voices():
#     voices = await edge_tts.list_voices()
#     for v in voices:
#         if v["Locale"].startswith("it"):
#             print(v["ShortName"], "-", v["Gender"])

# asyncio.run(list_voices())