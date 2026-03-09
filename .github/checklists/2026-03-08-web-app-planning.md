# Lunch Web App - Implementation Checklist

## Azure Resources
- [x] Bing Search resource (deprecated - using direct URL input instead)

## Backend (FastAPI)
- [x] Backend skeleton (main.py, config.py, models.py, sessions.py)
- [x] Auth router (POST /api/auth)
- [x] Scrape router (POST /api/scrape)
- [x] Sessions router (CRUD, orders, CSV download)
- [x] SSE events router (GET /api/sessions/{id}/events)

## Frontend (React + Fluent UI)
- [x] Scaffold (Vite + React + Fluent UI + React Router)
- [x] AuthGate component
- [x] AdminPanel + MenuReview components
- [x] PollPage + OrderList components
- [x] CSV download button

## Deployment
- [x] Dockerfile (multi-stage build)
- [x] Azure Container Registry (acrlunchorder.azurecr.io)
- [x] Azure Container App deployment
- [x] End-to-end test with real restaurant (tacobar.se - 33 items extracted)

## Live URL
https://lunch-web-app.happyrock-baafa260.swedencentral.azurecontainerapps.io/

## Verified Endpoints
- GET /api/health -> 200 OK
- POST /api/auth -> password gate works (401 on wrong, 200+cookie on correct)
- GET /api/auth/check -> cookie validation works
- POST /api/scrape -> agentic scraper pipeline works end-to-end
- POST /api/sessions -> creates UUID-based sessions
- POST /api/sessions/{id}/orders -> submits orders, notifies SSE subscribers
- GET /api/sessions/{id}/csv -> CSV with individual orders + combined totals
- GET /api/sessions/{id}/events -> SSE stream for live updates
- GET / -> serves React SPA (Fluent UI, Teams-style)
- GET /session/{id} -> SPA catch-all for poll pages
