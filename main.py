from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.process import router as process_router

app = FastAPI(title="Multimodal-Agentic-System")

# CORS (for your future frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(process_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Agentic System API is running."}
