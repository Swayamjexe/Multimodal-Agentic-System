import fitz
import easyocr
from faster_whisper import WhisperModel
import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from app.utils.extract_yt_id import extract_youtube_id

# OCR model
ocr_reader = easyocr.Reader(["en"], gpu=False)
#Audio Transcribe Model
whisper_model = WhisperModel("small", device="cpu", compute_type="int8")

def pdf_extractor(path: str) -> str:
    doc = fitz.open(path)
    text = ""
    for page in doc:
        page_text = page.get_text("text")
        if page_text.strip():
            text += page_text + "\n"
    return text.strip() if text.strip() else "[ERROR] No selectable text found"

def ocr_extractor(path: str) -> str:
    result = ocr_reader.readtext(path, detail=1)
    return " ".join([r[1] for r in result]) if result else "[ERROR] OCR found no text"

def audio_transcribe(path: str) -> str:
    segments, _ = whisper_model.transcribe(path)
    return " ".join([s.text for s in segments]).strip() or "[ERROR] No speech detected"

def youtube_transcript_extractor(url: str) -> str:
    video_id = extract_youtube_id(url)
    if not video_id:
        return "[ERROR] Invalid YouTube URL"
    transcript = YouTubeTranscriptApi().fetch(video_id)
    return TextFormatter().format_transcript(transcript)
