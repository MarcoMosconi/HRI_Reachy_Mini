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
from prompt_interactions import get_csv, get_prompt, Interaction, get_intro, get_close, read_LLM_response


# ============ LLM Configuration ============
USE_OLLAMA = False  # Set to True to use Ollama, False for Google Gemini
OLLAMA_MODEL = "llama3.2:1b"  # Change to your preferred Ollama model

# Initialize LLM client and create response function
if USE_OLLAMA:
    import ollama
    def get_llm_response(prompt):
        """Send prompt to Ollama and get response text"""
        response = ollama.generate(model=OLLAMA_MODEL, prompt=prompt, stream=False)
        return response['response']
else:
    client = genai.Client()
    chat = client.chats.create(model="gemini-2.5-flash")
    def get_llm_response(prompt):
        """Send prompt to Gemini and get response text"""
        return chat.send_message(prompt).text
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
emotion_speak = "welcoming1"
anxiety = 4
depression = 10
user_input = None
depression_score = 0

print("Connected to Reachy Mini! ")
    
# Wiggle antennas
print("Wiggling antennas...")
ReachyMini().goto_target(antennas=[0.5, -0.5], duration=0.2)
ReachyMini().goto_target(antennas=[-0.5, 0.5], duration=0.2)
ReachyMini().goto_target(antennas=[0, 0], duration=0.01)

with ReachyMini(media_backend="no_media") as mini:
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
            llm_text = get_llm_response(prompt)
            category, next_communication, robot_emotion = read_LLM_response(llm_text)
            interactions[i-1].ans = user_input
            interactions[i-1].assessment = category
            next_emotion = robot_emotion
            print(next_emotion)
            depression_score += int(category)

        speak(next_communication, mini=mini, emotion=emotion_speak)
        user_input = listen(mini=mini, use_whisper=USE_OLLAMA)  
        if not user_input:
            speak("Sorry I didn't catch that.", mini=mini)
            # TODO: maybe add retry logic here, for now just
            continue
             
print(depression_score)
