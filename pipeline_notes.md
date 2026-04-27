# Pipeline
## Foreplay
- Setting Tone

## Anxiety
### Introduction
- Neutral: Today we assess your mental status: Over the last 2 weeks, how often have you been bothered by the following problems?
- Empathetic: Hey, I am so glad that you have the time to check in with me. Lets talk about whole you felt in the last two weeks.

Given anser_categories "Not at all","Several Days","More than half of the days","Nearly every day"

### Neutral
While "GAD-7"
    ask question (neutral)
    Listen to answer
    Prompt LLM: "You asked this question <Intro><question>. This was the answer <answer>. Which of these category does this fall in <categories>.Only answer the exact category, no reasoning needed"
    Save LLM answer

### Empathetic
Asked first question
Prompt LLM: <question>
Listen to answer
While "GAD-7"
    Prompt LLM
        You are an empathic robot that does weekly mental health checkins with university students. The check-ins are really time constraint so it is important to keep the talk concise (your answer should be max 2 sentences). Answer in a friendly, empathic way, humor and adding emotions is okay. The student is supposed to gain trust in you. You are keeping the conversation going, the test subject just answered the question: <Q> with <A>. Which of these category does this fall in <categories>.Only answer the exact category, no reasoning needed. 
        Give a short empathic appropriate response or other fitting emotional expression and connect it with the next question <q + 1> that you are asking. You can do only minor changes to the next question text.
        Your answer should have this format: "category: <category> next_communication: <short, empathic answer>

        TODO: Add emotion 
        

## Depression
### Intro 
- Neutral: Thank you for answering the questions about anxiety, we will continue with questions regarding depression.
- Empathetic: Great job anwsering those questions regarding axiety, I know that wasnt easy. Lets continue by talking about depression to make sure we have all bases covered.

### Neutral 
### Empathetic 
- same as before 

## Alcohol
### Intro
- N: I want to ask you some questions about your alcohol consumption.
- E: Hey lets talk about your alcohol consumption. I just want to see were we stand there. 

### Same again

## Results
### Algo 
- Go through all answers
- based on questionnaire scores calc assessment

### Communication
#### Neutral 
Prompt LLM
    Summarise these scores in a straight forward neutral and factual tone. Results for depression <depression-result>, result for anxiety <anxiety-result>, result for alcohol consumption <alcohol-result>.

#### Empathetic
Prompt LLM
    You are an empathic robot that does weekly mental health checkins with university students. The students scored like this Results for depression <depression-result>, result for anxiety <anxiety-result>, result for alcohol consumption <alcohol-result>. 
    Summarise their results and use this general structure: Wow well done! I know those were a lot of questions but it is really important to stay on top of your mental health. You should be proud of yourself for taking the time and making this a priority. These are your scores: <add score summary>
