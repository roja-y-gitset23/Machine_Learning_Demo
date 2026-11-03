import os
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Chat API")

# CORS: only the origins you list. Never use ["*"] in production.
# In production set ALLOWED_ORIGINS="https://your-site.com"
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

DOCS: dict[str, str] = {}  # filename -> text


class ChatRequest(BaseModel):
    message: str


class DraftRequest(BaseModel):
    question: str
    answer: str
    sources: List[str] = []


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/documents")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "No file provided")
    content = (await file.read()).decode("utf-8", errors="ignore")
    DOCS[file.filename] = content
    return {"filename": file.filename, "characters": len(content), "status": "uploaded"}


@app.post("/chat")
def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(400, "Message cannot be empty")
    words = {w.lower() for w in req.message.split() if len(w) > 3}
    sources = [name for name, text in DOCS.items()
               if any(w in text.lower() for w in words)]
    if sources:
        answer = f"I found relevant information in {len(sources)} document(s) about: {req.message}"
    else:
        answer = f"I could not find this in the uploaded documents. You asked: {req.message}"
    return {"answer": answer, "sources": sources}


@app.post("/draft-email")
def draft_email(req: DraftRequest):
    src = ", ".join(req.sources) if req.sources else "our records"
    draft = (
        "Subject: Follow-up on your question\n\n"
        "Hello,\n\n"
        f"Thank you for your question: \"{req.question}\"\n\n"
        f"{req.answer}\n\n"
        f"Source(s): {src}\n\n"
        "Please let me know if you need anything else.\n\n"
        "Best regards,\nSupport Team"
    )
    return {"draft": draft}