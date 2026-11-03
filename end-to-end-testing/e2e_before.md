| # | Type | Question | Result | Time (s) | Tools used | Note |
|---|------|----------|--------|----------|------------|------|
| 1 | Document | What is the refund policy? | PASS | 0.032 | search_documents |  |
| 2 | Document | How many days do I have to return an item? | PASS | 0.03 | search_documents |  |
| 3 | Document | What are the support working hours? | PASS | 0.005 | search_documents |  |
| 4 | Unanswerable | What is the CEO's home address? | FAIL | 0.007 | - | HTTP 200: {'answer': 'Sure! Our team will handle that for you.', 'sour |
| 5 | Unanswerable | What will the stock price be next year? | FAIL | 0.017 | - | HTTP 200: {'answer': 'Sure! Our team will handle that for you.', 'sour |
| 6 | CRM | Show details for customer Rahul | FAIL | 0.004 | crm_tool | HTTP 200: {'answer': 'Please give me a customer name or ID.', 'sources |
| 7 | CRM | What is the email of customer ID 1? | PASS | 0.046 | crm_tool |  |
| 8 | Order | What is the status of order 1001? | PASS | 0.028 | order_tool |  |
| 9 | Order | Where is order 1002? | PASS | 0.006 | order_tool |  |
| 10 | Email draft | Draft email (formal) | PASS | 0.005 | draft-email |  |

**Passed: 7/10**