# MemoryGrid frontend

## Run locally

Start the FastAPI backend from the repository root:

```text
python -m uvicorn app.main:app --reload
```

Then start the frontend:

```text
npm run dev
```

The Vite development server runs on port 3000 and proxies `/api` requests to
`http://localhost:8000` by default. To call a different backend directly, set
`VITE_API_URL` in a local `.env.local` file, for example:

```text
VITE_API_URL=http://localhost:8000
```

Direct cross-origin requests are enabled for the default local frontend origins.
For another frontend origin, set `CORS_ORIGINS` for the backend to a JSON array
of allowed origins, such as `["https://memorygrid.example"]`.
