# Empathetic Human-Robot Interaction with Reachy Mini

A conversational human–robot interaction (HRI) system that combines **Reachy Mini, speech recognition, large language models (LLMs), and expressive robot movements** to conduct structured mental-health check-ins.

The project explores how an embodied robot can make questionnaire-based interactions more conversational by combining spoken dialogue with non-verbal expressions.

## Overview

The system enables Reachy Mini to interact with users through structured questionnaires covering anxiety, depression, and alcohol use. Instead of simply reading questions aloud, the robot uses an LLM to interpret user responses, generate contextual replies, and guide the conversation.

The interaction pipeline integrates speech processing, language-model-based response generation, questionnaire scoring, speech synthesis, and robot motion.

## Key Features

- **Speech-based interaction:** Captures spoken responses and converts them into text using Google Speech Recognition or a local Whisper model.
- **LLM-driven dialogue:** Uses Google Gemini by default, with an alternative Ollama integration, to interpret answers and generate context-aware responses.
- **Different conversational styles:** Supports empathetic and neutral dialogue styles to explore alternative approaches to human–robot interaction.
- **Expressive robot behaviour:** Coordinates spoken responses with Reachy Mini's recorded movements and emotional animations.
- **Structured questionnaire assessment:** Processes responses from the GAD-7, PHQ-9, and CAGE questionnaires and calculates corresponding scores.
- **Speech synthesis:** Converts generated responses into spoken audio using the configured text-to-speech backend.

## System Architecture

| Component | Responsibility |
|---|---|
| `interaction.py` | Main interaction loop, LLM integration, response processing, and questionnaire scoring |
| `dialogue.py` | Speech input, transcription, speech synthesis, and coordination with robot movements |
| `prompt_interactions.py` | Questionnaire logic, prompt construction, dialogue formatting, and LLM response parsing |
| `emotions.py` | Playback of recorded Reachy Mini movements and associated sounds |
| `question_tree.csv` | Questionnaire questions and alternative neutral or empathetic formulations |
| `pipeline_notes.md` | Documentation of the interaction pipeline |
| `commands.md` | Project commands and workflow notes |
| `requirements.txt` | Python dependencies |

## Interaction Pipeline

1. **Initiate the interaction:** Reachy Mini connects and performs an initial movement.
2. **Ask a question:** The system selects a question from the questionnaire and presents it verbally.
3. **Listen to the user:** Speech is captured through a microphone and transcribed into text.
4. **Interpret the response:** An LLM processes the answer, maps it to a questionnaire category, and generates a conversational reply.
5. **Coordinate speech and movement:** Reachy Mini speaks the generated response while performing a corresponding expressive movement.
6. **Complete the assessment:** The system progresses through the questionnaire and calculates summary scores.

## Technology Stack

- **Python** — Core application logic.
- **Reachy Mini SDK** — Robot control and movement.
- **Google Gemini** — Default LLM for dialogue generation and answer categorization.
- **Ollama** — Alternative local LLM backend.
- **SpeechRecognition** — Speech input and recognition.
- **Whisper** — Optional local speech transcription.
- **Text-to-speech tools** — Audio generation for spoken responses.
- **Pandas** — Loading questionnaire data from CSV files.

## Getting Started

### Prerequisites

- Python and the dependencies listed in `requirements.txt`.
- A configured Reachy Mini robot and its required software environment.
- A working microphone and audio output.
- A Google Gemini API key or a compatible local Ollama setup.
- The required speech-recognition and text-to-speech backends.

### Installation

Clone the repository:

```bash
git clone https://github.com/MarcoMosconi/HRI_Reachy_Mini.git
cd HRI_Reachy_Mini
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Configure the credentials and services required by the selected LLM and speech-processing backends. Store API keys in environment variables or a local environment file that is excluded from version control.

### Run the Interaction

Once the robot, audio devices, and required backends are configured, launch the application:

```bash
python interaction.py
```

## Research Motivation

This project explores the integration of conversational AI and embodied behaviour in human–robot interaction.

The main areas of interest include:

- Natural-language understanding and generation.
- Spoken interaction with a physical robot.
- Coordination between verbal responses and expressive movements.
- The use of empathetic and neutral conversational styles.
- LLM-based interpretation of structured questionnaire responses.

The system provides a platform for investigating how dialogue and non-verbal robot behaviour can be combined in structured interactions.

## Limitations

- LLM-generated classifications may be inaccurate or inconsistent.
- Speech recognition can be affected by background noise and unclear speech.
- Expressive movements are programmed behaviours and do not imply that the robot experiences the emotions it conveys.
- Questionnaire scores generated by the system are not a substitute for professional evaluation or clinical diagnosis.

**This project is an HRI prototype for experimentation and research, not a validated mental-health screening or diagnostic system.** It should not be used to make clinical decisions.
