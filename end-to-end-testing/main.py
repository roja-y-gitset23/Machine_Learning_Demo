import re
from typing import Dict, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import crm_tool
import order_tool

app = FastAPI(title="E2E Testing App")

# ---------- demo switch ----------
# buggy=True  -> reproduces the 2 original bugs (used for "python e2e_test.py before")
# buggy=False -> fixed behaviour (used for "python e2e_test.py after")
STATE = {"buggy": False}

# ---------- built-in data ----------
DOCS = {
    "policy": "Refund policy: items can be returned within 30 days of delivery for a full refund.",
    "hours": "Support working hours are 9 am to 6 pm, Monday to Friday.",
}
CUSTOMERS = {
    1: {"id": 1, "name": "Rahul", "email": "rahul@example.com", "city": "Chennai"},
    2: {"id": 2, "name": "Priya", "email": "priya@example.com", "city": "Mumbai"},
}
ORDERS = {
    1001: {"order_id": 1001, "status": "Shipped", "eta": "2 days"},
    1002: {"order_id": 1002, "status": "Processing", "eta": "5 days"},
}
SESSIONS: Dict[str, List[dict]] = {}
IDK = "I don't know based on the available information."
BUGGY_FALLBACK = "Sure! Our team will handle that for you."  # BUG 1: invents an answer


@app.get("/health")
def health():
    return {"status": "ok", "buggy": STATE["buggy"]}


class ModeRequest(BaseModel):
    buggy: bool


@app.post("/admin/mode")
def set_mode(req: ModeRequest):
    """Demo only: switch the original bugs on or off and clear old sessions."""
    STATE["buggy"] = req.buggy
    SESSIONS.clear()
    return {"buggy": STATE["buggy"]}


# ---------- mock CRM / order services (the tools call these) ----------
@app.get("/crm/customers/{key}")
def crm_customer(key: str):
    if key.isdigit() and int(key) in CUSTOMERS:
        return CUSTOMERS[int(key)]
    for c in CUSTOMERS.values():
        if c["name"].lower() == key.lower():
            return c
    raise HTTPException(404, "Customer not found")


@app.get("/orders/{order_id}")
def orders(order_id: int):
    if order_id in ORDERS:
        return ORDERS[order_id]
    raise HTTPException(404, "Order not found")


# ---------- chat ----------
class ChatRequest(BaseModel):
    session_id: str = "default"
    message: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[str] = []
    tools_used: List[str] = []


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    msg = req.message.lower()
    # BUG 1 (when buggy): unanswerable questions get a made-up answer
    answer = BUGGY_FALLBACK if STATE["buggy"] else IDK
    sources, tools = [], []

    if "order" in msg:
        tools.append("order_tool")
        m = re.search(r"\b(\d{4})\b", msg)
        if m:
            res = order_tool.get_order_status(m.group(1))
            if "error" in res:
                answer = f"Sorry, {res['error'].lower()} for order {m.group(1)}."
            else:
                answer = (f"Order {res['order_id']} is {res['status']}. "
                          f"Estimated delivery: {res['eta']}.")
        else:
            answer = "Please give me a 4-digit order number."

    elif "customer" in msg:
        tools.append("crm_tool")
        key = None
        m = re.search(r"\b(\d+)\b", msg)
        if m:
            key = m.group(1)
        else:
            for c in CUSTOMERS.values():
                # BUG 2 (when buggy): msg is lowercase but the name is not
                if STATE["buggy"]:
                    name_matches = c["name"] in msg
                else:
                    name_matches = c["name"].lower() in msg
                if name_matches:
                    key = c["name"]
        if key:
            res = crm_tool.get_customer(key)
            if "error" in res:
                answer = f"Sorry, {res['error'].lower()}."
            else:
                answer = (f"Customer {res['name']} (ID {res['id']}), "
                          f"email {res['email']}, city {res['city']}.")
        else:
            answer = "Please give me a customer name or ID."

    elif any(w in msg for w in ["refund", "return"]):
        tools.append("search_documents")
        sources.append("policy.txt")
        answer = DOCS["policy"]

    elif any(w in msg for w in ["support", "hours", "working"]):
        tools.append("search_documents")
        sources.append("policy.txt")
        answer = DOCS["hours"]

    SESSIONS.setdefault(req.session_id, []).append(
        {"user": req.message, "assistant": answer})
    return ChatResponse(answer=answer, sources=sources, tools_used=tools)


# ---------- email draft (only returns a draft, never sends) ----------
class DraftRequest(BaseModel):
    session_id: str
    tone: str = "formal"


class DraftEmail(BaseModel):
    subject: str
    body: str


@app.post("/draft-email", response_model=DraftEmail)
def draft_email(req: DraftRequest):
    history = SESSIONS.get(req.session_id)
    if not history:
        raise HTTPException(404, "No conversation found for this session")
    if req.tone not in ("formal", "friendly"):
        raise HTTPException(400, "tone must be 'formal' or 'friendly'")
    name = "Customer"
    for turn in history:
        for c in CUSTOMERS.values():
            if c["name"].lower() in turn["user"].lower():
                name = c["name"]
    points = "\n".join(f"- {t['assistant']}" for t in history[-3:])
    greet = f"Dear {name}," if req.tone == "formal" else f"Hi {name},"
    close = ("Kind regards,\nSupport Team" if req.tone == "formal"
             else "Cheers,\nSupport Team")
    body = (f"{greet}\n\nThank you for contacting us. Here is a summary of our chat:\n"
            f"{points}\n\nNext steps: please reply if you need anything else.\n\n{close}")
    return DraftEmail(subject="Summary of your query", body=body)