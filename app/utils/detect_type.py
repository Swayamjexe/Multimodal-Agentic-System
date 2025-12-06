def detect_input_type(user_input: str):
    if user_input.lower().endswith(".pdf"):
        return "pdf"
    if "youtube.com" in user_input or "youtu.be" in user_input:
        return "youtube"
    if user_input.lower().endswith((".png", ".jpg", ".jpeg")):
        return "image"
    if user_input.lower().endswith(".mp3"):
        return "audio"
    return "text"
