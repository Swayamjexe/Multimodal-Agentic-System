from langgraph.graph import StateGraph, END
from groq import Groq
from app.utils.groq_client import client
from app.models.state import AgentState
from app.utils.detect_type import detect_input_type
from app.langgraph.tools import (
    pdf_extractor,
    ocr_extractor,
    audio_transcribe,
    youtube_transcript_extractor
)
from app.utils.groq_llm import groq_llm
import json

# 1. Content Extractor Node
def content_extractor(state: AgentState):
    if state.extracted:
        return state
    input_type = detect_input_type(state.user_input)

    if input_type == "pdf":
        state.extracted_text = pdf_extractor(state.user_input)
    elif input_type == "image":
        state.extracted_text = ocr_extractor(state.user_input)
    elif input_type == "audio":
        state.extracted_text = audio_transcribe(state.user_input)
    elif input_type == "youtube":
        state.extracted_text = youtube_transcript_extractor(state.user_input)
    else:
        state.extracted_text = state.user_input  # plain text
    state.extracted = True
    return state


# 2. Intent Classifier Node
def intent_classifier(state: AgentState):
    prompt = f"""
You are an intent classification engine.

Your job is to look at:
1. The raw user input
2. The extracted text content

Then infer what the user wants.

Important: If the user is answering a clarification question or a follow-up question, IGNORE the extracted text.
Decide intent ONLY from the user_input.

If the user reply is short (less than 10 words), treat it as a clarification and ignore extracted text.

Note: If the text contains some kind of code classify it as code_explain intent, ignore improper syntax or formatting.

----------------------------------------
INTENT RULES
----------------------------------------

You must classify into EXACTLY one of these:
- summarization
- sentiment_analysis
- code_explain
- general_qa
- unknown

----------------------------------------
WHEN TO RETURN 'unknown'
----------------------------------------

Return intent = "unknown" and confidence = 0.00 if ANY of these are true:

1. The user input is a plain URL (e.g., YouTube link, website, file link)
2. The user input is only a file path and extracted text content does not contain a clear intent  
3. The user input is ONLY content with no clear instruction
4. The user input does NOT contain a question and does NOT clearly match another intent
5. You are not at least 70% certain of the user's intent
6. The extracted text is present but the user never asked what to do with it
7. If the user uploaded a file (PDF, image, audio, YouTube URL, or local path)
   AND the user did NOT ask any question
   AND did NOT request any task (summarization, sentiment, explanation):
   → classify as "unknown" with confidence = 0.0

----------------------------------------
GENERAL_QA RULES
----------------------------------------

Only classify as "general_qa" if:
- the user input contains a real question, even if provided text does not specify
  OR
- the user clearly asks something about the extracted text

A question MUST contain:
- a question mark (?) OR
- a question keyword: what, why, how, when, where, who, which

You MUST NOT classify as "general_qa" unless the user clearly asks a question.
Even if extracted_text is long, do NOT assume the user wants Q&A.

If neither is present → return unknown.

----------------------------------------
CONFIDENCE RULES
----------------------------------------

- Only give confidence > 0.65 if you are truly sure.
- If unsure → intent = "unknown", confidence = 0.0.

----------------------------------------
RETURN FORMAT (STRICT JSON ONLY):

{{
  "intent": "...",
  "confidence": 0.00
}}

----------------------------------------
USER INPUT:
{state.user_input}

EXTRACTED TEXT:
{state.extracted_text}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": prompt}],
        temperature=0.0,
    )

    out = response.choices[0].message.content

    try:
        data = json.loads(out)
    except:
        json_str = out[out.find("{"): out.rfind("}") + 1]
        data = json.loads(json_str)

    state.intent = data["intent"]
    state.intent_confidence = data["confidence"]

    return state


# 3. Follow-Up Node
def followup_agent(state: AgentState):
    state.requires_clarification = True
    state.clarification_question = (
        "What exactly do you want me to do?"
    )
    return state


# 4. Task Executor Node
def task_executor(state: AgentState):
    text = state.extracted_text.strip()
    intent = state.intent

    #Summarization
    if intent == "summarization":
        prompt = f"""
        Summarize the following text clearly and concisely.
        Focus on key ideas, remove filler, keep context.

        TEXT:
        {text}
        """
        state.final_result = groq_llm(prompt)
        return state

    #Sentiment Analysis
    if intent == "sentiment_analysis":
        prompt = f"""
        Perform sentiment analysis on the following text.

        Return JSON with:
        - sentiment: positive/negative/neutral/mixed
        - explanation: why you classified it this way

        TEXT:
        {text}
        """
        raw = groq_llm(prompt)
        state.final_result = raw
        return state

    #Code Explanation/Debugging
    if intent == "code_explain":
        prompt = f"""
        You are a senior software engineer.

        Analyze and explain the following code:
        - Step-by-step explanation
        - What the code does
        - Possible bugs or edge cases
        - Time/space complexity (if relevant)
        - Suggest improvements

        CODE:
        {text}
        """
        state.final_result = groq_llm(prompt)
        return state

    #General Question and Answering
    if intent == "general_qa":
        prompt = f"""
        Answer the user's question ONLY using the provided text if provided text is different else fallback to give generalized answer. Just give the Answer no pretext about provided text if not found.

        CONTEXT:
        {text}

        QUESTION:
        {state.user_input}
        """
        state.final_result = groq_llm(prompt)
        return state

    #If Unknown
    state.final_result = "⚠️ I couldn't determine what task to run."
    return state
