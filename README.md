# Multimodal-Agentic-System

## Overview
This project is a multi-modal, multi-agent enabled chatbot. It features Agent nodes like Content Extractor, Intent Classifier, Follow-up, Task Executor, which all together provides user with personalized answers on their input which can be 
a PDF, IMG(.png, .jpg, .jpeg), Audio(.mp3, .wav), Plain Text, Youtube Video URL and can perform tasks like Text extraction, Summarization, Code Explanation, Sentiment Analysis and General Question-Answering.

## Architecture
The System uses Langgraph to build the Agentic System graph.


<img width="265" height="622" alt="image" src="https://github.com/user-attachments/assets/83dea534-e6c0-4544-b023-a5c944be4626" />

[Fig. Compiled Graph Architecture]

### Nodes Description
- **Content Extractor Node:** Detects the type of user input (PDF, image, audio, YouTube, or text) and extracts readable content for further processing.  
- **Intent Classifier Node:** Analyzes the user input and extracted content to determine the user’s intent, assigning a confidence score.  
- **Follow-Up Node:** Handles cases where the user’s request is unclear, prompting them for clarification to guide the next steps.  
- **Task Executor Node:** Performs the appropriate action based on the detected intent, such as summarization, sentiment analysis, code explanation, or answering questions.

### Tools used by the System
- **PyMuPDF (`fitz`)**: Used to extract text from PDF files efficiently, page by page.  
- **EasyOCR (`easyocr`)**: Optical Character Recognition library for extracting text from images.  
- **Faster Whisper (`faster_whisper`)**: Lightweight audio transcription model for converting speech in audio files to text.  
- **Regular Expressions (`re`)**: Utilized for text parsing and processing, such as extracting patterns from strings.  
- **YouTube Transcript API (`youtube_transcript_api`)**: Fetches and formats transcripts from YouTube videos.  

## How It Works

1. **User Input:**  
   The user provides input in any supported format: PDF, image, audio, plain text, or YouTube URL.

2. **Content Extraction:**  
   The system extracts readable text from the input:
   - PDFs → `pdf_extractor`
   - Images → `ocr_extractor`
   - Audio → `audio_transcribe`
   - YouTube videos → `youtube_transcript_extractor`
   - Plain text → used directly

3. **Intent Detection:**  
   The system analyzes the user input and the extracted content to identify the user's task or intent (e.g., summarization, sentiment analysis, code explanation, or question answering).  
   - If the system is **highly confident (≥ 0.65)** about the intent, it proceeds to execute the task.  
   - If the confidence is **low (< 0.65)** or the intent is unclear, it routes the input to the **Follow-Up Node**.

4. **Follow-Up Clarification:**  
   The system asks the user a clarification question, such as:  
   > "What exactly do you want me to do?"  
   Once the user responds, the system re-evaluates the task and proceeds.

5. **Task Execution:**  
   Based on the confirmed intent, the system executes the appropriate action:
   - **Summarization** → produces a concise summary of the text.  
   - **Sentiment Analysis** → analyzes and explains the sentiment of the text.  
   - **Code Explanation** → provides detailed explanation, potential bugs, and improvements for the code.  
   - **General Q&A** → answers questions using the provided context or general knowledge.

6. **Result Display:**  
   The final result of the executed task is presented to the user. If the system cannot determine the task, it returns a warning message:
   > "⚠️ I couldn't determine what task to run."

## Screenshots

<img width="1919" height="1079" alt="Screenshot 2025-12-06 123150" src="https://github.com/user-attachments/assets/d7887be2-0947-4305-9145-9337036d8b5d" />

## Setup and Usage

1. **Clone the repository**  
   ```
   git clone https://github.com/Swayamjexe/Multimodal-Agentic-System
   cd <repository-folder>
   ```

2. **Create Virtual Environment**
   ```
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```
   
3. **Install required libraries**
   ```
   pip install -r requirements.txt
   ```
4. **Run the backend server**
   ```
   uvicorn main:app --reload
   ```
   Backend available at: http://127.0.0.1:8000/
   
6. **Run the frontend interface**
   ```
   python gradio_ui.py
   ```
   Frontend available at: http://127.0.0.1:7860/
   
8. **Testing with sample files**
   
   Use the files in the uploads/ folder (sample PDFs, images, and audio) to test the system.
