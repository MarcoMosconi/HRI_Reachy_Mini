from google import genai
from google.genai.types import GenerateContentConfig
from pydantic import BaseModel, Field
import os
import sys
import re
from reachy_mini import ReachyMini
import time

current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)
    
from dialogue import speak, listen
from emotions import play_emotion
from prompt_interactions import get_csv, get_prompt, Interaction, get_intro, get_close, read_LLM_response


# ============ LLM Configuration ============
USE_OLLAMA = False  # Set to True to use Ollama, False for Google Gemini
OLLAMA_MODEL = "llama3.2:1b"  # Change to your preferred Ollama model

# Initialize LLM client and create response function
if USE_OLLAMA:
    import ollama
    def get_llm_response(prompt):
        """Send prompt to Ollama and get response text"""
        # add retry logic here similar to Gemini
        try:
            response = ollama.generate(model=OLLAMA_MODEL, prompt=prompt, stream=False)
            return response['response']
        except Exception as e:
            print(f"[Ollama error] {e}")
            raise e
else:
    client = genai.Client()
    chat = client.chats.create(model="gemini-2.5-flash")
    def get_llm_response(prompt, retries = 3):
        """Send prompt to Gemini and get response text"""
        for i in range(retries):
            # add retry logic here 
            try:
                return chat.send_message(prompt).text
            except Exception as e:
                if i < retries - 1:
                    wait = 15* (i + 1)
                    print(f"[API error] {e} - retrying in {wait}s ")
                    time.sleep(wait)
                else:
                    print(f"[API error] Failed after {retries} attempts: {e}")
                    raise e
        # return chat.send_message(prompt).text
# ==========================================

df = get_csv("question_tree.csv")

interactions = []
for index, row in df.iterrows():
    interaction = Interaction(
        q_empathetic=row["question_empathy"],
        q_neutral=row["question_neutral"], 
        q_type=row["questionnaire"]
    )
    interactions.append(interaction)

empathy = True
emotion_speak = None
anxiety = 4
depression = 10
user_input = None
depression_score = 0
scores = {"GAD-7": [], "PHQ-9": [], "CAGE": []}

print("Connected to Reachy Mini! ")
    

with ReachyMini(media_backend="no_media") as mini:

    print("Wiggling antennas...")
    mini.goto_target(antennas=[0.5, -0.5], duration=0.2)
    mini.goto_target(antennas=[-0.5, 0.5], duration=0.2)
    mini.goto_target(antennas=[0, 0], duration=0.01)


    for i, interaction in enumerate(interactions):
        if i == 0:
            prompt = get_intro(interaction.get_question(empathy), empathy)
        elif i > 0 and i < anxiety:
            preprompt = "Over the last 2 weeks, how often have you been bothered by the following problems?"
            prompt = get_prompt(interaction.get_question(empathy), user_input, interactions[i+1].get_question(empathy), empathy=empathy, preprompt=preprompt)
        elif i == anxiety:
            if empathy:
                preprompt = f"Great job answering those questions regarding anxiety, I know that wasn't easy. Lets continue by talking about depression to make sure we have all bases covered.\
                Over the last 2 weeks, how often have you been bothered by the following problems?"
            else:
                preprompt = f"Thank you for answering the questions about anxiety, we will continue with questions regarding depression.\
                Over the last 2 weeks, how often have you been bothered by the following problems?"
            prompt = get_prompt(interaction.get_question(empathy), user_input, interactions[i+1].get_question(empathy), empathy=empathy, preprompt=preprompt)
        elif i > anxiety and i <= depression:
            preprompt = ""
            prompt = get_prompt(interaction.get_question(empathy), user_input, interactions[i+1].get_question(empathy), empathy=empathy, preprompt=preprompt)
        elif i == depression:
            if empathy:
                preprompt = "I want to ask you some questions about your alcohol consumption."
            else:
                preprompt = "Hey lets talk about your alcohol consumption. I just want to see were we stand there."
            prompt = get_prompt(interaction.get_question(empathy), user_input, interactions[i+1].get_question(empathy), empathy=empathy, preprompt=preprompt)
        else:
            # TODO: add overall assessment at the end based on all the answers and assessments from before
            # TODO: accumalted score and give overall assessment at the end
            prompt = get_close(empathy=empathy)
        
        if i == 0:
            next_communication = get_llm_response(prompt)
        else:
            category, next_communication, robot_emotion = None, None, None
            for attempt in range(3):
                try:
                    llm_text = get_llm_response(prompt)
                    category, next_communication, robot_emotion = read_LLM_response(llm_text)
                    break 
                except Exception as e:
                    print(f"[Attempt {attempt + 1} / 3 failed]: {e}")
                    if attempt == 2:  # if it is the last attempt, raise the error
                        print("[Skipping this question]")
                        next_communication = "Lets move on the next question."

            if category is not None:
                interactions[i-1].ans = user_input
                interactions[i-1].assessment = category
                next_emotion = robot_emotion
                print(next_emotion)
                # depression_score += int(category) 
                section = interaction.q_type
                if section in scores:
                    scores[section].append(int(category))

                if category == 0:
                    emotion_speak = "proud1"
                elif category == 1:
                    emotion_speak = "attentive1"
                elif category == 2:
                    emotion_speak = "sad1"
                elif category == 3:
                    emotion_speak = "sad2"


            # llm_text = get_llm_response(prompt)
            # category, next_communication, robot_emotion = read_LLM_response(llm_text)
            # interactions[i-1].ans = user_input
            # interactions[i-1].assessment = category
            # next_emotion = robot_emotion
            # print(next_emotion)
            # depression_score += int(category)
        
        if emotion_speak is None:
            emotion_speak = "dying1"

        speak(next_communication, mini=mini, emotion=emotion_speak)
        user_input = listen(mini=mini, use_whisper=USE_OLLAMA)  
        if not user_input:
            speak("Sorry I didn't catch that.", mini=mini)
            # TODO: maybe add retry logic here, for now just
            continue

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
# print(depression_score)