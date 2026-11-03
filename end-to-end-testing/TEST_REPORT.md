# Test Report – End-to-End Testing

## 1. Summary
10 scenarios: 3 document, 2 unanswerable, 2 CRM, 2 order, 1 email draft.
Before fixes: 7/10 passed. After fixes: 10/10 passed.
Unit tests: 6/6 passed. Secrets check: clean.

## 2. Scenario results
### Before fixes
(paste e2e_before.md)
### After fixes
(paste e2e_after.md)

## 3. Failures found and fixed
| # | Scenario | Problem | Fix | After fix |
|---|----------|---------|-----|-----------|
| 4, 5 | Unanswerable | App gave a made-up answer instead of saying it does not know | Default reply changed to "I don't know based on the available information." | PASS |
| 6 | CRM | Customer "Rahul" not matched because the message is lowercased and the name was not | Compare the lowercase name with the lowercase message | PASS |

## 4. Unit tests (mocked)
test_tools.py covers the CRM tool and order tool (found, not found, service down/timeout)
using mocked requests. Result: 6 passed.

## 5. Secrets check
- check_secrets.py found no hardcoded keys, passwords or tokens
- Settings are read from .env using python-dotenv
- .env is in .gitignore and not tracked by git; only .env.example is committed

## 6. Notes
The "before" run uses a demo switch (POST /admin/mode) that reproduces the two original
bugs, so the failing behaviour can be shown next to the fixed behaviour.

## 7. Conclusion
All 10 scenarios pass after the fixes. Next steps: add tests for edge cases such as an empty message or an invalid tone.