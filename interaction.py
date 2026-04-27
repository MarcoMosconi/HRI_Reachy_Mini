from google import genai
from google.genai.types import GenerateContentConfig
from pydantic import BaseModel, Field
import os
import sys
import re
from reachy_mini import ReachyMini


current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)
    
from dialogue import speak, listen
from emotions import play_emotion
from prompt_interactions import get_csv, get_prompt, Interaction


df = get_csv("question_tree.csv")

client = genai.Client()
chat = client.chats.create(model="gemini-2.5-flash")

interactions = []
for index, row in df.iterrows():
    interaction = Interaction(
        q_empathetic=row["question_empathy"],
        q_neutral=row["question_neutral"],
        q_type=row["questionnaire"]
    )
    interactions.append(interaction)

empathy = True
emotion_speak = "welcoming1"
for i, interaction in enumerate(interactions):
    with ReachyMini(media_backend="no_media") as mini:
        speak(interaction.get_question(empathy), mini=mini, emotion=emotion_speak)
        user_input = listen(mini=mini)  
        if not user_input:
            speak("Sorry I didn't catch that.", mini=mini)
            continue
        
        if i+1 < len(interactions):
            next_q_empathy = interactions[i+1].get_question(empathy)
            prompt = get_prompt(interaction.get_question(empathy), user_input, next_q_empathy)
        else:
            close = "Thank you for sharing with me. I hope you have a great week ahead! Remember, I'm always here if you want to talk again."
            prompt = get_prompt(interaction.get_question(empathy), user_input, close)

        llm_text = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )
        

