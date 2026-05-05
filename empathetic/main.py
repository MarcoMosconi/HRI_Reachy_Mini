from google import genai
from google.genai.types import GenerateContentConfig
from pydantic import BaseModel, Field
import os
import sys
import re
from reachy_mini import ReachyMini
import time
import pandas as pd

current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)
    
from dialogue import speak, listen
from emotions import play_emotion

# retry if api crashes
GEMINI_MODEL = "gemini-2.5-flash"

def call_llm(client, prompt, retries=3):
    """Call Gemini with exponential backoff retry on failure."""
    for i in range(retries):
        try:
            return client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt
            )
        except Exception as e:
            if i < retries - 1:
                wait = 2 ** i
                print(f"[API error] {e} — retrying in {wait}s...")
                time.sleep(wait)
            else:
                print(f"[API error] Failed after {retries} attempts: {e}")
                raise e
def send_chat_with_retry(chat, prompt, retries=3):
    """Send a chat message with exponential backoff retry on failure."""
    for i in range(retries):
        try:
            return chat.send_message(prompt)
        except Exception as e:
            if i < retries - 1:
                wait = 15 * (i + 1) 
                print(f"[API error] {e} — retrying in {wait}s...")
                time.sleep(wait)
            else:
                print(f"[API error] Failed after {retries} attempts: {e}")
                raise e

# Define a prompt that helps with DST
system_prompt = "You are a friendly and empathetic social robot conducting a brief weekly mental health check-in with a university student. Your name is BillyBob. \
Your purpose is to help the student reflect on their week, gently assess their mental state, and offer supportive responses. You are not a therapist — you are a caring, non-judgmental companion. Always encourage the student to speak to a counsellor or trusted person if they express serious distress. \
Keep your responses to maximum 2 sentences. Do not ask follow-up questions."

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
# questions = [
#     "Over the last 2 weeks, how often have you been feeling nervous, anxious or on edge?",
#     # "Ask the visitor what brings them here today.",
#     "What brings you here today?",
#     # "Thank them and say goodbye."
#     "It was lovely chatting with you. Take care and goodbye!"
# ]

EMPATHY_MODE = True  # True = empathetic, False = neutral
CSV_PATH = os.path.join(parent_dir, "question_tree.csv")

df = pd.read_csv(CSV_PATH)
questions = []

for _, row in df.iterrows():
    questions.append({
        "text": row["question_empathy"] if EMPATHY_MODE else row["question_neutral"],
        "pre_prompt": row["pre_prompt"],
        "section": row["questionnaire"],
    })

# TODO: create a chat with the config and connect to the robot
# Set GEMINI_API_KEY as an environment variable before running
client = genai.Client()
# this will start a new chat that handles history automatically
chat = client.chats.create(model="gemini-2.5-flash",
                           config=config
                          )

scores = {"GAD-7": [], "PHQ-9": [], "CAGE": []}

topic_idx = 0
with ReachyMini(media_backend="no_media") as mini:
    while topic_idx < len(questions):
        # current_topic = questions[topic_idx]
        # speak(current_topic, mini=mini)
        current_text = questions[topic_idx]["text"]
        pre_prompt = questions[topic_idx]["pre_prompt"]
        section = questions[topic_idx]["section"]

        if topic_idx == 0 or section != questions[topic_idx - 1]["section"]:
            speak(pre_prompt, mini=mini)

        speak(current_text, mini=mini)

        user_input = listen(mini=mini)  
        if not user_input:
            speak("Sorry I didn't catch that.", mini=mini)
            continue

        prompt = f"[Current topic: {current_text}]\nUser said: {user_input}"        # ask gemini to classify answer as 0 if it indicates the user is doing well, or 1 if it indicates the user is struggling
        classification = None
        # if topic_idx == 0:
            # class_prompt = (
            #     "The question given to the user is 'Over the last 2 weeks, how often have you been feeling nervous, anxious or on edge?'."
            #     "Classify the user's answer as 0 if it indicates the user is doing well, "
            #     "or 1 if it indicates the user is struggling. Respond with only the single "
            #     "digit 0 or 1. If the answer is unclear, respond with None. \n\nUser answer: " + user_input
            # )
        class_prompt = (
            f"The user was asked: '{current_text}'. "
            "Classify their answer into one of these categories:\n"
            "0 = Not at all\n"
            "1 = Several days\n"
            "2 = More than half the days\n"
            "3 = Nearly every day\n"
            "Respond with only a single digit: 0, 1, 2, or 3. "
            "If the answer is unclear, respond with 0.\n\n"
            "User answer: " + user_input
        )
        try:
            # class_raw = client.models.generate_content(
            #     model="gemini-2.5-flash",
            #     contents=class_prompt).text
            class_raw = call_llm(client, class_prompt).text
            m = re.search(r'\b([0-3])\b', class_raw)
            if m:
                classification = int(m.group(1))
            else:
                classification = 0

            print(f"I've classified your response as {classification}.")
            scores[section].append(classification)

            if classification == 0:
                play_emotion(mini, "proud1")
            elif classification == 1:
                play_emotion(mini, "attentive1")
            elif classification == 2:
                play_emotion(mini, "sad2")
            elif classification == 3:
                play_emotion(mini, "sad2")
        except Exception as e:
            print(f"Classification failed: {e}")

        # get chat response
        try:
            raw = send_chat_with_retry(chat, prompt).text
            response = ResponseWithState.model_validate_json(raw)
            speak(response.reply, mini=mini)
            # if response.next_state:
            topic_idx += 1
        except Exception as e:
            print(f"[Chat failed]: {e}")
            speak("I'm sorry, I'm having technical difficulties. We'll have to stop here for today. Thank you for your time.", mini=mini)
            break

gad_total = sum(scores["GAD-7"])
if gad_total <= 4:
    gad_level = "Minimal anxiety"
elif gad_total <= 9:
    gad_level = "Mild anxiety"
elif gad_total <= 14:
    gad_level = "Moderate anxiety"
else:
    gad_level = "Severe anxiety"
 
phq_total = sum(scores["PHQ-9"])
if phq_total <= 4:
    phq_level = "Minimal depression"
elif phq_total <= 9:
    phq_level = "Mild depression"
elif phq_total <= 14:
    phq_level = "Moderate depression"
elif phq_total <= 19:
    phq_level = "Moderately severe depression"
else:
    phq_level = "Severe depression"
 
cage_total = sum(scores["CAGE"])
cage_level = "High risk" if cage_total >= 2 else "Low risk"
 
print("\n" + "="*40)
print("ASSESSMENT COMPLETE")
print("="*40)
print(f"GAD-7 : {gad_total} → {gad_level}")
print(f"PHQ-9 : {phq_total} → {phq_level}")
print(f"CAGE  : {cage_total} → {cage_level}")
print("="*40)

                  
        # # TODO: send message and get response
        # raw = chat.send_message(prompt).text

        # # parse text response into python object
        # response = ResponseWithState.model_validate_json(raw)
        # speak(response.reply, mini=mini)

        # # check if should change topic
        # if response.next_state:
        # topic_idx += 1