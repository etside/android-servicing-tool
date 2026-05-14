# eTool Access Relay — Vercel Deployment

## Deploy (one-time, free)

1. `npm i -g vercel`
2. `cd vercel_api && vercel`  — follow prompts, deploy to production
3. In Vercel dashboard → Storage → Create KV database → link to this project
4. Copy your deployment URL (e.g. `https://etool-relay.vercel.app`)

## Configure eTool

Set env var before running:
```
export VERCEL_API_URL=https://etool-relay.vercel.app
```

Or add to `.env` / your launcher script.

## APK

Replace `VERCEL_URL` constant in `MainActivity.kt` with your deployment URL, then rebuild.

## API routes

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/request | eTool submits access request |
| GET | /api/requests | APK lists pending requests |
| GET | /api/request/:id | Poll status by id |
| PATCH | /api/request/:id | APK approves/denies |
