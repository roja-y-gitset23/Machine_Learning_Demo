import re
import pathlib

PATTERNS = [r"sk-[A-Za-z0-9]{20,}", r"AIza[0-9A-Za-z_\-]{30,}",
            r"(api_key|secret|password|token)\s*=\s*[\"'][^\"']{8,}[\"']"]
SKIP = {"venv", ".git", "__pycache__", ".pytest_cache"}
found = 0

for p in pathlib.Path(".").rglob("*"):
    if p.is_file() and p.suffix in {".py", ".js", ".html", ".json", ".md"} \
            and not (set(p.parts) & SKIP) and p.name != "check_secrets.py":
        text = p.read_text(encoding="utf-8", errors="ignore")
        if any(re.search(pat, text, re.I) for pat in PATTERNS):
            print("POSSIBLE SECRET:", p)
            found += 1

gitignore = pathlib.Path(".gitignore")
if not gitignore.exists() or ".env" not in gitignore.read_text():
    print(".env is NOT in .gitignore")
    found += 1

print("OK: no hardcoded secrets found" if found == 0 else f"{found} problem(s) found")