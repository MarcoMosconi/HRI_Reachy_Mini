
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

# Define a prompt that helps with DST
system_prompt = "You are a friendly and empathetic social robot conducting a brief weekly mental health check-in with a university student. Your name is BillyBob. \
Your purpose is to help the student reflect on their week, gently assess their mental state, and offer supportive responses. You are not a therapist — you are a caring, non-judgmental companion. Always encourage the student to speak to a counsellor or trusted person if they express serious distress."

class ResponseWithState(BaseModel):
    reply: str = Field(description="Empathetic response to the user input, based on the current topic")
    next_state: bool = Field(description="True if the conversation has wrapped up and is ready to move to the next topic")

# pass this config when creating a chat
config = GenerateContentConfig(
    system_instruction=system_prompt,
    response_mime_type="application/json",
    response_json_schema=ResponseWithState.model_json_schema()
)

# Define some topics you want to talk about
questions = [
    "Over the last 2 weeks, how often have you been feeling nervous, anxious or on edge?",
    "Ask the visitor what brings them here today.",
    "Thank them and say goodbye."
]

# TODO: create a chat with the config and connect to the robot
# Set GEMINI_API_KEY as an environment variable before running
client = genai.Client()
# this will start a new chat that handles history automatically
chat = client.chats.create(model="gemini-2.5-flash",
                           config=config
                          )

topic_idx = 0
with ReachyMini(media_backend="no_media") as mini:
    while topic_idx < len(questions):
        current_topic = questions[topic_idx]
        speak(current_topic, mini=mini)
        
        user_input = listen(mini=mini)  
        if not user_input:
            speak("Sorry I didn't catch that.", mini=mini)
            continue

        prompt = f"[Current topic: {current_topic}]\nUser said: {user_input}"
        # ask gemini to classify answer as 0 if it indicates the user is doing well, or 1 if it indicates the user is struggling
        classification = None
        if topic_idx == 0:
            class_prompt = (
                "The question given to the user is 'Over the last 2 weeks, how often have you been feeling nervous, anxious or on edge?'."
                "Classify the user's answer as 0 if it indicates the user is doing well, "
                "or 1 if it indicates the user is struggling. Respond with only the single "
                "digit 0 or 1. If the answer is unclear, respond with None. \n\nUser answer: " + user_input
            )
            class_raw = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=class_prompt).text
            m = re.search(r'\b([01])\b', class_raw)
            if m:
                classification = int(m.group(1))
            else:
                # best-effort fallback
                m2 = re.search(r'([01])', class_raw)
                if m2:
                    classification = int(m2.group(1))

            if classification is not None:
                print(f"I've classified your response as {classification}.")
                play_emotion(mini, "sad2") if classification == 1 else play_emotion(mini, "proud1")
            else:
                print("I couldn't classify your answer reliably.")

        # TODO: send message and get response
        raw = chat.send_message(prompt).text

        # parse text response into python object
        response = ResponseWithState.model_validate_json(raw)
        speak(response.reply, mini=mini)

        # check if should change topic
        if response.next_state:
            topic_idx += 1