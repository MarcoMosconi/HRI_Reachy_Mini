from reachy_mini.motion.recorded_move import RecordedMoves
from reachy_mini import ReachyMini
import asyncio
import subprocess
import platform

emotions = RecordedMoves("pollen-robotics/reachy-mini-emotions-library")

def play_sound(sound_path):
    if sound_path is None:
        return
    system = platform.system()
    if system == "Darwin":      # Mac
        subprocess.Popen(["afplay", sound_path])
    elif system == "Linux":
        subprocess.Popen(["aplay", sound_path])   #or paplay
    elif system == "Windows":
        import winsound
        winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)

def play_emotion(mini, move_name):
    move = emotions.get(move_name)
    play_sound(move.sound_path)
    asyncio.run(mini.async_play_move(move, sound=False))

