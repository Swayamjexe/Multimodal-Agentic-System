import os
from fastapi import UploadFile
from app.services.state_store import StateStore
from app.models.state import AgentState
from app.langgraph.graph_builder import app_graph   

async def save_upload_file(file: UploadFile) -> str:
    if not file or not file.filename:
        return None

    os.makedirs("./uploads", exist_ok=True)
    safe_name = file.filename.replace("/", "_").replace("\\", "_")
    path = f"./uploads/{safe_name}"

    with open(path, "wb") as f:
        f.write(await file.read())

    return path


async def run_agent(text: str = None, file: UploadFile = None, session_id: str = "default", clarification_answer: str = None):

    # Restore user's state
    state = StateStore.get(session_id)

    # Handle clarification response
    if clarification_answer:
        state.clarifications.append(clarification_answer)
        state.user_input = clarification_answer

        state.extracted = True
        state.extracted_text = state.extracted_text

        state.requires_clarification = False
        state.clarification_question = ""

        result = app_graph.invoke(state)
        state = AgentState(**result)

        StateStore.update(session_id, state)

        if state.requires_clarification:
            return {
                "requires_clarification": True,
                "clarification_question": state.clarification_question,
                "state": state.model_dump()
            }

        return {
            "requires_clarification": False,
            "final_result": state.final_result,
            "extracted_text": state.extracted_text
        }

    # New user input (text OR file)
    # 1) TEXT takes priority
    if text is not None and text.strip() != "":
        state = AgentState(user_input=text)

    # 2) Otherwise FILE
    elif file:
        path = await save_upload_file(file)
        state = AgentState(user_input=path)

    # 3) Neither provided → ERROR (prevent user_input=None)
    else:
        raise ValueError("No valid user input (text or file) provided.")


    # Run LangGraph
    result = app_graph.invoke(state)
    state = AgentState(**result)

    # Save updated state
    StateStore.update(session_id, state)

    # Clarification needed?
    if state.requires_clarification:
        return {
            "requires_clarification": True,
            "clarification_question": state.clarification_question,
            "state": state.model_dump()
        }

    # Final result (DONE)
    return {
        "requires_clarification": False,
        "final_result": state.final_result,
        "extracted_text": state.extracted_text
    }
