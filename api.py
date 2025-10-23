from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import pandas as pd
from core import load_data, search, DATA_DIR

# -----------------------------------------------------------
# FastAPI app setup
# -----------------------------------------------------------
app = FastAPI(title="Kiez Connect API")

# Enable CORS so React frontend can access this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://your-react-domain.com",  # Replace with your actual frontend domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------
# Global data load
# -----------------------------------------------------------
DATAFRAME: pd.DataFrame | None = None

@app.on_event("startup")
def _startup():
    """Load data once when the app starts."""
    global DATAFRAME
    DATAFRAME = load_data(DATA_DIR)

# -----------------------------------------------------------
# Root route (for friendly message)
# -----------------------------------------------------------
@app.get("/")
def root():
    """Base URL friendly message."""
    return {
        "message": "✅ Kiez Connect API is running successfully!",
        "available_endpoints": {
            "health": "/api/health",
            "docs": "/docs",
            "search": {
                "method": "POST",
                "path": "/api/search",
                "body_example": {"query": "jobs in Mitte", "limit": 10},
            },
        },
        "developer_note": "Visit /docs for interactive API documentation.",
    }

# -----------------------------------------------------------
# Health check route
# -----------------------------------------------------------
@app.get("/api/health")
def health():
    """Simple health check."""
    return {"status": "ok"}

# -----------------------------------------------------------
# Search endpoint
# -----------------------------------------------------------
class SearchIn(BaseModel):
    query: str
    limit: int | None = 50

@app.post("/api/search")
def api_search(body: SearchIn):
    """Search jobs/events/courses based on text query."""
    if DATAFRAME is None or DATAFRAME.empty:
        raise HTTPException(status_code=500, detail="Data not loaded")

    results = search(DATAFRAME, body.query)
    if body.limit:
        results = results.head(body.limit)

    # Choose the main columns to send to frontend
    cols = [
        c
        for c in [
            "type",
            "title",
            "course_name",
            "provider",
            "company",
            "district",
            "location",
            "address",
            "latitude",
            "longitude",
            "job_url_direct",
            "job_url",
            "link",
            "url",
            "website",
        ]
        if c in results.columns
    ]

    return {
        "count": int(len(results)),
        "items": results[cols].fillna("").to_dict(orient="records"),
    }

# -----------------------------------------------------------
# Optional redirect from /home → /docs
# -----------------------------------------------------------
@app.get("/home", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url="/docs")
