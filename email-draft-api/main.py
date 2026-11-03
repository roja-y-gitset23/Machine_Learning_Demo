import os
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from google import genai
from google.genai import types
from pydantic import BaseModel, ValidationError

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-3.5-flash-lite"  # change if your key uses another model

app = FastAPI(title="Email Draft Feature")

# ---------- Two sample conversations (session store) ----------
SESSIONS = {
    "session1": {
        "customer_name": "Rahul",
        "history": [
            {"role": "customer", "text": "Hi, my order #4521 (laptop stand) was supposed to arrive yesterday but it hasn't."},
            {"role": "agent", "text": "Sorry about that, Rahul. I checked and it is delayed at the courier hub."},
            {"role": "agent", "text": "It will be delivered by Friday. I will send you the tracking link today."},
            {"role": "customer", "text": "Okay, please make sure it arrives by Friday."},
        ],
    },
    "session2": {
        "customer_name": "Priya",
        "history": [
            {"role": "customer", "text": "The headphones I received are damaged. I want a refund."},
            {"role": "agent", "text": "I am sorry, Priya. Please share a photo of the damage."},
            {"role": "customer", "text": "Sent the photo to your support email."},
            {"role": "agent", "text": "Thanks. Refund will be approved within 2 days and credited in 5-7 business days."},
        ],
    },
        "session3": {
        "customer_name": "Arjun",
        "history": [
            {"role": "customer", "text": "I was charged twice for my subscription this month."},
            {"role": "agent", "text": "Sorry about that, Arjun. I can see two charges of Rs. 499 on 1st November."},
            {"role": "agent", "text": "I have raised a refund for the duplicate charge. It will reach your account in 3-5 business days."},
            {"role": "customer", "text": "Thanks, please confirm once it is done."},
            {"role": "agent", "text": "Will do. You will get a confirmation email from us."},
        ],
    },
    "session4": {
        "customer_name": "Meena",
        "history": [
            {"role": "customer", "text": "I want to change the delivery address for order #7810."},
            {"role": "agent", "text": "Sure, Meena. The order has not shipped yet, so this is possible."},
            {"role": "customer", "text": "New address is 12 Lake View Road, Chennai 600041."},
            {"role": "agent", "text": "Updated. The order will now ship tomorrow and arrive in 3 days."},
        ],
    },
    "session5": {
        "customer_name": "Karthik",
        "history": [
            {"role": "customer", "text": "My app keeps crashing when I try to upload a profile photo."},
            {"role": "agent", "text": "Sorry to hear that, Karthik. Which phone and app version are you using?"},
            {"role": "customer", "text": "Android 13, app version 4.2."},
            {"role": "agent", "text": "That is a known bug fixed in version 4.3. Please update the app from the Play Store."},
            {"role": "customer", "text": "Okay, I will update and check."},
        ],
    },
}

# ---------- Pydantic models ----------
class DraftRequest(BaseModel):
    session_id: str
    tone: Literal["formal", "friendly"] = "formal"


class EmailDraft(BaseModel):
    subject: str
    body: str


# ---------- Helpers ----------
def build_prompt(session: dict, tone: str) -> str:
    convo = "\n".join(f"{m['role'].upper()}: {m['text']}" for m in session["history"])
    name = session["customer_name"]
    return f"""You write DRAFT summary emails for a customer support team.
Read the conversation and write one email to the customer.

Rules:
- Tone: {tone}.
- Subject: short, e.g. "Summary of your order query".
- Body must start with "Dear {name}," and include: key points discussed,
  next steps, and a polite closing signed "Support Team".
- Respond ONLY with JSON: {{"subject": "...", "body": "..."}}

Conversation:
{convo}
"""


def generate_draft(prompt: str) -> EmailDraft:
    last_error = ""
    for attempt in range(1, 4):  # up to 3 attempts
        text = prompt if not last_error else (
            prompt + f"\nYour previous output was invalid: {last_error}\nFix it and return valid JSON."
        )
        response = client.models.generate_content(
            model=MODEL,
            contents=text,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=EmailDraft,
                temperature=0,
            ),
        )
        try:
            return EmailDraft.model_validate_json(response.text)
        except ValidationError as e:
            last_error = str(e)
    raise HTTPException(status_code=502, detail="Could not generate a valid draft after 3 attempts")


# ---------- Endpoint ----------
@app.post("/draft-email", response_model=EmailDraft)
def draft_email(req: DraftRequest):
    session = SESSIONS.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    # Only returns the draft. Nothing is ever sent.
    return generate_draft(build_prompt(session, req.tone))