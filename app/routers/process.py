from fastapi import APIRouter, UploadFile, File, Form
from app.services.agent_runner import run_agent

router = APIRouter(prefix="/agent", tags=["Agent"])

@router.post("/chat")
async def chat_endpoint(
    session_id: str = Form("default"),
    text: str = Form(None),
    clarification_answer: str = Form(None),
    file: UploadFile = File(None),
):
    return await run_agent(
        text=text,
        file=file,
        session_id=session_id,
        clarification_answer=clarification_answer
    )
