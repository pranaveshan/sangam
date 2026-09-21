# SANGAM — Judge Demo Testing Checklist

## Quick start

1. Backend: `cd backend && .venv\Scripts\activate && uvicorn app.main:app --reload --port 8100`
2. Frontend: `cd frontend && npm run dev` (port 5180)
3. Open http://localhost:5180

## 3-minute judge path

- [ ] Homepage shows Speak / Show / Explore (not a huge form)
- [ ] Language switcher changes UI (try Telugu / Hindi)
- [ ] `/report` — speak or type a problem
- [ ] Follow-ups only if location/people missing
- [ ] “Here’s what we understood” with Listen / Correct / Confirm
- [ ] After confirm: related reports + collaborators (DEMO DATA labeled)
- [ ] Explore Problems public page works without login
- [ ] University login → accept challenge → project workspace
- [ ] Suggest project plan → labeled **AI SUGGESTION** → Approve
- [ ] Community feedback → theme analysis (not success-from-sentiment-alone)
- [ ] Admin dashboard insights cite live DB aggregates
- [ ] Offline: disconnect network → report queues with honest “Saved on this device” message

## Honesty checks

- [ ] No fake partner logos or live deployment claims
- [ ] Demo universities/partners show DEMO DATA
- [ ] AI failure shows save-and-process-later (not invented analysis)
- [ ] No API keys in frontend

## Sample report text

English: After heavy rain, waterlogging is damaging crops near our village school.

Telugu: వర్షం పడిన తర్వాత మా పొలంలో నీళ్లు నిలిచిపోతున్నాయి. పంట పాడవుతోంది.
