# api.py
from typing import Optional, Literal
import pandas as pd
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from core import load_data, search, DATA_DIR

app = FastAPI(title="Kiez Connect API")

# CORS for local dev + your production frontend (replace with your domain)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://hackathon-kiez-chatbot.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATAFRAME: Optional[pd.DataFrame] = None

@app.on_event("startup")
def _startup():
    global DATAFRAME
    DATAFRAME = load_data(DATA_DIR)

@app.get("/")
def root():
    return {
        "message": "✅ Kiez Connect API is running",
        "health": "/api/health",
        "docs": "/docs",
        "search": {
            "method": "POST",
            "path": "/api/search",
            "body_example": {
                "query": "jobs in Mitte python",
                "topic": "job",
                "district": "Mitte",
                "scope": "nearby",
                "radius_km": 3.0,
                "use_my_location": False,
                "origin_lat": 52.52,
                "origin_lon": 13.405,
                "limit": 25
            }
        }
    }

@app.get("/home", include_in_schema=False)
def to_docs():
    return RedirectResponse(url="/docs")

@app.get("/api/health")
def health():
    return {"status": "ok"}

class SearchIn(BaseModel):
    # backwards-compatible free text
    query: Optional[str] = None

    # new filters aligned with your Streamlit logic
    topic: Optional[Literal["job","event","course"]] = None
    district: Optional[str] = None
    scope: Optional[Literal["all","only","nearby"]] = "all"
    radius_km: float = 3.0
    use_my_location: bool = False
    origin_lat: Optional[float] = None
    origin_lon: Optional[float] = None
    keyword: Optional[str] = None

    # paging / sorting (optional)
    limit: int = 50
    offset: int = 0
    sort_by: Optional[str] = None
    sort_dir: Optional[Literal["asc","desc"]] = "asc"

@app.post("/api/search")
def api_search(body: SearchIn):
    if DATAFRAME is None or DATAFRAME.empty:
        raise HTTPException(status_code=500, detail="Data not loaded")

    results = search(
        DATAFRAME,
        query=body.query,
        topic=body.topic,
        district=body.district,
        scope=body.scope,
        radius_km=body.radius_km,
        use_my_location=body.use_my_location,
        origin_lat=body.origin_lat,
        origin_lon=body.origin_lon,
        keyword=body.keyword,
        sort_by=body.sort_by,
        sort_dir=body.sort_dir,
    )

    total = len(results)
    if body.offset:
        results = results.iloc[body.offset:]
    if body.limit:
        results = results.head(body.limit)

    cols = [
        c for c in [
            "type","title","course_name","provider","company",
            "district","location","address",
            "latitude","longitude",
            "date","start_date","end_date","when","time","start_time",
            "price","duration","level",
            "job_url_direct","job_url","link","url","website","registration","appointment_url","booking_url"
        ] if c in results.columns
    ]

    # include an "id" so frontend can request details later if needed
    payload = results[cols].fillna("").copy()
    payload.insert(0, "id", list(results.index))

    return {
        "total": int(total),
        "count": int(len(payload)),
        "items": payload.to_dict(orient="records")
    }
