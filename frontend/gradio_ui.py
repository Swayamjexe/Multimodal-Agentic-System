import gradio as gr
import requests
import uuid
import json

API_URL = "http://127.0.0.1:8000/api/agent/chat"

# Create a random session_id
SESSION_ID = str(uuid.uuid4())


def log_request_debug(data, files):
    print("\n================= GRADIO → BACKEND DEBUG LOG =================")
    print("DATA FIELDS SENT:")
    print(json.dumps(data, indent=2))

    if files is None:
        print("FILES: None")
    else:
        print("FILES SENT:")
        for k, v in files.items():
            if v is None:
                print(f"  {k}: None")
            else:
                filename, content, mime = v
                print(f"  {k}: filename={filename!r}, size={len(content)} bytes, mime={mime}")
    print("==============================================================\n")


def send_to_backend(message, file_obj, chat_history, is_clarification):
    """
    Sends the message or file to the backend.
    `is_clarification` tells us if the current input is a clarification answer.
    """

    # Clarification mode
    if is_clarification:
        data = {
            "session_id": SESSION_ID,
            "text": "",
            "clarification_answer": message,
        }
        log_request_debug(data, None)
        resp = requests.post(API_URL, data=data)

        try:
            response = resp.json()
        except:
            chat_history.append({
                "role": "assistant",
                "content": f"❌ Backend Error:\n{resp.text}"
            })
            return chat_history, True 

        if response.get("requires_clarification"):
            chat_history.append({
                "role": "assistant",
                "content": response["clarification_question"]
            })
            return chat_history, True 

        # Final output after clarification
        chat_history.append({
            "role": "assistant",
            "content": f"📄 Extracted Text:\n{response.get('extracted_text','')}"
        })
        chat_history.append({
            "role": "assistant",
            "content": f"✅ Final Result:\n{response.get('final_result','')}"
        })
        return chat_history, False #Reset

    # Normal user message
    if message:
        chat_history.append({"role": "user", "content": message})

    # Safety: text + file not allowed
    if message and file_obj:
        chat_history.append({
            "role": "assistant",
            "content": "❌ Please send either text OR a file, not both."
        })
        return chat_history, False

    # Prepare data for backend
    if message:
        data = {"session_id": SESSION_ID, "text": message, "clarification_answer": ""}
        log_request_debug(data, None)
        files = {"file": ("", b"", "application/octet-stream")}
        resp = requests.post(API_URL, data=data, files=files)

    elif file_obj:
        if not file_obj.name:
            chat_history.append({"role": "assistant", "content": "❌ Invalid file upload."})
            return chat_history, False
        
        data = {"session_id": SESSION_ID, "text": "", "clarification_answer": ""}
        try:
            with open(file_obj.name, "rb") as f:
                content = f.read()
        except Exception as e:
            chat_history.append({"role": "assistant", "content": f"❌ Failed to read file: {e}"})
            return chat_history
        files = {
            "file": (file_obj.name.split("\\")[-1], content, getattr(file_obj, "mime_type", "application/octet-stream"))
        }
        log_request_debug(data, files)
        resp = requests.post(API_URL, data=data, files=files)

    else:
        chat_history.append({"role": "assistant", "content": "❌ Please enter text or upload a file."})
        return chat_history, False

    # Handle backend response
    try:
        response = resp.json()
    except:
        chat_history.append({"role": "assistant",
                             "content": f"❌ Backend Error:\n{resp.text}"})
        return chat_history, False

    # Clarification requested by backend
    if response.get("requires_clarification"):
        chat_history.append({
            "role": "assistant",
            "content": response["clarification_question"]
        })
        return chat_history, True  # Activate clarification mode

    # Final result
    chat_history.append({
        "role": "assistant",
        "content": f"📄 Extracted Text:\n{response.get('extracted_text','')}"
    })
    chat_history.append({
        "role": "assistant",
        "content": f"✅ Final Result:\n{response.get('final_result','')}"
    })

    return chat_history, False


# GRADIO UI LAYOUT
with gr.Blocks() as demo:
    gr.HTML("<style>footer {visibility: hidden}</style>")
    gr.Markdown("## 🤖 LangGraph Chatbot UI\nMinimal interface — Text or File, not both.")

    chatbot = gr.Chatbot(height=500)
    clarification_state = gr.State(False)

    with gr.Row():
        message = gr.Textbox(
            label="Enter text...",
            placeholder="Write something here OR upload a file",
        )
        file_input = gr.File(
            label="Upload PDF / Image / Audio",
            file_types=[".pdf", ".png", ".jpg", ".jpeg", ".mp3"],
        )
        send_btn = gr.Button("Send")

    # Wrapper to update clarification state
    def handle_send(message, file_obj, chat_history, is_clarification):
        chat_history, new_clarification_state = send_to_backend(
            message, file_obj, chat_history, is_clarification
        )
        return chat_history, new_clarification_state

    send_btn.click(
        handle_send,
        inputs=[message, file_input, chatbot, clarification_state],
        outputs=[chatbot, clarification_state],
    )


demo.launch()