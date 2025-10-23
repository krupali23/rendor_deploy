from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from core import load_data, search, DATA_DIR

app = FastAPI(title="Kiez Connect API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://your-react-domain.com",   # update to your real frontend domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATAFRAME: pd.DataFrame | None = None

@app.on_event("startup")
def _startup():
    global DATAFRAME
    DATAFRAME = load_data(DATA_DIR)

class SearchIn(BaseModel):
    query: str
    limit: int | None = 50

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.post("/api/search")
def api_search(body: SearchIn):
    if DATAFRAME is None or DATAFRAME.empty:
        raise HTTPException(status_code=500, detail="Data not loaded")
    results = search(DATAFRAME, body.query)
    if body.limit:
        results = results.head(body.limit)
    cols = [c for c in ["type","title","course_name","provider","company","district","location",
                        "address","latitude","longitude","job_url_direct","job_url","link","url","website"]
            if c in results.columns]
    return {"count": int(len(results)),
            "items": results[cols].fillna("").to_dict(orient="records")}
