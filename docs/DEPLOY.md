# Deploy SANGAM as a public website

## Option A — Quick public demo (this machine)

1. Run `deploy-local.bat` (builds UI into API, serves on port 8100)
2. Expose with a tunnel (localtunnel / Cloudflare / ngrok)
3. Share the HTTPS URL with judges

## Option B — Render.com (free Docker)

1. Push this repo to GitHub
2. Create a new Web Service on https://render.com → use `Dockerfile` / `render.yaml`
3. Open the Render URL (API + website together)

## Option C — Docker anywhere

```bash
docker build -t sangam .
docker run -p 8100:8100 sangam
```

Open http://localhost:8100

## Production notes

- Frontend is built with `VITE_API_URL=` (same-origin `/api`)
- FastAPI serves `backend/static` (the React build)
- SQLite is fine for SIH demo; use PostgreSQL for real multi-user load
- Demo auth credentials remain for judging — not production SSO
