# OMEN contributor guide

OMEN is an institutional career intelligence platform. Preserve the loop: market demand → student skills → learning → verification → placement → outcomes → institutional improvement.

## Rules
- Never commit secrets. Use `.env.example` as the contract.
- Market Employability Score is a market-derived readiness signal, never a hiring probability.
- Hard eligibility is deterministic and separate from semantic role matching.
- TPO recommendations are advisory; final shortlist decisions remain human-controlled.
- Student private data and resumes must be protected by backend authorization and Supabase RLS.
- Put business logic in backend services, not React components.
- Every status change should create history and, where appropriate, a notification.

## Local commands
- Backend: `cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload`
- Frontend: `cd frontend && npm install && npm run dev`
