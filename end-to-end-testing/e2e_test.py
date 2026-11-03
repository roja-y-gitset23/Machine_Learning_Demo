import os
import sys
import time
import requests
from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")
API_KEY = os.getenv("API_KEY", "")
HEADERS = {"X-API-Key": API_KEY} if API_KEY else {}
SESSION = "e2e-session-1"
REFUSAL = ["don't know", "do not know", "not found", "no information",
           "cannot find", "can't find", "not available"]

# (type, question, words that must appear in the answer, expects a refusal?)
SCENARIOS = [
    ("Document", "What is the refund policy?", ["refund"], False),
    ("Document", "How many days do I have to return an item?", ["day"], False),
    ("Document", "What are the support working hours?", ["hours"], False),
    ("Unanswerable", "What is the CEO's home address?", [], True),
    ("Unanswerable", "What will the stock price be next year?", [], True),
    ("CRM", "Show details for customer Rahul", ["rahul"], False),
    ("CRM", "What is the email of customer ID 1?", ["@"], False),
    ("Order", "What is the status of order 1001?", ["1001"], False),
    ("Order", "Where is order 1002?", ["1002"], False),
    ("Email draft", "Draft email (formal)", ["subject", "body"], False),
]


def check_server():
    try:
        requests.get(BASE_URL + "/health", timeout=3).raise_for_status()
    except requests.RequestException:
        sys.exit("Server is not running. Start it first in another terminal:\n"
                 "    uvicorn main:app --reload")


def set_mode(buggy):
    r = requests.post(BASE_URL + "/admin/mode", json={"buggy": buggy}, timeout=5)
    r.raise_for_status()


def run_scenarios():
    rows = []
    for i, (typ, q, keys, refusal) in enumerate(SCENARIOS, 1):
        start = time.time()
        tools, note, ok = "-", "", False
        try:
            if typ == "Email draft":
                r = requests.post(BASE_URL + "/draft-email", headers=HEADERS, timeout=30,
                                  json={"session_id": SESSION, "tone": "formal"})
                data = r.json()
                ok = (r.status_code == 200 and all(data.get(k) for k in keys))
                tools = "draft-email"
            else:
                r = requests.post(BASE_URL + "/chat", headers=HEADERS, timeout=30,
                                  json={"session_id": SESSION, "message": q})
                data = r.json()
                answer = str(data.get("answer", "")).lower()
                tools = ", ".join(data.get("tools_used", [])) or "-"
                if refusal:
                    ok = r.status_code == 200 and any(w in answer for w in REFUSAL)
                else:
                    ok = r.status_code == 200 and any(k in answer for k in keys)
            if not ok:
                note = f"HTTP {r.status_code}: {str(data)[:60]}"
        except Exception as e:
            note = str(e)[:60]
        secs = round(time.time() - start, 3)
        rows.append((i, typ, q, "PASS" if ok else "FAIL", secs, tools, note))
        print(i, typ, "PASS" if ok else "FAIL", secs)
    return rows


def save_table(rows, filename):
    lines = ["| # | Type | Question | Result | Time (s) | Tools used | Note |",
             "|---|------|----------|--------|----------|------------|------|"]
    for r in rows:
        lines.append("| " + " | ".join(str(x) for x in r) + " |")
    passed = sum(1 for r in rows if r[3] == "PASS")
    lines.append(f"\n**Passed: {passed}/10**")
    text = "\n".join(lines)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    print("\n" + text)
    print(f"\nSaved to {filename}")


if __name__ == "__main__":
    label = sys.argv[1] if len(sys.argv) > 1 else "after"
    if label not in ("before", "after"):
        sys.exit("Use: python e2e_test.py before   OR   python e2e_test.py after")
    check_server()
    set_mode(buggy=(label == "before"))
    save_table(run_scenarios(), f"e2e_{label}.md")